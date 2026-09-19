#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_inside(root: Path, relative: str) -> Path:
    base = root.resolve()
    path = (root / relative).resolve()
    if path != base and base not in path.parents:
        raise ValueError(f"path escapes evaluator root: {relative}")
    if not path.is_file():
        raise ValueError(f"evaluator file not found: {relative}")
    return path


def build_manifest(root: Path, paths: list[str]) -> dict:
    files = []
    for relative in sorted(set(paths)):
        path = _resolve_inside(root, relative)
        files.append({"path": relative, "size": path.stat().st_size, "sha256": _hash(path)})
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "manifest_version": 1,
        "files": files,
        "evaluator_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def verify_manifest(root: Path, manifest: dict) -> dict:
    current = build_manifest(root, [entry["path"] for entry in manifest.get("files", [])])
    expected = manifest.get("evaluator_sha256")
    status = "pass" if expected and current["evaluator_sha256"] == expected else "fail"
    return {
        "status": status,
        "expected_evaluator_sha256": expected,
        "actual_evaluator_sha256": current["evaluator_sha256"],
        "files": current["files"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze or verify activation evaluator assets by SHA-256.")
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--root", required=True)
    freeze.add_argument("--path", action="append", required=True)
    freeze.add_argument("--out", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--root", required=True)
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--json")
    args = parser.parse_args()

    root = Path(args.root)
    if args.command == "freeze":
        manifest = build_manifest(root, args.path)
        payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        Path(args.out).write_text(payload, encoding="utf-8")
        print(payload, end="")
        return 0

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    report = verify_manifest(root, manifest)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        Path(getattr(args, "json")).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
