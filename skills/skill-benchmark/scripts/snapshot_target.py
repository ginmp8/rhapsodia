#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from _common import dump_json, iter_files, path_is_inside, sha256_file, tree_hash


def copy_file(source: Path, destination: Path) -> dict:
    before = source.stat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    after = source.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        destination.unlink(missing_ok=True)
        raise RuntimeError(f'source changed while being snapshotted: {source}')
    digest = sha256_file(destination)
    if digest != sha256_file(source):
        destination.unlink(missing_ok=True)
        raise RuntimeError(f'source hash changed while being snapshotted: {source}')
    return {
        'size': destination.stat().st_size,
        'sha256': digest,
        'source_identity': {
            'device': int(after.st_dev),
            'inode': int(after.st_ino),
            'size': int(after.st_size),
            'mtime_ns': int(after.st_mtime_ns),
        },
    }


def capture(target: Path, snapshot: Path, manifest_path: Path) -> dict:
    target = target.resolve(strict=True)
    snapshot = snapshot.resolve(strict=False)
    manifest_path = manifest_path.resolve(strict=False)
    if not target.is_dir():
        raise ValueError(f'target is not a directory: {target}')
    if path_is_inside(target, snapshot) or path_is_inside(target, manifest_path):
        raise ValueError('snapshot and manifest must be outside the benchmark target')
    if snapshot.exists():
        if any(snapshot.iterdir()):
            raise ValueError(f'snapshot directory must be empty or absent: {snapshot}')
    snapshot.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for source in iter_files(target):
        rel = source.relative_to(target).as_posix()
        if source.is_symlink():
            raise ValueError(f'symlink is not accepted as benchmark source evidence: {rel}')
        destination = snapshot / rel
        evidence = copy_file(source, destination)
        rows.append({'path': rel, 'snapshot_path': str(destination.resolve(strict=True)), **evidence})

    if not rows:
        raise ValueError('target contains no benchmarkable files')
    snapshot_sha = tree_hash(snapshot, reject_symlinks=True)
    manifest = {
        'manifest_version': 1,
        'status': 'pass',
        'source_root': str(target),
        'snapshot_root': str(snapshot),
        'source_tree_sha256': snapshot_sha,
        'file_count': len(rows),
        'files': rows,
    }
    dump_json(manifest, manifest_path)
    return manifest


def verify(manifest_path: Path, *, snapshot_only: bool) -> dict:
    manifest_path = manifest_path.resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    source = Path(manifest['source_root'])
    snapshot = Path(manifest['snapshot_root'])
    expected_tree = manifest['source_tree_sha256']
    snapshot_errors: list[dict] = []
    source_errors: list[dict] = []

    try:
        actual_snapshot_tree = tree_hash(snapshot, reject_symlinks=True)
    except Exception as exc:
        actual_snapshot_tree = None
        snapshot_errors.append({'reason': 'snapshot-unreadable', 'error': str(exc)})
    if actual_snapshot_tree != expected_tree:
        snapshot_errors.append({'reason': 'snapshot-tree-changed', 'expected': expected_tree, 'actual': actual_snapshot_tree})

    if not snapshot_only:
        for row in manifest.get('files', []):
            rel = row['path']
            path = source / rel
            if not path.is_file() or path.is_symlink():
                source_errors.append({'path': rel, 'reason': 'source-missing-or-nonportable'})
                continue
            digest = sha256_file(path)
            if digest != row['sha256'] or path.stat().st_size != row['size']:
                source_errors.append({'path': rel, 'reason': 'source-bytes-changed', 'expected_sha256': row['sha256'], 'actual_sha256': digest})

    status = 'pass' if not snapshot_errors and not source_errors else 'fail'
    return {
        'status': status,
        'manifest': str(manifest_path),
        'snapshot_only': snapshot_only,
        'source_tree_sha256': expected_tree,
        'snapshot_errors': snapshot_errors,
        'source_errors': source_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Capture exact benchmark target bytes and verify their identity later.')
    sub = parser.add_subparsers(dest='command', required=True)

    c = sub.add_parser('capture')
    c.add_argument('--target', required=True)
    c.add_argument('--snapshot-dir', required=True)
    c.add_argument('--out', required=True)

    v = sub.add_parser('verify')
    v.add_argument('--manifest', required=True)
    v.add_argument('--snapshot-only', action='store_true')
    v.add_argument('--json', dest='json_output')

    args = parser.parse_args()
    try:
        if args.command == 'capture':
            result = capture(Path(args.target), Path(args.snapshot_dir), Path(args.out))
        else:
            result = verify(Path(args.manifest), snapshot_only=args.snapshot_only)
            if args.json_output:
                dump_json(result, args.json_output)
        dump_json(result)
        return 0 if result.get('status') == 'pass' else 1
    except Exception as exc:
        result = {'status': 'fail', 'stage': args.command, 'error': str(exc)}
        try:
            if getattr(args, 'json_output', None):
                dump_json(result, args.json_output)
        except Exception:
            pass
        dump_json(result)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
