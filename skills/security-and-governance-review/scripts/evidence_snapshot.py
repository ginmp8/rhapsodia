#!/usr/bin/env python3
"""Create a deterministic evidence/source identity receipt without exposing protected content."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from _security_common import EVIDENCE_RECEIPT_VERSION, protected_status, sha256_bytes, sha256_file

BLOCKED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".venv", "venv", "node_modules"}
DEPENDENCY_NAMES = {"requirements.txt", "pyproject.toml", "poetry.lock", "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.json", "gemfile", "gemfile.lock", "go.mod", "go.sum", "cargo.toml", "cargo.lock", "packages.lock.json", "directory.packages.props"}


def records(target: Path) -> list[dict]:
    out: list[dict] = []
    root = target if target.is_dir() else target.parent
    candidates: list[Path] = []
    if target.is_file():
        candidates = [target]
    else:
        for current, dirs, files in os.walk(target, topdown=True, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in BLOCKED_DIRS)
            candidates.extend(Path(current, name) for name in sorted(files))
    for path in candidates:
        rel = path.relative_to(root).as_posix() if target.is_dir() else path.name
        if path.is_symlink():
            out.append({"path": rel, "status": "symlink-blocked", "role": "source"})
            continue
        status = protected_status(rel)
        try:
            size = path.stat().st_size
        except OSError:
            out.append({"path": rel, "status": "unreadable", "role": "source"})
            continue
        role = "dependency-source" if path.name.lower() in DEPENDENCY_NAMES else "source"
        if status == "protected-unread":
            out.append({"path": rel, "status": status, "role": role, "size": size})
        elif status == "protected-hash-only":
            out.append({"path": rel, "status": status, "role": role, "size": size, "sha256": sha256_file(path)})
        else:
            out.append({"path": rel, "status": "hashed", "role": role, "size": size, "sha256": sha256_file(path)})
    return sorted(out, key=lambda x: x["path"])


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a deterministic security review evidence receipt.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"target not found: {target}")
    files = records(target)
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload = {
        "receipt_version": EVIDENCE_RECEIPT_VERSION,
        "target_name": target.name,
        "tree_sha256": sha256_bytes(canonical),
        "files": files,
        "rules": {
            "protected-unread": "presence/metadata only; content is not read or hashed",
            "protected-hash-only": "content identity only; content is never emitted",
            "symlink-blocked": "link target is not traversed",
        },
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
