#!/usr/bin/env python3
"""Package a skill folder into skill.zip with lightweight validation."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

MAX_BYTES = 25 * 1024 * 1024
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".zip"}


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with yaml frontmatter")
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data


def validate_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise ValueError("SKILL.md not found")
    meta = read_frontmatter(skill_md)
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("frontmatter name must be lowercase hyphen-case")
    if len(description.split()) < 12:
        raise ValueError("frontmatter description is too short")
    if any(part in description for part in "<>"):
        raise ValueError("frontmatter description cannot contain angle brackets")


def iter_package_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(skill_dir)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def package(skill_dir: Path, output_dir: Path) -> Path:
    validate_skill(skill_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "skill.zip"
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in iter_package_files(skill_dir):
            zf.write(path, path.relative_to(skill_dir.parent))
    size = out.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"skill.zip exceeds 25 mb limit: {size} bytes")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill folder as skill.zip")
    parser.add_argument("skill_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    try:
        out = package(Path(args.skill_dir).resolve(), Path(args.output_dir).resolve())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
