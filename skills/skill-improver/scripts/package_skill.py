#!/usr/bin/env python3
"""Validate and package a ChatGPT skill folder as a zip archive."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".skill-improver",
    ".hardening-work",
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "test-results.json",
    "skill-benchmark.md",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".zip",
}


def is_excluded(path: Path, root: Path, output_path: Path) -> bool:
    resolved = path.resolve()
    if resolved == output_path.resolve():
        return True
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
        return True
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if any(part.startswith("hardening-") for part in rel.parts):
        return True
    return False


def iter_package_files(root: Path, output_path: Path) -> list[Path]:
    files: list[Path] = []
    for candidate in sorted(root.rglob("*")):
        if not candidate.is_file():
            continue
        if is_excluded(candidate, root, output_path):
            continue
        files.append(candidate)
    return files


def run_validator(root: Path, validator: Path) -> dict:
    if not validator.exists():
        raise FileNotFoundError(f"validator not found: {validator}")
    completed = subprocess.run(
        [sys.executable, "-S", str(validator), "--target", str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("validator failed:\n" + completed.stdout)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"status": "pass", "raw_output": completed.stdout}


def validate_root(root: Path) -> None:
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"target is not a directory: {root}")
    skill_files = list(root.rglob("SKILL.md"))
    if len(skill_files) != 1:
        raise ValueError(f"expected exactly one SKILL.md, found {len(skill_files)}")


def package(root: Path, output_path: Path, files: list[Path]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = file_path.relative_to(root).as_posix()
            zf.write(file_path, arcname)
    os.replace(tmp_path, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package a ChatGPT skill folder.")
    parser.add_argument("--target", required=True, type=Path, help="Path to the skill folder.")
    parser.add_argument("--output", required=True, type=Path, help="Output zip path.")
    parser.add_argument(
        "--validator",
        type=Path,
        help="Validator script. Defaults to scripts/validate_skill_improver_package.py under the target.",
    )
    parser.add_argument("--no-validate", action="store_true", help="Skip validator execution.")
    args = parser.parse_args()

    root = args.target.resolve()
    output_path = args.output.resolve()
    validate_root(root)

    validator_result: dict | None = None
    if not args.no_validate:
        validator = args.validator.resolve() if args.validator else root / "scripts" / "validate_skill_improver_package.py"
        validator_result = run_validator(root, validator)

    files = iter_package_files(root, output_path)
    package(root, output_path, files)

    result = {
        "status": "pass",
        "target": str(root),
        "output": str(output_path),
        "files_packaged": len(files),
        "validator": validator_result,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
