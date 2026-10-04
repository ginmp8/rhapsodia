#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _common import atomic_write_json, canonical_future_path, is_noise, path_is_inside, sha256_file


def selected_files(root: Path, selected: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for raw in selected:
        rel = Path(raw)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError(f'path must be relative and stay inside root: {raw}')
        source = (root / rel).resolve()
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise ValueError(f'path escapes root: {raw}') from exc
        if not source.exists():
            raise FileNotFoundError(f'selected path does not exist: {raw}')
        if source.is_symlink():
            raise ValueError(f'symlink evidence is not accepted: {raw}')
        candidates = [source] if source.is_file() else sorted(source.rglob('*'))
        for path in candidates:
            if path.is_symlink():
                raise ValueError(f'symlink evidence is not accepted: {path.relative_to(root)}')
            if not path.is_file():
                continue
            rel_path = path.relative_to(root)
            if is_noise(rel_path):
                continue
            key = rel_path.as_posix()
            if key not in seen:
                seen.add(key)
                files.append(path)
    return sorted(files)


def capture(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    snapshot_dir = canonical_future_path(args.snapshot_dir)
    manifest = canonical_future_path(args.manifest)

    if not root.is_dir():
        raise ValueError(f'root is not a directory: {root}')
    if path_is_inside(root, snapshot_dir):
        raise ValueError('snapshot directory must be outside the evidence root')
    if path_is_inside(root, manifest):
        raise ValueError('manifest must be outside the evidence root')
    if snapshot_dir.exists() and any(snapshot_dir.iterdir()):
        raise ValueError(f'snapshot directory must be absent or empty: {snapshot_dir}')

    files = selected_files(root, args.path)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for source in files:
        rel = source.relative_to(root)
        dest = snapshot_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        source_hash = sha256_file(source)
        snapshot_hash = sha256_file(dest)
        if source_hash != snapshot_hash:
            raise RuntimeError(f'copied bytes differ for {rel.as_posix()}')
        rows.append({
            'path': rel.as_posix(),
            'size': source.stat().st_size,
            'sha256': source_hash
        })

    payload = {
        'manifest_version': 1,
        'root': str(root),
        'snapshot_dir': str(snapshot_dir),
        'selected_paths': args.path,
        'files': rows
    }
    atomic_write_json(manifest, payload)
    result = {'status': 'pass', 'manifest': str(manifest), 'snapshot_dir': str(snapshot_dir), 'file_count': len(rows)}
    print(json.dumps(result, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    root = Path(data['root']).resolve()
    snapshot_dir = Path(data['snapshot_dir']).resolve()
    expected = {row['path']: row for row in data.get('files', [])}
    current_files = selected_files(root, data.get('selected_paths', []))
    current_paths = {path.relative_to(root).as_posix() for path in current_files}
    expected_paths = set(expected)

    added = sorted(current_paths - expected_paths)
    removed = sorted(expected_paths - current_paths)
    source_changed: list[str] = []
    snapshot_changed: list[str] = []
    missing_snapshot: list[str] = []

    for rel, row in expected.items():
        source = root / rel
        snap = snapshot_dir / rel
        if source.exists() and source.is_file() and sha256_file(source) != row['sha256']:
            source_changed.append(rel)
        if not snap.exists() or not snap.is_file():
            missing_snapshot.append(rel)
        elif sha256_file(snap) != row['sha256']:
            snapshot_changed.append(rel)

    ok = not (added or removed or source_changed or snapshot_changed or missing_snapshot)
    result = {
        'status': 'pass' if ok else 'fail',
        'manifest': str(manifest_path),
        'added': added,
        'removed': removed,
        'source_changed': source_changed,
        'snapshot_changed': snapshot_changed,
        'missing_snapshot': missing_snapshot,
        'file_count': len(expected)
    }
    if args.json_output:
        atomic_write_json(Path(args.json_output), result)
    print(json.dumps(result, indent=2))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description='Capture and verify immutable local evidence snapshots.')
    sub = parser.add_subparsers(dest='command', required=True)

    cap = sub.add_parser('capture')
    cap.add_argument('--root', required=True)
    cap.add_argument('--path', action='append', required=True)
    cap.add_argument('--snapshot-dir', required=True)
    cap.add_argument('--manifest', required=True)

    ver = sub.add_parser('verify')
    ver.add_argument('--manifest', required=True)
    ver.add_argument('--json-output')

    args = parser.parse_args()
    try:
        return capture(args) if args.command == 'capture' else verify(args)
    except Exception as exc:
        result = {'status': 'fail', 'error': str(exc)}
        if getattr(args, 'json_output', None):
            atomic_write_json(Path(args.json_output), result)
        print(json.dumps(result, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
