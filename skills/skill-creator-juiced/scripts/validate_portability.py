#!/usr/bin/env python3
"""Validate structural portability across Agent Skills-compatible host profiles."""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
sys.dont_write_bytecode = True
from pathlib import Path

from skill_spec import parse_frontmatter, read_text, validate_agent_skill

KNOWN_HOSTS = {"portable-core", "openai", "codex", "claude", "copilot", "cursor"}
CURSOR_FRONTMATTER = {"paths", "disable-model-invocation", "icon", "color"}
HOST_PRIVATE_TOKENS = {
    "skills__read": "OpenAI/ChatGPT private skill tool name",
    "tools.skills__": "OpenAI/ChatGPT private skill tool namespace",
    "functions.exec": "OpenAI/ChatGPT private orchestration tool name",
    "python_user_visible": "OpenAI/ChatGPT private execution tool name",
    "container.exec": "OpenAI/ChatGPT private execution tool name",
    "/home/oai/": "OpenAI sandbox-specific filesystem path",
    "sandbox:/mnt/data": "OpenAI sandbox-specific artifact path",
    "/mnt/data/": "OpenAI sandbox-specific filesystem path",
}


def normalize_hosts(raw: str) -> list[str]:
    requested = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not requested:
        requested = ["portable-core"]
    if "all" in requested:
        requested = ["portable-core", "openai", "codex", "claude", "copilot", "cursor"]
    if "portable-core" not in requested:
        requested.insert(0, "portable-core")
    unknown = sorted(set(requested) - KNOWN_HOSTS)
    if unknown:
        raise ValueError(f"unknown host profile(s): {', '.join(unknown)}")
    return list(dict.fromkeys(requested))


def frontmatter(target: Path) -> dict:
    fm, error, _ = parse_frontmatter(read_text(target / "SKILL.md"))
    if error or not isinstance(fm, dict):
        return {}
    return fm


def scan_host_private_core(target: Path) -> list[dict]:
    findings: list[dict] = []
    skip = {"references/host-portability.md"}
    for md in sorted(target.rglob("*.md")):
        rel = md.relative_to(target).as_posix()
        if rel in skip:
            continue
        text = read_text(md)
        for token, reason in HOST_PRIVATE_TOKENS.items():
            if token in text:
                findings.append({"code": "HOST_PRIVATE_CORE", "severity": "error", "evidence": f"{rel}: {token}", "reason": reason})
    return findings


def scan_python_dependencies(target: Path) -> list[dict]:
    findings: list[dict] = []
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    local_modules = {p.stem for p in (target / "scripts").glob("*.py")} if (target / "scripts").exists() else set()
    for script in sorted((target / "scripts").glob("*.py")) if (target / "scripts").exists() else []:
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
        for name in sorted(imports):
            if script.name == "skill_spec.py" and name == "yaml":
                # Optional PyYAML import has a bundled fallback parser.
                continue
            if stdlib and name not in stdlib and name not in local_modules:
                findings.append({"code": "PYTHON_EXTERNAL_DEPENDENCY", "severity": "warning", "evidence": f"{script.name}: {name}", "reason": "external Python dependency may not exist on every host"})
    return findings


def validate_openai_adapter(target: Path) -> tuple[str, list[dict]]:
    adapter = target / "agents" / "openai.yaml"
    if not adapter.exists():
        return "not-present", []
    text = read_text(adapter)
    findings = []
    for required in ["interface:", "display_name:", "short_description:"]:
        if required not in text:
            findings.append({"code": "OPENAI_ADAPTER_FIELD", "severity": "error", "evidence": required, "reason": "OpenAI adapter is present but incomplete"})
    return ("fail" if any(f["severity"] == "error" for f in findings) else "pass"), findings


def validate_portability(target: Path, hosts: list[str]) -> dict:
    target = target.resolve()
    portable = validate_agent_skill(target, "portable")
    findings: list[dict] = []
    for error in portable.get("errors", []):
        findings.append({"code": "PORTABLE_CORE", "severity": "error", "evidence": error, "reason": "portable core validation failed"})
    findings.extend(scan_host_private_core(target))
    findings.extend(scan_python_dependencies(target))

    fm = frontmatter(target) if (target / "SKILL.md").exists() else {}
    keys = set(fm)
    cursor_keys = sorted(keys & CURSOR_FRONTMATTER)
    if cursor_keys and any(h not in {"portable-core", "cursor"} for h in hosts):
        for key in cursor_keys:
            findings.append({"code": "CURSOR_FRONTMATTER_IN_CORE", "severity": "warning", "evidence": key, "reason": "Cursor-specific metadata should not be a cross-host correctness dependency"})

    core_errors = [f for f in findings if f["severity"] == "error"]
    host_results: dict[str, dict] = {
        "portable-core": {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}
    }

    if "openai" in hosts:
        adapter, adapter_findings = validate_openai_adapter(target)
        findings.extend(adapter_findings)
        errors = [f for f in adapter_findings if f["severity"] == "error"]
        host_results["openai"] = {"status": "fail" if core_errors or errors else "pass", "evidence_level": "structural", "adapter": adapter}
    if "codex" in hosts:
        host_results["codex"] = {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}
    if "claude" in hosts:
        claude_findings = []
        name_tokens = str(fm.get("name", "")).split("-")
        for token in sorted({t for t in name_tokens if t in {"anthropic", "claude"}}):
            item = {"code": "CLAUDE_RESERVED_NAME", "severity": "error", "evidence": token, "reason": "Claude custom skills reserve anthropic/claude in names"}
            findings.append(item)
            claude_findings.append(item)
        host_results["claude"] = {"status": "fail" if core_errors or claude_findings else "pass", "evidence_level": "structural", "adapter": "none-required"}
    if "copilot" in hosts:
        host_results["copilot"] = {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}
    if "cursor" in hosts:
        host_results["cursor"] = {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    status = "fail" if errors or any(r["status"] == "fail" for r in host_results.values()) else "pass"
    return {
        "status": status,
        "requested_hosts": hosts,
        "portable_core": host_results["portable-core"]["status"] == "pass",
        "host_results": host_results,
        "runtime_verified": False,
        "runtime_note": "structural portability only; runtime/behavioral compatibility requires execution evidence on each host",
        "errors": errors,
        "warnings": warnings,
        "portable_profile": portable,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills portability across requested host profiles.")
    parser.add_argument("target", help="Path to a skill directory")
    parser.add_argument("--hosts", default="portable-core", help="Comma-separated: portable-core,openai,codex,claude,copilot,cursor,all")
    parser.add_argument("--profile", choices=["portable", "openai"], help="Legacy compatibility option; portable maps to portable-core, openai maps to portable-core,openai")
    parser.add_argument("--json", dest="json_path", help="Optional JSON output path")
    args = parser.parse_args()
    raw_hosts = args.hosts
    if args.profile:
        raw_hosts = "portable-core" if args.profile == "portable" else "portable-core,openai"
    try:
        report = validate_portability(Path(args.target), normalize_hosts(raw_hosts))
    except Exception as exc:
        report = {"status": "fail", "errors": [{"code": "PORTABILITY_EXCEPTION", "severity": "error", "evidence": str(exc), "reason": "validator exception"}], "warnings": []}
    if args.json_path:
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
