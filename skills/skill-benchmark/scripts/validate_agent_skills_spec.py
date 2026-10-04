#!/usr/bin/env python3
"""Validate normative Agent Skills package constraints without third-party dependencies."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from _common import dump_json, extract_local_refs, parse_frontmatter

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KNOWN_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
YAML_NON_STRING = re.compile(r"^(?:true|false|null|~|[-+]?\d+(?:\.\d+)?)$", re.I)


def _frontmatter_block(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return [], ["SKILL.md missing opening frontmatter fence"]
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return [], ["SKILL.md missing closing frontmatter fence"]
    return normalized[4:end].splitlines(), errors


def _top_level_keys(lines: list[str]) -> set[str]:
    keys: set[str] = set()
    for line in lines:
        if line and not line[:1].isspace() and ":" in line:
            keys.add(line.split(":", 1)[0].strip())
    return keys


def _metadata_entries(lines: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    entries: list[tuple[str, str]] = []
    errors: list[str] = []
    in_metadata = False
    base_indent: int | None = None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[:1].isspace():
            key, _, value = line.partition(":")
            in_metadata = key.strip() == "metadata"
            base_indent = None
            if in_metadata and value.strip() not in {"", "{}"}:
                errors.append("metadata must be a YAML mapping, not an inline scalar")
            continue
        if not in_metadata:
            continue
        indent = len(line) - len(line.lstrip())
        if base_indent is None:
            base_indent = indent
        if indent < base_indent:
            in_metadata = False
            continue
        stripped = line.strip()
        if ":" not in stripped:
            errors.append(f"metadata entry is not key:value: {stripped}")
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        raw = value.strip()
        if not key or not raw:
            errors.append("metadata keys and values must be non-empty strings")
            continue
        if raw[0:1] in {"'", '"'} and raw[-1:] == raw[0:1]:
            raw = raw[1:-1]
        elif YAML_NON_STRING.fullmatch(raw):
            errors.append(f"metadata value for {key!r} must be a string; quote YAML scalar values that parse as non-strings")
            continue
        entries.append((key, raw))
    return entries, errors


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}
    if not root.is_dir():
        return {"status": "fail", "errors": [f"target is not a directory: {root}"], "warnings": [], "checks": {}}
    skill_files = [p for p in root.rglob("SKILL.md") if p.is_file()]
    if skill_files != [root / "SKILL.md"]:
        errors.append(f"target must contain exactly one root SKILL.md, found {len(skill_files)}")
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return {"status": "fail", "errors": errors or ["root SKILL.md is missing"], "warnings": warnings, "checks": checks}

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    lines, block_errors = _frontmatter_block(text)
    errors.extend(block_errors)
    fm, parse_errors = parse_frontmatter(skill_md)
    errors.extend(parse_errors)
    keys = _top_level_keys(lines)

    name = fm.get("name", "")
    description = fm.get("description", "")
    compatibility = fm.get("compatibility")
    if not name:
        errors.append("frontmatter.name is required")
    elif not NAME_RE.fullmatch(name):
        errors.append("frontmatter.name must use lowercase letters/numbers separated by single hyphens")
    elif len(name) > 64:
        errors.append("frontmatter.name must be at most 64 characters")
    if name and root.name != name:
        errors.append(f"frontmatter.name must match parent directory name: {root.name}")
    if not description:
        errors.append("frontmatter.description is required and must be non-empty")
    elif len(description) > 1024:
        errors.append("frontmatter.description must be at most 1024 characters")
    if compatibility is not None and not (1 <= len(compatibility) <= 500):
        errors.append("frontmatter.compatibility must be 1..500 characters when present")
    unknown = sorted(keys - KNOWN_FIELDS)
    if unknown:
        warnings.append("unknown top-level frontmatter fields may not be portable: " + ", ".join(unknown))

    metadata, metadata_errors = _metadata_entries(lines)
    errors.extend(metadata_errors)

    refs = extract_local_refs(text)
    missing: list[str] = []
    unsafe: list[str] = []
    for ref in refs:
        p = Path(ref)
        if p.is_absolute() or ".." in p.parts:
            unsafe.append(ref)
        elif not (root / p).exists():
            missing.append(ref)
    if unsafe:
        errors.append("unsafe local references: " + ", ".join(sorted(unsafe)))
    if missing:
        errors.append("missing local references: " + ", ".join(sorted(missing)))

    body_lines = text.splitlines()
    if len(body_lines) > 500:
        warnings.append("SKILL.md exceeds the specification's recommended 500-line progressive-disclosure threshold")

    checks.update({
        "root_skill_md": skill_md.is_file(),
        "name": name,
        "name_matches_parent": bool(name and name == root.name),
        "description_chars": len(description),
        "compatibility_chars": len(compatibility) if compatibility is not None else None,
        "metadata_entry_count": len(metadata),
        "local_reference_count": len(refs),
        "skill_md_lines": len(body_lines),
    })
    status = "fail" if errors else ("warn" if warnings else "pass")
    return {"status": status, "errors": errors, "warnings": warnings, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        report = validate(Path(args.target))
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)], "warnings": [], "checks": {}}
    dump_json(report, args.json_output)
    if args.json_output:
        dump_json(report)
    return 1 if report.get("status") == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
