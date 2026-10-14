#!/usr/bin/env python3
"""Offline structure/Top-100/link/semantic-routing sanity gate for one portable skill."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

RELEASE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^\s\)]+)(?:\s+\"[^\"]*\")?\)")
MARKERS = ["## Mission and boundary", "## Mode routing", "## Execute", "## Non-negotiable invariants", "## Output and stop conditions", "## Direct resources and verification"]
REQUIRED_DIRECT = ["references/method.md", "references/evidence-and-bias.md", "references/output-contract.md", "references/activation.md", "references/portability.md", "references/research-basis.md"]
FORBIDDEN_HINTS = ["/home/oai", "container.exec", "functions.exec", "mcp__", "require a subagent", "CLAUDE_CODE", "cursor_only"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    entry = root / "SKILL.md"
    if not entry.is_file():
        return ["missing SKILL.md"]
    content = _read(entry)
    lines = content.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return ["invalid or missing YAML frontmatter"]
    end = lines.index("---", 1)
    header = lines[1:end]
    fields: dict[str, str] = {}
    for line in header:
        if ":" not in line:
            errors.append("malformed frontmatter line")
            continue
        key, val = line.split(":", 1)
        fields[key.strip()] = val.strip()
    if fields.get("name") != "premortem-analysis":
        errors.append("unexpected frontmatter name")
    if not fields.get("description") or len(fields["description"]) > 1024:
        errors.append("missing or excessively long description")
    if set(fields) - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}:
        errors.append("host-specific/nonportable frontmatter fields")
    desc = fields.get("description", "").lower()
    for phrase in ["failed", "plan", "before", "do not use", "incident"]:
        if phrase not in desc:
            errors.append(f"frontmatter missing routing signal {phrase!r}")
    top = "\n".join(lines[:100])
    if any(m not in top for m in MARKERS):
        errors.append("first 100 lines lack a required control-plane section")
    if not ("hypothetical" in top and "without" in top and "not-run" in top):
        errors.append("first 100 lines omit failure framing or uncertainty/limitation boundary")
    if any(word in content for word in FORBIDDEN_HINTS):
        errors.append("canonical SKILL.md includes a host-specific dependency")
    direct_links = {link.split("#", 1)[0] for link in LINK.findall(content)}
    for path in REQUIRED_DIRECT:
        if path not in direct_links:
            errors.append(f"required direct resource missing from SKILL.md: {path}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f"symlinks unsupported in portable archive: {relative}")
            continue
        if path.is_dir():
            if path.name in ("__pycache__", ".git", ".mypy_cache", ".pytest_cache"):
                errors.append(f"generated/protected directory: {relative}")
            continue
        if path.suffix in (".pyc", ".zip"):
            errors.append(f"generated/nested archive file: {relative}")
        if path.suffix != ".md":
            continue
        data = _read(path)
        for link in LINK.findall(data):
            target = link.split("#", 1)[0]
            if not target or re.match(r"(?i)^(https?://|mailto:)", target):
                continue
            if re.match(r"(?i)^(javascript:|file:|data:)", target):
                errors.append(f"unsafe Markdown URL: {relative} -> {target}")
                continue
            dest = (path.parent / target).resolve()
            if not dest.is_relative_to(root) or not dest.exists():
                errors.append(f"broken or escaping link: {relative} -> {target}")
        if path != entry and len(data.splitlines()) > 100:
            intro = "\n".join(data.splitlines()[:40]).lower()
            for tag in ("purpose", "load when", "decision impact", "contents"):
                if tag not in intro:
                    errors.append(f"long Markdown missing early semantic preview: {relative} ({tag})")
    ver = root / "VERSION"
    log = root / "CHANGELOG.md"
    if not ver.is_file() or not log.is_file():
        errors.append("VERSION or CHANGELOG.md missing")
    else:
        version = _read(ver).strip()
        if not RELEASE.fullmatch(version):
            errors.append("invalid SemVer VERSION")
        if len(re.findall(r"(?m)^## \[" + re.escape(version) + r"\](?:\s+-\s+\d{4}-\d{2}-\d{2})?\s*$", _read(log))) != 1:
            errors.append("CHANGELOG.md must have exactly one current-version heading")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    errors = validate_package(args.root)
    result: dict[str, Any] = {"status": "pass" if not errors else "fail", "errors": errors, "scope": "structural/top100/links/release"}
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(result["status"].upper(), "; ".join(errors) if errors else "portable skill package structure valid")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
