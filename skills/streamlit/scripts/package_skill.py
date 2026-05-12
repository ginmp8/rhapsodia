#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "reports"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name.startswith(".") and path.name not in {".streamlit"}:
        return False
    return path.is_file()


def validate(root: Path) -> None:
    required = ["SKILL.md", "agents/openai.yaml", "scripts/validate_streamlit_skill.py"]
    for rel in required:
        if not (root / rel).exists():
            raise SystemExit(f"missing required file: {rel}")
    import subprocess
    result = subprocess.run(
        [os.environ.get("PYTHON", "python"), str(root / "scripts" / "validate_streamlit_skill.py"), str(root)],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stdout + result.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Package the Streamlit skill as skill.zip")
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    output = Path(args.output).resolve()
    if output.suffix != ".zip":
        output = output / "skill.zip"
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.validate:
        validate(root)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(root.rglob("*")):
            if should_include(file, root):
                zf.write(file, Path(root.name) / file.relative_to(root))

    print(f"wrote {output}")


if __name__ == "__main__":
    main()
