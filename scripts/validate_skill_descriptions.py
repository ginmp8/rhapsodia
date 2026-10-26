#!/usr/bin/env python3
"""Validate every canonical skill's ChatGPT-compatible frontmatter description."""
from __future__ import annotations
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 500
KEY = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:[ 	]*(.*))?$")

def parse_description(content: str) -> str:
    lines = content.replace("\r\n", "\n").lstrip("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing YAML frontmatter") from exc
    front = lines[1:end]
    fields = [i for i, line in enumerate(front) if not line.startswith((" ", "\t")) and KEY.match(line) and KEY.match(line).group(1) == "description"]
    if len(fields) != 1:
        raise ValueError(f"expected one description field, found {len(fields)}")
    index = fields[0]
    raw = KEY.match(front[index]).group(2) or ""
    if raw in {">", ">-", ">+", "|", "|-", "|+"}:
        block = []
        for line in front[index + 1:]:
            if line and not line[0].isspace():
                break
            if line.strip():
                block.append(line.strip())
            elif block:
                block.append("")
        value = (" " if raw.startswith(">") else "\n").join(block).strip()
    elif raw.startswith(("'", '"')):
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid double-quoted description: {exc}") from exc
        elif raw.endswith("'"):
            value = raw[1:-1].replace("''", "'")
        else:
            raise ValueError("unterminated single-quoted description")
    else:
        value = raw.split(" #", 1)[0]
    if not isinstance(value, str):
        raise ValueError("description must be text")
    value = value.strip()
    if not value:
        raise ValueError("description cannot be empty")
    if len(value) > LIMIT:
        raise ValueError(f"description has {len(value)} characters; maximum is {LIMIT}")
    return value

def check(root: Path) -> list[str]:
    failures = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        return ["no canonical skills found"]
    for skill in skills:
        try:
            parse_description(skill.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            failures.append(f"{skill.relative_to(root)}: {exc}")
    return failures

if __name__ == "__main__":
    import sys
    errors = check(ROOT)
    for issue in errors:
        print(issue, file=sys.stderr)
    print(f"skill description check: {'PASS' if not errors else 'FAIL'}; limit={LIMIT}; skills={len(list((ROOT / 'skills').glob('*/SKILL.md')))}")
    raise SystemExit(bool(errors))
