#!/usr/bin/env python3
"""Validate structural portability across Agent Skills-compatible hosts."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

from validate_skill_booster import find_skill_roots, parse_frontmatter, read_text, validate as validate_structure

KNOWN_HOSTS = {"portable-core", "openai", "claude", "copilot", "cursor"}
HOST_PRIVATE_TOKENS = {
    "skills__read": "OpenAI/ChatGPT private skill tool name",
    "tools.skills__": "OpenAI/ChatGPT private skill tool namespace",
    "functions.exec": "OpenAI/ChatGPT private orchestration tool name",
    "python_user_visible": "OpenAI/ChatGPT private execution tool name",
    "container.exec": "OpenAI/ChatGPT private execution tool name",
    "/home/oai/": "OpenAI sandbox-specific filesystem path",
    "sandbox:/mnt/data": "OpenAI sandbox-specific artifact path",
}
HOST_PATH_TOKENS = [".claude/skills", ".cursor/skills", ".github/skills", ".copilot/skills", ".codex/skills", ".agents/skills"]
STANDARD_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CURSOR_FRONTMATTER = {"paths", "disable-model-invocation", "icon", "color"}


def normalize_hosts(raw: str) -> list[str]:
    requested = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not requested:
        requested = ["portable-core"]
    if "all" in requested:
        requested = ["portable-core", "openai", "claude", "copilot", "cursor"]
    if "portable-core" not in requested:
        requested.insert(0, "portable-core")
    unknown = sorted(set(requested) - KNOWN_HOSTS)
    if unknown:
        raise ValueError(f"unknown host profile(s): {', '.join(unknown)}")
    return list(dict.fromkeys(requested))


def extract_top_level_keys(skill_md: Path) -> set[str]:
    text = read_text(skill_md).replace("\r\n", "\n")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not match:
        return set()
    keys: set[str] = set()
    for line in match.group(1).splitlines():
        if line and not line[:1].isspace():
            m = re.match(r"^([A-Za-z0-9_-]+):", line)
            if m:
                keys.add(m.group(1))
    return keys


def scan_host_private_core(root: Path, skill_md: Path) -> list[dict]:
    findings: list[dict] = []
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root).as_posix()
        if rel == "references/host-compatibility.md":
            continue
        text = read_text(md)
        for token, reason in HOST_PRIVATE_TOKENS.items():
            if token in text:
                findings.append({"code": "HOST_PRIVATE_CORE", "severity": "error", "evidence": f"{rel}: {token}", "reason": reason})
    skill_text = read_text(skill_md)
    for token in HOST_PATH_TOKENS:
        if token in skill_text:
            findings.append({
                "code": "HOST_INSTALL_PATH_IN_CORE",
                "severity": "warning",
                "evidence": token,
                "reason": "installation paths belong in the host-compatibility reference, not core workflow logic",
            })
    return findings


def validate_openai_adapter(root: Path) -> tuple[str, list[dict]]:
    adapter = root / "agents" / "openai.yaml"
    if not adapter.exists():
        return "not-present", []
    text = read_text(adapter)
    findings: list[dict] = []
    for required in ["interface:", "display_name:", "short_description:"]:
        if required not in text:
            findings.append({"code": "OPENAI_ADAPTER_FIELD", "severity": "error", "evidence": required, "reason": "OpenAI adapter is present but incomplete"})
    for obsolete in ["products:", "  icon:", "  color:"]:
        if obsolete in text:
            findings.append({"code": "OPENAI_ADAPTER_LEGACY_FIELD", "severity": "warning", "evidence": obsolete.strip(), "reason": "prefer current documented agents/openai.yaml fields"})
    return ("pass" if not any(f["severity"] == "error" for f in findings) else "fail"), findings


def scan_python_dependencies(root: Path) -> list[dict]:
    findings: list[dict] = []
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    for script in sorted((root / "scripts").glob("*.py")) if (root / "scripts").exists() else []:
        try:
            tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            findings.append({"code": "PYTHON_SYNTAX", "severity": "error", "evidence": f"{script.name}:{exc.lineno}", "reason": exc.msg})
            continue
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        if stdlib:
            external = sorted(name for name in imports if name not in stdlib and name != "validate_skill_booster")
            for name in external:
                findings.append({"code": "PYTHON_EXTERNAL_DEPENDENCY", "severity": "warning", "evidence": f"{script.name}: {name}", "reason": "external Python dependency may not exist on every host"})
    return findings


def validate(root: Path, hosts: list[str]) -> dict:
    root = root.resolve()
    structural = validate_structure(root)
    findings: list[dict] = []
    if structural.get("status") != "pass":
        findings.extend({"code": "STRUCTURE", "severity": "error", "evidence": msg, "reason": "structural validation failed"} for msg in structural.get("errors", []))

    skill_roots = find_skill_roots(root) if root.exists() else []
    fm: dict[str, str] = {}
    keys: set[str] = set()
    if len(skill_roots) == 1:
        skill_md = skill_roots[0]
        fm, _ = parse_frontmatter(skill_md)
        keys = extract_top_level_keys(skill_md)
        findings.extend(scan_host_private_core(root, skill_md))
        extra = sorted(keys - STANDARD_FRONTMATTER - CURSOR_FRONTMATTER)
        for key in extra:
            findings.append({"code": "UNKNOWN_FRONTMATTER", "severity": "warning", "evidence": key, "reason": "unknown top-level frontmatter may not be interpreted consistently across hosts"})
        cursor_only = sorted(keys & CURSOR_FRONTMATTER)
        if cursor_only and any(host != "cursor" for host in hosts if host != "portable-core"):
            for key in cursor_only:
                findings.append({"code": "CURSOR_FRONTMATTER_IN_PORTABLE_CORE", "severity": "warning", "evidence": key, "reason": "Cursor-specific frontmatter should not be required for cross-host behavior"})
        if "allowed-tools" in keys and len(hosts) > 2:
            findings.append({"code": "EXPERIMENTAL_ALLOWED_TOOLS", "severity": "warning", "evidence": "allowed-tools", "reason": "open Agent Skills marks this field experimental and host support varies"})

    host_results: dict[str, dict] = {}
    core_errors = [f for f in findings if f["severity"] == "error"]
    host_results["portable-core"] = {"status": "fail" if core_errors else "pass", "adapter": "none-required"}

    if "claude" in hosts:
        claude_findings: list[dict] = []
        name_tokens = str(fm.get("name", "")).split("-")
        reserved = sorted({token for token in name_tokens if token in {"anthropic", "claude"}})
        for token in reserved:
            item = {"code": "CLAUDE_RESERVED_NAME", "severity": "error", "evidence": token, "reason": "Claude custom skills reserve anthropic/claude in names"}
            findings.append(item)
            claude_findings.append(item)
        host_results["claude"] = {"status": "fail" if claude_findings or core_errors else "pass", "adapter": "none-required"}

    if "openai" in hosts:
        adapter_status, adapter_findings = validate_openai_adapter(root)
        findings.extend(adapter_findings)
        errors = [f for f in adapter_findings if f["severity"] == "error"]
        host_results["openai"] = {"status": "fail" if errors or core_errors else "pass", "adapter": adapter_status}

    if "copilot" in hosts:
        host_results["copilot"] = {"status": "fail" if core_errors else "pass", "adapter": "none-required"}

    if "cursor" in hosts:
        host_results["cursor"] = {"status": "fail" if core_errors else "pass", "adapter": "none-required"}

    findings.extend(scan_python_dependencies(root))
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    status = "fail" if errors or any(result["status"] == "fail" for result in host_results.values()) else "pass"
    return {
        "status": status,
        "requested_hosts": hosts,
        "portable_core": host_results.get("portable-core", {}).get("status") == "pass",
        "host_results": host_results,
        "runtime_verified": False,
        "runtime_note": "structural portability only; each host/runtime still needs execution evidence for behavioral or tool claims",
        "errors": errors,
        "warnings": warnings,
        "structural_validation": structural,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills portability across requested hosts.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--hosts", default="portable-core", help="Comma-separated: portable-core,openai,claude,copilot,cursor,all")
    parser.add_argument("--json", dest="json_output")
    args = parser.parse_args()
    try:
        hosts = normalize_hosts(args.hosts)
        report = validate(Path(args.target), hosts)
    except Exception as exc:
        report = {"status": "fail", "errors": [{"code": "PORTABILITY_EXCEPTION", "severity": "error", "evidence": str(exc), "reason": "validator exception"}], "warnings": []}
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json_output:
        Path(args.json_output).write_text(text + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
