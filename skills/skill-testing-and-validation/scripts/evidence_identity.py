#!/usr/bin/env python3
"""Compute a deterministic identity for material target bytes.

Transient runtime/build evidence is excluded so executing a read-only gate does not
change the candidate identity merely because an interpreter created caches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".zip"}


def _excluded(root: Path, path: Path) -> bool:
    rel = path.relative_to(root)
    return any(part in EXCLUDE_DIRS for part in rel.parts) or (
        path.is_file() and path.suffix.lower() in EXCLUDE_SUFFIXES
    )


def material_files(root: Path) -> Iterable[Path]:
    root = root.resolve()
    if root.is_file():
        if root.suffix.lower() not in EXCLUDE_SUFFIXES:
            yield root
        return
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if _excluded(root, path):
            continue
        if path.is_file() or path.is_symlink():
            yield path


def tree_identity(target: Path) -> dict[str, Any]:
    root = target.resolve()
    digest = hashlib.sha256()
    count = 0
    if root.is_file():
        base = root.parent
    else:
        base = root
    for path in material_files(root):
        rel = path.relative_to(base).as_posix().encode("utf-8")
        if path.is_symlink():
            kind = b"L"
            payload = path.readlink().as_posix().encode("utf-8")
        else:
            kind = b"F"
            payload = path.read_bytes()
        file_hash = hashlib.sha256(payload).digest()
        digest.update(kind)
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(file_hash)
        count += 1
    return {
        "identity_version": 1,
        "algorithm": "sha256-material-tree-v1",
        "sha256": digest.hexdigest(),
        "file_count": count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hash material target bytes while ignoring transient runtime/build evidence.")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()
    result = tree_identity(Path(args.target))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
