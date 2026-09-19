#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from _harness_common import dump_json, is_noise, is_secret_like, path_is_inside, sha256_file, tree_hash


def iter_snapshot_files(root: Path):
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if is_noise(rel):
            continue
        if path.is_symlink():
            yield path, rel
        elif path.is_file():
            yield path, rel


def capture(target: Path, snapshot_dir: Path, manifest_path: Path) -> dict:
    target = target.resolve(strict=True)
    snapshot_dir = snapshot_dir.expanduser().resolve(strict=False)
    manifest_path = manifest_path.expanduser().resolve(strict=False)
    if path_is_inside(target, snapshot_dir) or path_is_inside(target, manifest_path):
        raise ValueError('snapshot and manifest must be outside the target skill root')
    if snapshot_dir.exists():
        raise FileExistsError(f'snapshot directory already exists: {snapshot_dir}')

    rows = []
    snapshot_dir.mkdir(parents=True, exist_ok=False)
    try:
        for source, rel in iter_snapshot_files(target):
            rel_text = rel.as_posix()
            if is_secret_like(rel_text):
                raise ValueError(f'sensitive-looking file blocks snapshot: {rel_text}')
            destination = snapshot_dir / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                link_target = os.readlink(source)
                resolved = source.resolve(strict=True)
                try:
                    resolved.relative_to(target)
                except ValueError as exc:
                    raise ValueError(f'symlink escapes target root: {rel_text} -> {link_target}') from exc
                if resolved.is_dir():
                    raise ValueError(f'directory symlink is not supported in harness snapshots: {rel_text}')
                shutil.copy2(resolved, destination)
                source_type = 'symlink-file'
            else:
                shutil.copy2(source, destination)
                link_target = None
                source_type = 'file'
            rows.append({
                'path': rel_text,
                'source_type': source_type,
                'link_target': link_target,
                'size': destination.stat().st_size,
                'sha256': sha256_file(destination),
            })
        manifest = {
            'manifest_version': 1,
            'target': str(target),
            'snapshot_dir': str(snapshot_dir),
            'file_count': len(rows),
            'source_tree_sha256': tree_hash(target),
            'snapshot_tree_sha256': tree_hash(snapshot_dir),
            'files': rows,
        }
        dump_json(manifest, str(manifest_path))
        return {'status': 'pass', **{k: manifest[k] for k in ('file_count', 'source_tree_sha256', 'snapshot_tree_sha256')}, 'manifest': str(manifest_path)}
    except Exception:
        shutil.rmtree(snapshot_dir, ignore_errors=True)
        raise


def verify(manifest_path: Path, *, snapshot_only: bool) -> dict:
    manifest_path = manifest_path.expanduser().resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    target = Path(manifest['target'])
    snapshot_dir = Path(manifest['snapshot_dir'])
    snapshot_hash = tree_hash(snapshot_dir) if snapshot_dir.exists() else None
    source_hash = None if snapshot_only else (tree_hash(target) if target.exists() else None)
    snapshot_match = snapshot_hash == manifest.get('snapshot_tree_sha256')
    source_match = True if snapshot_only else source_hash == manifest.get('source_tree_sha256')
    status = 'pass' if snapshot_match and source_match else 'fail'
    return {
        'status': status,
        'manifest': str(manifest_path),
        'snapshot_only': snapshot_only,
        'expected_snapshot_tree_sha256': manifest.get('snapshot_tree_sha256'),
        'actual_snapshot_tree_sha256': snapshot_hash,
        'snapshot_match': snapshot_match,
        'expected_source_tree_sha256': manifest.get('source_tree_sha256'),
        'actual_source_tree_sha256': source_hash,
        'source_match': source_match,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Capture and verify an immutable baseline copy of one target skill package.')
    sub = parser.add_subparsers(dest='command', required=True)

    cap = sub.add_parser('capture')
    cap.add_argument('--target', required=True)
    cap.add_argument('--snapshot-dir', required=True)
    cap.add_argument('--manifest', required=True)

    ver = sub.add_parser('verify')
    ver.add_argument('--manifest', required=True)
    ver.add_argument('--snapshot-only', action='store_true')
    ver.add_argument('--output')

    args = parser.parse_args()
    try:
        if args.command == 'capture':
            report = capture(Path(args.target), Path(args.snapshot_dir), Path(args.manifest))
            dump_json(report, None)
            return 0
        report = verify(Path(args.manifest), snapshot_only=args.snapshot_only)
        dump_json(report, args.output)
        return 0 if report['status'] == 'pass' else 1
    except Exception as exc:
        report = {'status': 'fail', 'stage': args.command, 'error': str(exc)}
        dump_json(report, getattr(args, 'output', None))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
