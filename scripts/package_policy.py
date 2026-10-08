"""Shared release policy: source files only, never local runtime state or secrets."""
from __future__ import annotations
import os
from pathlib import Path

EXCLUDED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.tox', '.venv', 'venv', 'dist', 'build', '.artifacts', '.rhapsodia'}
EXCLUDED_NAMES = {'.ds_store'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo', '.zip'}


def excluded_name(name: str) -> bool:
    name = name.casefold()
    return (name in EXCLUDED_DIRS or name in EXCLUDED_NAMES or Path(name).suffix.lower() in EXCLUDED_SUFFIXES
            or name == '.env' or (name.startswith('.env.') and name not in {'.env.example', '.env.sample', '.env.template'}))


def include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return not any(excluded_name(part) for part in relative.parts) and path.is_file() and not path.is_symlink()


def files(root: Path):
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if not excluded_name(name) and not (Path(directory) / name).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if include(path, root):
                yield path


def copy_ignore(directory: str, names: list[str]) -> list[str]:
    skipped = [name for name in names if excluded_name(name)]
    for name in names:
        if name not in skipped and (Path(directory) / name).is_symlink():
            raise ValueError('portable source tree contains a symbolic link; review it before packaging')
    return skipped
