#!/usr/bin/env python3
"""Validate and package a skill folder as skill.zip.

This self-contained helper is for maintaining this skill package. It is not a
replacement for documentation review, hardening, or benchmark workflows.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

MAX_ZIP_BYTES = 25 * 1024 * 1024
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    _, yaml_part, _ = text.split("---", 2)
    data: dict[str, str] = {}
    for line in yaml_part.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data


def validate_skill_folder(skill_path: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md is missing"]
    frontmatter = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if set(frontmatter) != {"name", "description"}:
        errors.append("frontmatter must contain only name and description")
    if not frontmatter.get("name"):
        errors.append("frontmatter name is empty")
    if not frontmatter.get("description"):
        errors.append("frontmatter description is empty")
    if frontmatter.get("name", "") != frontmatter.get("name", "").lower():
        errors.append("frontmatter name must be lowercase")
    if frontmatter.get("description", "") != frontmatter.get("description", "").lower():
        errors.append("frontmatter description must be lowercase")
    return errors


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.name == "skill.zip":
        return False
    return True


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    errors = validate_skill_folder(skill_path)
    if errors:
        raise ValueError("; ".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "skill.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(skill_path.rglob("*")):
            if file_path.is_file() and should_include(file_path):
                archive.write(file_path, file_path.relative_to(skill_path.parent))
    size = zip_path.stat().st_size
    if size > MAX_ZIP_BYTES:
        raise ValueError(f"skill.zip exceeds 25 MiB upload limit: {size} bytes")
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package a skill folder as skill.zip")
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument("output_dir", nargs="?", default=".", help="Directory where skill.zip will be written")
    args = parser.parse_args()
    skill_path = Path(args.skill_path).resolve()
    if not skill_path.is_dir():
        print(f"target is not a directory: {skill_path}", file=sys.stderr)
        return 2
    try:
        zip_path = package_skill(skill_path, Path(args.output_dir).resolve())
    except Exception as exc:
        print(f"package failed: {exc}", file=sys.stderr)
        return 1
    print(str(zip_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
