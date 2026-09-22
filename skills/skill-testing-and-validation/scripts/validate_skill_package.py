#!/usr/bin/env python3
"""Validate structural invariants of an Agent Skills-compatible package.

Uses a real YAML parser when PyYAML is available and a conservative portable
fallback otherwise. The fallback rejects YAML constructs it cannot validate
safely instead of silently accepting malformed frontmatter.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOP_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
BLOCK_MARKERS = {"|", ">", "|-", ">-", "|+", ">+"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _decode_quoted(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        try:
            return str(ast.literal_eval(value))
        except Exception:
            return value[1:-1]
    return value


def _validate_plain_scalar(value: str) -> str | None:
    value = value.strip()
    if not value or value[0] in {"'", '"', "[", "{"}:
        return None
    if re.search(r":(?:[ \t]|$)", value):
        return "unquoted plain scalar contains a mapping separator ': '; quote it or use a block scalar"
    return None


def _portable_parse(raw: str) -> tuple[dict[str, Any], list[str]]:
    """Conservative parser for the frontmatter subset used by Agent Skills."""
    data: dict[str, Any] = {}
    errors: list[str] = []
    lines = raw.replace("\r\n", "\n").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[:1].isspace():
            errors.append(f"unexpected indented YAML line without a validated parent at line {i + 1}")
            i += 1
            continue
        match = TOP_KEY_RE.match(line)
        if not match:
            errors.append(f"invalid top-level YAML mapping line {i + 1}: {line}")
            i += 1
            continue
        key = match.group(1)
        value = (match.group(2) or "").strip()
        if value in BLOCK_MARKERS:
            folded = value.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1].isspace()):
                block.append(lines[i].lstrip())
                i += 1
            data[key] = (" " if folded else "\n").join(block).strip()
            continue
        if value == "":
            nested: dict[str, str] = {}
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1].isspace()):
                nested_line = lines[i]
                if not nested_line.strip() or nested_line.lstrip().startswith("#"):
                    i += 1
                    continue
                stripped = nested_line.lstrip()
                nested_match = TOP_KEY_RE.match(stripped)
                if not nested_match:
                    errors.append(f"invalid nested YAML mapping line {i + 1}: {nested_line}")
                    i += 1
                    continue
                nested_value = (nested_match.group(2) or "").strip()
                scalar_error = _validate_plain_scalar(nested_value)
                if scalar_error:
                    errors.append(f"invalid YAML for '{key}.{nested_match.group(1)}': {scalar_error}")
                nested[nested_match.group(1)] = _decode_quoted(nested_value)
                i += 1
            data[key] = nested
            continue
        scalar_error = _validate_plain_scalar(value)
        if scalar_error:
            errors.append(f"invalid YAML for '{key}': {scalar_error}")
        if value.startswith(("'", '"')) and (len(value) < 2 or value[-1] != value[0]):
            errors.append(f"invalid YAML for '{key}': unterminated quoted scalar")
        data[key] = _decode_quoted(value)
        i += 1
    return data, errors


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, Any], list[str], str]:
    text = read_text(skill_md)
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, ["SKILL.md is missing YAML frontmatter delimited by ---"], "none"
    raw = match.group(1)

    fallback_data, fallback_errors = _portable_parse(raw)
    if fallback_errors:
        return fallback_data, fallback_errors, "portable-conservative"

    try:
        import yaml  # type: ignore
    except Exception:
        return fallback_data, [], "portable-conservative"

    try:
        parsed = yaml.safe_load(raw)
    except Exception as exc:
        return {}, [f"invalid YAML frontmatter: {exc}"], "pyyaml"
    if not isinstance(parsed, dict):
        return {}, ["frontmatter must parse to a YAML mapping"], "pyyaml"
    return parsed, [], "pyyaml"


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    parser = "none"
    data: dict[str, Any] = {}

    if not root.exists() or not root.is_dir():
        return {"status": "fail", "errors": [f"target is not a directory: {root}"], "warnings": [], "parser": parser}

    root_skill = root / "SKILL.md"
    nested = [p for p in root.rglob("SKILL.md") if p != root_skill and ".git" not in p.parts]
    if not root_skill.is_file():
        errors.append("root SKILL.md is missing")
    if nested:
        errors.append(f"nested SKILL.md files make the package root ambiguous: {len(nested)}")

    if root_skill.is_file():
        data, parse_errors, parser = parse_frontmatter(root_skill)
        errors.extend(parse_errors)
        name = str(data.get("name") or "").strip()
        description = str(data.get("description") or "").strip()
        if not name:
            errors.append("frontmatter.name is required")
        elif not NAME_RE.fullmatch(name):
            errors.append("frontmatter.name must be lowercase hyphen-case")
        elif name != root.name:
            errors.append(f"frontmatter.name must match package directory name: {root.name}")
        if not description:
            errors.append("frontmatter.description is required")
        elif len(description) > 1024:
            errors.append("frontmatter.description exceeds 1024 characters")

    return {
        "status": "pass" if not errors else "fail",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "parser": parser,
        "frontmatter": {k: data.get(k) for k in ("name", "description", "compatibility") if k in data},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Agent Skills package structure and YAML frontmatter.")
    ap.add_argument("target", nargs="?", default=".")
    ap.add_argument("--format", choices=("json", "text"), default="json")
    args = ap.parse_args()
    result = validate(Path(args.target))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"status={result['status']} parser={result['parser']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
