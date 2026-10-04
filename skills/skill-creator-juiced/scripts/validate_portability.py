#!/usr/bin/env python3
"""Validate structural portability across Agent Skills semantic profiles and distribution surfaces."""
from __future__ import annotations

import argparse
import ast
import json
import sys
sys.dont_write_bytecode = True
from pathlib import Path

from skill_spec import parse_frontmatter, read_text, validate_agent_skill

KNOWN_HOSTS = {"portable-core", "openai", "codex", "claude", "copilot", "cursor"}
DEFAULT_HOSTS = ["portable-core", "openai", "codex", "claude", "copilot", "cursor"]
SURFACE_TO_PROFILE = {
    "chatgpt": "openai",
    "openai-api": "openai",
    "codex": "codex",
    "claude-code": "claude",
    "claude-ai-api": "claude",
    "copilot-github": "copilot",
    "copilot-vscode": "copilot",
    "copilot-visual-studio": "copilot",
    "cursor": "cursor",
}
DEFAULT_SURFACES = list(SURFACE_TO_PROFILE)
CURSOR_FRONTMATTER = {"paths", "disable-model-invocation", "icon", "color"}
CLAUDE_CODE_FRONTMATTER = {"argument-hint", "user-invocable", "model", "context", "agent", "hooks"}
HOST_EXTENSION_KEYS = CURSOR_FRONTMATTER | CLAUDE_CODE_FRONTMATTER
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
        requested = list(DEFAULT_HOSTS)
    if "portable-core" not in requested:
        requested.insert(0, "portable-core")
    unknown = sorted(set(requested) - KNOWN_HOSTS)
    if unknown:
        raise ValueError(f"unknown host profile(s): {', '.join(unknown)}")
    return list(dict.fromkeys(requested))


def normalize_surfaces(raw: str | None) -> list[str]:
    if raw is None:
        return []
    requested = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not requested:
        return []
    if "all" in requested:
        requested = list(DEFAULT_SURFACES)
    unknown = sorted(set(requested) - set(SURFACE_TO_PROFILE))
    if unknown:
        raise ValueError(f"unknown distribution surface(s): {', '.join(unknown)}")
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


def validate_portability(target: Path, hosts: list[str], surfaces: list[str] | None = None) -> dict:
    target = target.resolve()
    requested_hosts = list(dict.fromkeys(hosts))
    requested_surfaces = list(dict.fromkeys(surfaces or []))
    mapped_profiles = [SURFACE_TO_PROFILE[surface] for surface in requested_surfaces]
    resolved_hosts = list(dict.fromkeys([*requested_hosts, *mapped_profiles]))
    if "portable-core" not in resolved_hosts:
        resolved_hosts.insert(0, "portable-core")

    portable = validate_agent_skill(target, "portable")
    findings: list[dict] = []
    for error in portable.get("errors", []):
        findings.append({"code": "PORTABLE_CORE", "severity": "error", "evidence": error, "reason": "portable core validation failed"})
    findings.extend(scan_host_private_core(target))
    findings.extend(scan_python_dependencies(target))

    fm = frontmatter(target) if (target / "SKILL.md").exists() else {}
    keys = set(fm)
    for key in sorted(keys & HOST_EXTENSION_KEYS):
        findings.append({
            "code": "HOST_EXTENSION_IN_CORE",
            "severity": "error",
            "evidence": key,
            "reason": "host-specific frontmatter must live in an optional adapter rather than portable-core SKILL.md",
        })

    core_errors = [f for f in findings if f["severity"] == "error"]
    host_results: dict[str, dict] = {
        "portable-core": {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}
    }

    if "openai" in resolved_hosts:
        adapter, adapter_findings = validate_openai_adapter(target)
        findings.extend(adapter_findings)
        errors = [f for f in adapter_findings if f["severity"] == "error"]
        host_results["openai"] = {"status": "fail" if core_errors or errors else "pass", "evidence_level": "structural", "adapter": adapter}
    if "codex" in resolved_hosts:
        host_results["codex"] = {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}
    if "claude" in resolved_hosts:
        claude_findings = []
        name_tokens = str(fm.get("name", "")).split("-")
        for token in sorted({t for t in name_tokens if t in {"anthropic", "claude"}}):
            item = {"code": "CLAUDE_RESERVED_NAME", "severity": "error", "evidence": token, "reason": "Claude custom skills reserve anthropic/claude in names"}
            findings.append(item)
            claude_findings.append(item)
        host_results["claude"] = {"status": "fail" if core_errors or claude_findings else "pass", "evidence_level": "structural", "adapter": "none-required"}
    if "copilot" in resolved_hosts:
        host_results["copilot"] = {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}
    if "cursor" in resolved_hosts:
        host_results["cursor"] = {"status": "fail" if core_errors else "pass", "evidence_level": "structural", "adapter": "none-required"}

    surface_results: dict[str, dict] = {}
    for surface in requested_surfaces:
        profile = SURFACE_TO_PROFILE[surface]
        profile_result = host_results.get(profile, {"status": "not-run"})
        surface_results[surface] = {
            "status": profile_result["status"],
            "semantic_profile": profile,
            "evidence_level": "structural-mapping",
            "runtime_verified": False,
        }

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    status = "fail" if errors or any(r["status"] == "fail" for r in host_results.values()) or any(r["status"] == "fail" for r in surface_results.values()) else "pass"
    return {
        "status": status,
        "requested_hosts": requested_hosts,
        "resolved_hosts": resolved_hosts,
        "requested_surfaces": requested_surfaces,
        "portable_core": host_results["portable-core"]["status"] == "pass",
        "host_results": host_results,
        "surface_results": surface_results,
        "runtime_verified": False,
        "runtime_note": "structural portability and surface-to-profile mapping only; runtime/behavioral compatibility requires execution evidence on each material surface",
        "errors": errors,
        "warnings": warnings,
        "portable_profile": portable,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills portability across semantic profiles and distribution surfaces.")
    parser.add_argument("target", help="Path to a skill directory")
    parser.add_argument("--hosts", default="portable-core", help="Comma-separated semantic profiles: portable-core,openai,codex,claude,copilot,cursor,all")
    parser.add_argument("--surfaces", default="", help="Comma-separated distribution/client surfaces or all")
    parser.add_argument("--profile", choices=["portable", "openai"], help="Legacy compatibility option; portable maps to portable-core, openai maps to portable-core,openai")
    parser.add_argument("--json", dest="json_path", help="Optional JSON output path")
    args = parser.parse_args()
    raw_hosts = args.hosts
    if args.profile:
        raw_hosts = "portable-core" if args.profile == "portable" else "portable-core,openai"
    try:
        report = validate_portability(Path(args.target), normalize_hosts(raw_hosts), normalize_surfaces(args.surfaces))
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
