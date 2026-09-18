#!/usr/bin/env python3
"""Capture exact external source bytes before analysis and verify their identity later."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


def dump_json(data: object, out: str | None = None) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if out:
        target = Path(out)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        temp = Path(tmp_name)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(text.encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        except Exception:
            if temp.exists():
                temp.unlink()
            raise
    else:
        sys.stdout.write(text)
        sys.stdout.flush()


def lexical_inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def path_is_inside(root: Path, candidate: Path) -> bool:
    root = root.resolve(strict=False)
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def identity_tuple(stat: os.stat_result) -> tuple[int, int, int, int]:
    return int(stat.st_dev), int(stat.st_ino), int(stat.st_size), int(stat.st_mtime_ns)


def identity_dict(stat: os.stat_result) -> dict:
    return {
        "device": int(stat.st_dev),
        "inode": int(stat.st_ino),
        "size": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
    }


def copy_stable_file(source: Path, destination: Path) -> tuple[str, int, dict]:
    before = source.stat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temp = Path(tmp_name)
    digest = hashlib.sha256()
    size = 0
    try:
        with source.open("rb") as src, os.fdopen(fd, "wb") as dst:
            for chunk in iter(lambda: src.read(1024 * 1024), b""):
                digest.update(chunk)
                dst.write(chunk)
                size += len(chunk)
            dst.flush()
            os.fsync(dst.fileno())
        after = source.stat()
        if identity_tuple(before) != identity_tuple(after):
            raise RuntimeError(f"source changed while being snapshotted: {source}")
        os.replace(temp, destination)
        return digest.hexdigest(), size, identity_dict(after)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise


def expand_selection(root: Path, raw: str) -> list[tuple[str, Path, str, str | None]]:
    authored = Path(os.path.abspath(root / raw))
    if not lexical_inside(root, authored):
        raise ValueError(f"path escapes root: {raw}")
    if not authored.exists() and not authored.is_symlink():
        raise FileNotFoundError(raw)

    def one(logical: Path) -> tuple[str, Path, str, str | None]:
        rel = logical.relative_to(root).as_posix()
        if logical.is_symlink():
            link_target = os.readlink(logical)
            resolved = logical.resolve(strict=True)
            if not lexical_inside(root, resolved):
                raise ValueError(f"symlink escapes root: {rel} -> {link_target}")
            if not resolved.is_file():
                raise ValueError(f"directory or non-file symlinks are not supported: {rel}")
            return rel, resolved, "symlink-file", link_target
        if not logical.is_file():
            raise ValueError(f"unsupported source type: {rel}")
        return rel, logical, "file", None

    if authored.is_symlink() or authored.is_file():
        return [one(authored)]
    if not authored.is_dir():
        raise ValueError(f"unsupported selected path: {raw}")

    rows: list[tuple[str, Path, str, str | None]] = []
    for dirpath, dirnames, filenames in os.walk(authored, followlinks=False):
        base = Path(dirpath)
        for name in dirnames:
            candidate = base / name
            if candidate.is_symlink():
                raise ValueError(f"directory symlinks are not supported: {candidate.relative_to(root).as_posix()}")
        for name in filenames:
            rows.append(one(base / name))
    return rows


def capture(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve(strict=True)
    snapshot_root = Path(args.snapshot_dir).expanduser().resolve(strict=False)
    manifest_path = Path(args.out).expanduser().resolve(strict=False)
    if path_is_inside(root, snapshot_root):
        raise ValueError("snapshot directory must be outside the source root")
    if path_is_inside(root, manifest_path):
        raise ValueError("manifest must be outside the source root")

    items: dict[str, tuple[Path, str, str | None]] = {}
    for selected in args.path:
        for rel, actual, source_type, link_target in expand_selection(root, selected):
            items[rel] = (actual, source_type, link_target)
    if not items:
        raise ValueError("source selection resolved to zero files")

    snapshot_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel in sorted(items):
        actual, source_type, link_target = items[rel]
        destination = snapshot_root / rel
        digest, size, identity = copy_stable_file(actual, destination)
        row = {
            "path": rel,
            "source_type": source_type,
            "canonical_source_path": str(actual.resolve(strict=True)),
            "snapshot_path": str(destination.resolve(strict=True)),
            "size": size,
            "sha256": digest,
            "source_identity": identity,
        }
        if link_target is not None:
            row["link_target"] = link_target
        rows.append(row)

    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest = {
        "manifest_version": 1,
        "source_root": str(root),
        "snapshot_root": str(snapshot_root),
        "selected_paths": list(args.path),
        "file_count": len(rows),
        "snapshot_identity_sha256": hashlib.sha256(payload).hexdigest(),
        "files": rows,
    }
    dump_json(manifest, str(manifest_path))
    dump_json({
        "status": "pass",
        "file_count": len(rows),
        "manifest": str(manifest_path),
        "snapshot_root": str(snapshot_root),
        "snapshot_identity_sha256": manifest["snapshot_identity_sha256"],
    })
    return 0


def verify_hash(path: Path, expected_sha: str, expected_size: int) -> tuple[bool, dict]:
    if not path.is_file():
        return False, {"missing": True}
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    actual_sha = digest.hexdigest()
    return size == expected_size and actual_sha == expected_sha, {"size": size, "sha256": actual_sha}


def verify(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = Path(manifest["source_root"])
    snapshot_root = Path(manifest["snapshot_root"])
    snapshot_changed = []
    source_changed = []

    for row in manifest.get("files", []):
        rel = row["path"]
        snapshot = snapshot_root / rel
        ok, evidence = verify_hash(snapshot, row["sha256"], int(row["size"]))
        if not ok:
            snapshot_changed.append({"path": rel, "evidence": evidence})

        if args.snapshot_only:
            continue

        logical = root / rel
        if row.get("source_type") == "symlink-file":
            if not logical.is_symlink():
                source_changed.append({"path": rel, "reason": "symlink-missing-or-replaced"})
                continue
            current_target = os.readlink(logical)
            if current_target != row.get("link_target"):
                source_changed.append({"path": rel, "reason": "symlink-target-changed"})
                continue
            try:
                actual = logical.resolve(strict=True)
            except OSError as exc:
                source_changed.append({"path": rel, "reason": "symlink-unresolvable", "error": str(exc)})
                continue
        else:
            actual = logical

        if not actual.is_file():
            source_changed.append({"path": rel, "reason": "source-missing-or-not-file"})
            continue
        canonical = str(actual.resolve(strict=True))
        if canonical != row.get("canonical_source_path"):
            source_changed.append({"path": rel, "reason": "canonical-source-changed"})
            continue
        ok, evidence = verify_hash(actual, row["sha256"], int(row["size"]))
        if not ok:
            source_changed.append({"path": rel, "reason": "source-bytes-changed", "evidence": evidence})

    passed = not snapshot_changed and not source_changed
    report = {
        "status": "pass" if passed else "fail",
        "manifest": str(manifest_path),
        "snapshot_only": bool(args.snapshot_only),
        "file_count": len(manifest.get("files", [])),
        "snapshot_changed": snapshot_changed,
        "source_changed": source_changed,
    }
    dump_json(report, args.json_out)
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture exact source bytes before analysis and verify their identity later.")
    sub = parser.add_subparsers(dest="command", required=True)

    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--root", required=True)
    capture_parser.add_argument("--path", action="append", required=True)
    capture_parser.add_argument("--snapshot-dir", required=True)
    capture_parser.add_argument("--out", required=True)

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--manifest", required=True)
    verify_parser.add_argument("--snapshot-only", action="store_true")
    verify_parser.add_argument("--json", dest="json_out")

    args = parser.parse_args()
    try:
        return capture(args) if args.command == "capture" else verify(args)
    except Exception as exc:
        dump_json({"status": "fail", "stage": args.command, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
