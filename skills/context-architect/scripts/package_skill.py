#!/usr/bin/env python3
"""Package the context-architect skill as skill.zip after structural validation."""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name.startswith(".") and path.name not in {".gitkeep"}:
        return False
    return path.is_file()


def validate_folder(root: Path) -> list[str]:
    errors: list[str] = []
    if not (root / "SKILL.md").exists():
        errors.append("missing SKILL.md")
    if not (root / "agents" / "openai.yaml").exists():
        errors.append("missing agents/openai.yaml")
    if len(list(root.rglob("SKILL.md"))) != 1:
        errors.append("package must contain exactly one SKILL.md")
    return errors


def package(root: Path, output: Path) -> Path:
    errors = validate_folder(root)
    if errors:
        raise SystemExit("folder validation failed: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.name != "skill.zip":
        output = output / "skill.zip" if output.suffix == "" else output.with_name("skill.zip")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if should_include(path, root):
                zf.write(path, path.relative_to(root).as_posix())
    size_mb = output.stat().st_size / (1024 * 1024)
    if size_mb > 25:
        raise SystemExit(f"package exceeds 25 MB: {size_mb:.2f} MB")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Package context-architect as skill.zip.")
    parser.add_argument("target", help="Skill folder to package.")
    parser.add_argument("output", nargs="?", default="skill.zip", help="Output zip path or directory.")
    args = parser.parse_args()
    root = Path(args.target).resolve()
    output = Path(args.output).resolve()
    result = package(root, output)
    print(f"wrote {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
