#!/usr/bin/env python3
"""Package the Streamlit skill as skill.zip after validation."""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDE_PARTS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return path.is_file()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.target).resolve()
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    validator = root / "scripts" / "validate_streamlit_skill.py"
    result = subprocess.run([sys.executable, str(validator), str(root)], text=True)
    if result.returncode != 0:
        return result.returncode

    if out.exists():
        out.unlink()

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if should_include(path, root):
                zf.write(path, Path(root.name) / path.relative_to(root))

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        if not any(name == f"{root.name}/SKILL.md" for name in names):
            print("FAIL: archive missing root SKILL.md")
            return 1
        bad = [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
        if bad:
            print("FAIL: archive contains generated files: " + ", ".join(bad))
            return 1

    print(f"PASS: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
