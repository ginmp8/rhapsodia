#!/usr/bin/env python3
"""Create one ZIP archive for each immediate subfolder of a directory."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}


def iter_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative_path = path.relative_to(folder)
        if any(part in EXCLUDED_DIRS for part in relative_path.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        files.append(path)
    return files


def zip_folder(folder: Path, output_dir: Path) -> tuple[Path, int]:
    output_path = output_dir / f"{folder.name}.zip"
    files = iter_files(folder)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative_path = path.relative_to(folder).as_posix()
            archive.write(path, f"{folder.name}/{relative_path}")
    return output_path, len(files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create one ZIP file for each immediate subfolder."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("skills"),
        help="Directory containing the folders to package.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for the generated ZIP files; defaults to the source directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the ZIP files that would be created without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output_dir = (args.output_dir or source).resolve()

    if not source.is_dir():
        print(f"source is not a directory: {source}", file=sys.stderr)
        return 2

    folders = sorted(
        path for path in source.iterdir() if path.is_dir() and not path.is_symlink()
    )
    if not folders:
        print(f"no immediate subfolders found in: {source}", file=sys.stderr)
        return 1

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    for folder in folders:
        output_path = output_dir / f"{folder.name}.zip"
        if args.dry_run:
            print(f"would create {output_path} ({len(iter_files(folder))} files)")
            continue
        output_path, file_count = zip_folder(folder, output_dir)
        print(f"created {output_path} ({file_count} files)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())