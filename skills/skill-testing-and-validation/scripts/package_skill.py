#!/usr/bin/env python3
"""Package a skill folder as skill.zip with conservative exclusions."""
from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".zip"}
MAX_BYTES = 25 * 1024 * 1024


def iter_package_files(root: Path):
    for path in root.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix not in EXCLUDE_SUFFIXES:
            yield path


def validate_root(root: Path) -> list[str]:
    errors = []
    if not (root / "SKILL.md").exists():
        errors.append("SKILL.md missing")
    if len(list(root.glob("SKILL.md"))) != 1:
        errors.append("expected exactly one root SKILL.md")
    return errors


def package(root: Path, output: Path) -> dict:
    root = root.resolve()
    output = output.resolve()
    errors = validate_root(root)
    if errors:
        return {"passed": False, "errors": errors, "output": str(output)}
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    files = list(iter_package_files(root))
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(root.parent))
    size = output.stat().st_size
    return {
        "passed": size <= MAX_BYTES,
        "errors": [] if size <= MAX_BYTES else ["archive exceeds 25 MiB upload limit"],
        "output": str(output),
        "size_bytes": size,
        "file_count": len(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill folder as skill.zip.")
    parser.add_argument("target", help="Skill folder")
    parser.add_argument("output", nargs="?", default="skill.zip", help="Output zip path")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()
    result = package(Path(args.target), Path(args.output))
    if args.report:
        Path(args.report).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
