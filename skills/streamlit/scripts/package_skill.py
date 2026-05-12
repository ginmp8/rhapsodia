#!/usr/bin/env python3
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDE_PARTS = {'__pycache__', '.git', '.pytest_cache', '.mypy_cache'}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo'}


def include(path: Path) -> bool:
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name == 'skill.zip':
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', default='.')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(args.target).resolve()
    out = Path(args.output).resolve()
    subprocess.check_call([sys.executable, str(root / 'scripts' / 'validate_streamlit_skill.py'), str(root)])
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob('*')):
            if path.is_file() and include(path.relative_to(root)):
                zf.write(path, Path(root.name) / path.relative_to(root))
    print(out)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
