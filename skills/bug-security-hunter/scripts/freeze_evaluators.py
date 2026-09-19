#!/usr/bin/env python3
"""Freeze or verify Bug Security Hunter evaluator assets by SHA-256."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_PATHS = [
    "evals/activation-scenarios.json",
    "evals/behavioral-scenarios.json",
    "evals/reproducibility-scenarios.json",
    "schemas/review-receipt.schema.json",
    "scripts/validate_review_receipt.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(root: Path, paths: list[str]) -> dict:
    entries = []
    for rel in sorted(paths):
        path = (root / rel).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise SystemExit(f"FAIL: evaluator path escapes root: {rel}") from exc
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"FAIL: evaluator file missing or unsafe: {rel}")
        entries.append({"path": rel, "sha256": sha256(path), "bytes": path.stat().st_size})
    return {"manifest_version": 1, "target": "bug-security-hunter", "files": entries}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--root", required=True)
    freeze.add_argument("--out", required=True)
    freeze.add_argument("--path", action="append", dest="paths")
    verify = sub.add_parser("verify")
    verify.add_argument("--root", required=True)
    verify.add_argument("--manifest", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.command == "freeze":
        paths = args.paths or DEFAULT_PATHS
        manifest = build_manifest(root, paths)
        out = Path(args.out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"PASS: froze {len(manifest['files'])} evaluator files to {out}")
        return 0

    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = [entry["path"] for entry in manifest.get("files", [])]
    current = build_manifest(root, paths)
    expected = {entry["path"]: entry for entry in manifest.get("files", [])}
    actual = {entry["path"]: entry for entry in current.get("files", [])}
    problems = []
    for rel in sorted(set(expected) | set(actual)):
        if rel not in expected:
            problems.append(f"unexpected evaluator: {rel}")
        elif rel not in actual:
            problems.append(f"missing evaluator: {rel}")
        elif expected[rel].get("sha256") != actual[rel].get("sha256"):
            problems.append(f"changed evaluator: {rel}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print(f"PASS: evaluator manifest verified ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
