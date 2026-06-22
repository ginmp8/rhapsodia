#!/usr/bin/env python3
"""Create and validate a deterministic skill.zip archive for bug-security-hunter."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

SKILL_NAME = "bug-security-hunter"
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".DS_Store", ".zip"}
REQUIRED_ARCHIVE_FILES = {
    f"{SKILL_NAME}/SKILL.md",
    f"{SKILL_NAME}/agents/openai.yaml",
    f"{SKILL_NAME}/evals/activation-scenarios.json",
    f"{SKILL_NAME}/scripts/validate_skill_package.py",
    f"{SKILL_NAME}/scripts/package_skill.py",
}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if path.is_symlink():
        return False
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.name in EXCLUDE_SUFFIXES or path.suffix in EXCLUDE_SUFFIXES:
        return False
    return path.is_file()


def validate_archive(output: Path) -> None:
    with zipfile.ZipFile(output, "r") as zf:
        names = zf.namelist()
    if not names:
        raise SystemExit("FAIL: archive is empty")
    top_levels = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
    if top_levels != {SKILL_NAME}:
        raise SystemExit(f"FAIL: archive must contain one top-level {SKILL_NAME}/ folder, got {sorted(top_levels)}")
    for name in names:
        pp = PurePosixPath(name)
        if name.startswith("/") or ".." in pp.parts:
            raise SystemExit(f"FAIL: unsafe archive member path: {name}")
        if any(part in EXCLUDE_PARTS for part in pp.parts) or pp.suffix in EXCLUDE_SUFFIXES:
            raise SystemExit(f"FAIL: excluded file leaked into archive: {name}")
    missing = sorted(REQUIRED_ARCHIVE_FILES - set(names))
    if missing:
        raise SystemExit("FAIL: archive missing required files: " + ", ".join(missing))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="skill folder")
    parser.add_argument("--output", required=True, help="output skill.zip path")
    parser.add_argument("--validate", action="store_true", help="run validate_skill_package.py first")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    output = Path(args.output).resolve()
    if args.validate:
        validator = target / "scripts" / "validate_skill_package.py"
        subprocess.run([sys.executable, str(validator), str(target)], check=True)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(target.rglob("*")):
            if should_include(path, target):
                arcname = f"{SKILL_NAME}/{path.relative_to(target).as_posix()}"
                info = zipfile.ZipInfo(arcname)
                info.date_time = (2026, 1, 1, 0, 0, 0)
                info.external_attr = 0o644 << 16
                zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)

    validate_archive(output)
    print(f"PASS: wrote and validated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
