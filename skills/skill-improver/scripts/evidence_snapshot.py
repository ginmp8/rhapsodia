#!/usr/bin/env python3
"""Capture, verify, and hash immutable evidence used by skill-improvement experiments."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def canonical(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def stable_files(path: Path) -> list[Path]:
    if path.is_symlink():
        raise ValueError(f"symlink evidence is not supported: {path}")
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"evidence path not found: {path}")
    files: list[Path] = []
    for candidate in sorted(path.rglob("*")):
        rel_parts = candidate.relative_to(path).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if candidate.is_symlink():
            raise ValueError(f"symlink evidence is not supported: {candidate}")
        if candidate.is_file():
            files.append(candidate)
    return files


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.stage-", suffix=".json", dir=path.parent)
    os.close(fd)
    stage = Path(raw)
    try:
        with stage.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(stage, path)
    finally:
        stage.unlink(missing_ok=True)


def safe_relative(root: Path, candidate: Path) -> Path:
    try:
        return canonical(candidate).relative_to(canonical(root))
    except ValueError as exc:
        raise ValueError(f"path escapes root: {candidate}") from exc


def ensure_capture_paths_safe(root: Path, selected: list[Path], snapshot_dir: Path, manifest: Path) -> None:
    c_snapshot = canonical(snapshot_dir)
    c_manifest = canonical(manifest)
    if c_snapshot == c_manifest:
        raise ValueError("snapshot directory aliases manifest")
    for path in selected:
        c_path = canonical(path)
        if c_snapshot == c_path or str(c_snapshot).startswith(str(c_path) + os.sep):
            raise ValueError("snapshot directory must not be inside a selected source path")
        if c_manifest == c_path or str(c_manifest).startswith(str(c_path) + os.sep):
            raise ValueError("manifest must not be inside a selected source path")
    safe_relative(root, root)


def capture(root: Path, raw_paths: list[Path], snapshot_dir: Path, manifest_path: Path) -> dict[str, Any]:
    root = canonical(root)
    selected = [canonical(root / p) if not p.is_absolute() else canonical(p) for p in raw_paths]
    for path in selected:
        safe_relative(root, path)
    ensure_capture_paths_safe(root, selected, snapshot_dir, manifest_path)

    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for selected_path in selected:
        selected_rel = safe_relative(root, selected_path)
        for source_file in stable_files(selected_path):
            root_rel = source_file.relative_to(root).as_posix()
            if root_rel in seen:
                continue
            seen.add(root_rel)
            snapshot_file = snapshot_dir / root_rel
            snapshot_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, snapshot_file)
            digest = sha256_file(snapshot_file)
            entries.append(
                {
                    "path": root_rel,
                    "selected_from": selected_rel.as_posix(),
                    "snapshot_path": snapshot_file.relative_to(snapshot_dir).as_posix(),
                    "size": snapshot_file.stat().st_size,
                    "sha256": digest,
                }
            )

    manifest = {
        "manifest_version": 1,
        "root": str(root),
        "snapshot_dir": str(canonical(snapshot_dir)),
        "entries": sorted(entries, key=lambda item: item["path"]),
    }
    write_json_atomic(manifest_path, manifest)
    return {
        "status": "pass",
        "stage": "source-snapshot",
        "manifest": str(canonical(manifest_path)),
        "files": len(entries),
    }


def verify(manifest_path: Path) -> dict[str, Any]:
    manifest_path = canonical(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = canonical(Path(data["root"]))
    snapshot_dir = canonical(Path(data["snapshot_dir"]))
    checks: list[dict[str, Any]] = []
    failures = 0

    for entry in data.get("entries", []):
        rel = Path(entry["path"])
        live = canonical(root / rel)
        snap = canonical(snapshot_dir / Path(entry["snapshot_path"]))
        expected = str(entry["sha256"])
        live_hash = sha256_file(live) if live.is_file() else None
        snapshot_hash = sha256_file(snap) if snap.is_file() else None
        status = "pass" if live_hash == expected and snapshot_hash == expected else "fail"
        if status == "fail":
            failures += 1
        checks.append(
            {
                "path": rel.as_posix(),
                "status": status,
                "expected_sha256": expected,
                "live_sha256": live_hash,
                "snapshot_sha256": snapshot_hash,
            }
        )

    return {
        "status": "pass" if failures == 0 else "fail",
        "stage": "source-snapshot-verify",
        "manifest": str(manifest_path),
        "failures": failures,
        "checks": checks,
    }


def tree_hash(root: Path) -> dict[str, Any]:
    root = canonical(root)
    files = stable_files(root)
    hasher = hashlib.sha256()
    entries: list[dict[str, Any]] = []
    for file_path in files:
        rel = file_path.relative_to(root).as_posix()
        digest = sha256_file(file_path)
        size = file_path.stat().st_size
        hasher.update(rel.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(str(size).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(bytes.fromhex(digest))
        entries.append({"path": rel, "size": size, "sha256": digest})
    return {
        "status": "pass",
        "stage": "hash-tree",
        "root": str(root),
        "file_count": len(entries),
        "tree_sha256": hasher.hexdigest(),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture, verify, or hash evidence for skill-improvement runs.")
    sub = parser.add_subparsers(dest="command", required=True)

    cap = sub.add_parser("capture", help="Copy exact source bytes and write a hash manifest.")
    cap.add_argument("--root", required=True, type=Path)
    cap.add_argument("--path", action="append", required=True, type=Path)
    cap.add_argument("--snapshot-dir", required=True, type=Path)
    cap.add_argument("--manifest", required=True, type=Path)

    ver = sub.add_parser("verify", help="Verify both live and captured bytes against a manifest.")
    ver.add_argument("--manifest", required=True, type=Path)

    htree = sub.add_parser("hash-tree", help="Emit a deterministic identity for a directory tree.")
    htree.add_argument("--root", required=True, type=Path)

    args = parser.parse_args()
    try:
        if args.command == "capture":
            result = capture(args.root, args.path, canonical(args.snapshot_dir), canonical(args.manifest))
        elif args.command == "verify":
            result = verify(args.manifest)
        else:
            result = tree_hash(args.root)
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        return 0 if result.get("status") == "pass" else 1
    except Exception as exc:
        print(
            json.dumps(
                {"status": "fail", "stage": args.command, "error": str(exc)},
                indent=2,
                sort_keys=True,
            ),
            flush=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
