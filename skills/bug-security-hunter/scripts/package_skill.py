#!/usr/bin/env python3
"""Create a deterministic skill.zip archive for bug-security-hunter."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".DS_Store"}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.name in EXCLUDE_SUFFIXES or path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.is_dir():
        return False
    return True


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
                info = zipfile.ZipInfo(str(path.relative_to(target)).replace(os.sep, "/"))
                info.date_time = (2026, 1, 1, 0, 0, 0)
                info.external_attr = 0o644 << 16
                zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)

    print(f"PASS: wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
