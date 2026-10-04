#!/usr/bin/env python3
"""Validate the host-neutral Agent Skills core against requested portability profiles."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from package_skill import extract_refs, find_symlinks, read_text, validate_frontmatter  # noqa: E402

PROFILES = {"portable-core", "openai", "codex", "claude", "copilot", "cursor"}
PRIVATE_PATH_PATTERNS = [
    re.compile(r"sandbox:/", re.IGNORECASE),
    re.compile(r"/mnt/data/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\"),
]


def _core_checks(target: Path) -> list[str]:
    errors: list[str] = []
    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        return ["root SKILL.md is missing"]
    text = read_text(skill_md)
    errors.extend(validate_frontmatter(text, root_name=target.name, profile="portable"))
    for ref in sorted(extract_refs(text)):
        candidate = target / ref
        if not candidate.exists():
            errors.append(f"referenced path missing: {ref}")
    for link in find_symlinks(target):
        errors.append(f"symlink is not portable/package-safe: {link}")
    for pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(text):
            errors.append(f"SKILL.md depends on host-private/absolute path pattern: {pattern.pattern}")
    return errors


def validate_portability(target: Path, profiles: list[str]) -> dict[str, Any]:
    target = Path(target).resolve()
    requested = []
    for profile in profiles:
        if profile not in PROFILES:
            raise ValueError(f"unsupported portability profile: {profile}")
        if profile not in requested:
            requested.append(profile)
    if "portable-core" not in requested:
        requested.insert(0, "portable-core")
    core_errors = _core_checks(target)
    rows: list[dict[str, Any]] = []
    for profile in requested:
        errors = list(core_errors)
        notes: list[str] = []
        if profile == "openai":
            adapter = target / "agents" / "openai.yaml"
            notes.append("agents/openai.yaml is optional adapter metadata" if adapter.exists() else "no OpenAI adapter; portable core remains sufficient")
        elif profile in {"codex", "claude", "copilot", "cursor"}:
            notes.append("profile uses the same portable semantic core; discovery/install location is host-owned")
        else:
            notes.append("open Agent Skills portable semantic core")
        rows.append({
            "profile": profile,
            "status": "pass" if not errors else "fail",
            "errors": errors,
            "notes": notes,
            "runtime_evidence": "not-run",
        })
    return {
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
        "target": str(target),
        "profiles": rows,
        "claim_layer": "structural-portability",
        "runtime_behavior": "not-proven",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate portable Agent Skills core and requested host profiles.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--hosts", default="portable-core,openai,codex,claude,copilot,cursor")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    profiles = [item.strip() for item in args.hosts.split(",") if item.strip()]
    try:
        result = validate_portability(Path(args.target), profiles)
    except ValueError as exc:
        result = {"status": "fail", "target": str(Path(args.target).resolve()), "errors": [str(exc)], "profiles": []}
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
