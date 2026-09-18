#!/usr/bin/env python3
"""Freeze or verify a skill candidate by content hash manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

BLOCKED_PARTS = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "build", "dist", "reports", "generated_evidence", "generated-evidence",
    "benchmark-results", "validation-reports",
}
BLOCKED_SUFFIXES = {".pyc", ".pyo"}
BLOCKED_FILENAMES = {"skill.zip"}


def should_exclude(rel: Path) -> bool:
    return bool(set(rel.parts) & BLOCKED_PARTS or rel.suffix in BLOCKED_SUFFIXES or rel.name in BLOCKED_FILENAMES)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(target: Path) -> dict:
    target = target.resolve()
    files: dict[str, str] = {}
    for path in sorted(target.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(target)
        if should_exclude(rel):
            continue
        files[rel.as_posix()] = file_hash(path)
    combined = hashlib.sha256()
    for rel, digest in files.items():
        combined.update(rel.encode("utf-8"))
        combined.update(b"\0")
        combined.update(digest.encode("ascii"))
        combined.update(b"\n")
    return {
        "manifest_version": 1,
        "target_name": target.name,
        "file_count": len(files),
        "candidate_sha256": combined.hexdigest(),
        "files": files,
    }


def freeze(target: Path, out: Path) -> dict:
    manifest = snapshot(target)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"status": "pass", "manifest": str(out), **{k: manifest[k] for k in ("file_count", "candidate_sha256")}}


def verify(target: Path, manifest_path: Path) -> dict:
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = snapshot(target)
    missing = sorted(set(expected.get("files", {})) - set(actual["files"]))
    added = sorted(set(actual["files"]) - set(expected.get("files", {})))
    changed = sorted(
        rel for rel in set(expected.get("files", {})) & set(actual["files"])
        if expected["files"].get(rel) != actual["files"].get(rel)
    )
    ok = not missing and not added and not changed and expected.get("candidate_sha256") == actual["candidate_sha256"]
    return {
        "status": "pass" if ok else "fail",
        "candidate_sha256": actual["candidate_sha256"],
        "expected_candidate_sha256": expected.get("candidate_sha256"),
        "missing": missing,
        "added": added,
        "changed": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze or verify a validated skill candidate.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_freeze = sub.add_parser("freeze")
    p_freeze.add_argument("--target", required=True)
    p_freeze.add_argument("--out", required=True)
    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--target", required=True)
    p_verify.add_argument("--manifest", required=True)
    args = parser.parse_args()

    try:
        report = freeze(Path(args.target), Path(args.out)) if args.command == "freeze" else verify(Path(args.target), Path(args.manifest))
    except Exception as exc:
        report = {"status": "fail", "error": str(exc)}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
