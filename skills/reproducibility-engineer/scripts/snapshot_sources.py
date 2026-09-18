#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from _common import dump_json, path_is_inside


def lexical_inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def identity_tuple(stat: os.stat_result) -> tuple[int, int, int, int]:
    return (int(stat.st_dev), int(stat.st_ino), int(stat.st_size), int(stat.st_mtime_ns))


def identity_dict(stat: os.stat_result) -> dict:
    return {
        'device': int(stat.st_dev),
        'inode': int(stat.st_ino),
        'size': int(stat.st_size),
        'mtime_ns': int(stat.st_mtime_ns),
    }


def fsync_dir(path: Path) -> None:
    if os.name == 'nt':
        return
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def copy_stable_file(source: Path, destination: Path) -> tuple[str, int, dict]:
    before = source.stat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{destination.name}.', suffix='.tmp', dir=destination.parent)
    tmp = Path(tmp_name)
    h = hashlib.sha256()
    size = 0
    try:
        with source.open('rb') as src, os.fdopen(fd, 'wb') as dst:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
                dst.write(chunk)
                size += len(chunk)
            dst.flush()
            os.fsync(dst.fileno())
        after = source.stat()
        if identity_tuple(before) != identity_tuple(after):
            raise RuntimeError(f'source changed while being snapshotted: {source}')
        os.replace(tmp, destination)
        fsync_dir(destination.parent)
        return h.hexdigest(), size, identity_dict(after)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def expand_selection(root: Path, raw: str) -> list[tuple[str, Path, str, str | None]]:
    authored = Path(os.path.abspath(root / raw))
    if not lexical_inside(root, authored):
        raise ValueError(f'path escapes root: {raw}')
    if not authored.exists() and not authored.is_symlink():
        raise FileNotFoundError(raw)

    def one(logical: Path, actual: Path) -> tuple[str, Path, str, str | None]:
        rel = logical.relative_to(root).as_posix()
        if logical.is_symlink():
            link_target = os.readlink(logical)
            resolved = logical.resolve(strict=True)
            if not lexical_inside(root, resolved):
                raise ValueError(f'symlink escapes root: {rel} -> {link_target}')
            if not resolved.is_file():
                raise ValueError(f'directory or non-file symlinks are not supported for source snapshots: {rel}')
            return rel, resolved, 'symlink-file', link_target
        if not actual.is_file():
            raise ValueError(f'unsupported source type: {rel}')
        return rel, actual, 'file', None

    if authored.is_symlink() or authored.is_file():
        return [one(authored, authored)]
    if not authored.is_dir():
        raise ValueError(f'unsupported selected path: {raw}')

    rows = []
    for dirpath, dirnames, filenames in os.walk(authored, followlinks=False):
        base = Path(dirpath)
        for name in list(dirnames):
            p = base / name
            if p.is_symlink():
                raise ValueError(f'directory symlinks are not supported for source snapshots: {p.relative_to(root).as_posix()}')
        for name in filenames:
            p = base / name
            rows.append(one(p, p))
    return rows


def capture(args) -> int:
    root = Path(args.root).expanduser().resolve(strict=True)
    snapshot_root = Path(args.snapshot_dir).expanduser().resolve(strict=False)
    out = Path(args.out).expanduser().resolve(strict=False)
    if path_is_inside(root, snapshot_root):
        raise ValueError('snapshot directory must be outside the source root')
    if path_is_inside(root, out):
        raise ValueError('manifest must be outside the source root')

    items: dict[str, tuple[Path, str, str | None]] = {}
    for selected in args.path:
        for rel, actual, source_type, link_target in expand_selection(root, selected):
            existing = items.get(rel)
            candidate = (actual, source_type, link_target)
            if existing and existing != candidate:
                raise ValueError(f'conflicting source selection for {rel}')
            items[rel] = candidate

    if not items:
        raise ValueError('source selection resolved to zero files')

    snapshot_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel in sorted(items):
        actual, source_type, link_target = items[rel]
        destination = snapshot_root / rel
        digest, size, identity = copy_stable_file(actual, destination)
        row = {
            'path': rel,
            'source_type': source_type,
            'canonical_source_path': str(actual.resolve(strict=True)),
            'snapshot_path': str(destination.resolve(strict=True)),
            'size': size,
            'sha256': digest,
            'source_identity': identity,
        }
        if link_target is not None:
            row['link_target'] = link_target
        rows.append(row)

    payload = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('utf-8')
    manifest = {
        'manifest_version': 1,
        'source_root': str(root),
        'snapshot_root': str(snapshot_root),
        'selected_paths': list(args.path),
        'file_count': len(rows),
        'snapshot_identity_sha256': hashlib.sha256(payload).hexdigest(),
        'files': rows,
    }
    dump_json(manifest, str(out))
    dump_json({'status': 'pass', 'file_count': len(rows), 'manifest': str(out), 'snapshot_root': str(snapshot_root), 'snapshot_identity_sha256': manifest['snapshot_identity_sha256']}, None)
    return 0


def verify_file_hash(path: Path, expected_sha: str, expected_size: int) -> tuple[bool, dict]:
    if not path.is_file():
        return False, {'missing': True}
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
            size += len(chunk)
    actual_sha = h.hexdigest()
    ok = size == expected_size and actual_sha == expected_sha
    return ok, {'size': size, 'sha256': actual_sha}


def verify(args) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    root = Path(manifest['source_root'])
    snapshot_root = Path(manifest['snapshot_root'])
    snapshot_changed = []
    source_changed = []

    for row in manifest.get('files', []):
        rel = row['path']
        snap = snapshot_root / rel
        ok, evidence = verify_file_hash(snap, row['sha256'], int(row['size']))
        if not ok:
            snapshot_changed.append({'path': rel, 'evidence': evidence})

        if args.snapshot_only:
            continue

        logical = root / rel
        source_type = row.get('source_type', 'file')
        if source_type == 'symlink-file':
            if not logical.is_symlink():
                source_changed.append({'path': rel, 'reason': 'symlink-missing-or-replaced'})
                continue
            current_target = os.readlink(logical)
            if current_target != row.get('link_target'):
                source_changed.append({'path': rel, 'reason': 'symlink-target-changed', 'expected': row.get('link_target'), 'actual': current_target})
                continue
            try:
                actual = logical.resolve(strict=True)
            except OSError as exc:
                source_changed.append({'path': rel, 'reason': 'symlink-unresolvable', 'error': str(exc)})
                continue
        else:
            actual = logical

        if not actual.is_file():
            source_changed.append({'path': rel, 'reason': 'source-missing-or-not-file'})
            continue
        canonical = str(actual.resolve(strict=True))
        if canonical != row.get('canonical_source_path'):
            source_changed.append({'path': rel, 'reason': 'canonical-source-changed', 'expected': row.get('canonical_source_path'), 'actual': canonical})
            continue
        ok, evidence = verify_file_hash(actual, row['sha256'], int(row['size']))
        if not ok:
            source_changed.append({'path': rel, 'reason': 'source-bytes-changed', 'evidence': evidence})

    ok = not snapshot_changed and not source_changed
    report = {
        'status': 'pass' if ok else 'fail',
        'manifest': str(manifest_path),
        'snapshot_only': bool(args.snapshot_only),
        'snapshot_changed': snapshot_changed,
        'source_changed': source_changed,
        'file_count': len(manifest.get('files', [])),
    }
    dump_json(report, args.json_out)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description='Capture exact source bytes before analysis and verify that evidence identity later remains stable.')
    sub = ap.add_subparsers(dest='cmd', required=True)

    c = sub.add_parser('capture')
    c.add_argument('--root', required=True)
    c.add_argument('--path', action='append', required=True)
    c.add_argument('--snapshot-dir', required=True)
    c.add_argument('--out', required=True)

    v = sub.add_parser('verify')
    v.add_argument('--manifest', required=True)
    v.add_argument('--snapshot-only', action='store_true')
    v.add_argument('--json', dest='json_out')

    args = ap.parse_args()
    try:
        return capture(args) if args.cmd == 'capture' else verify(args)
    except Exception as exc:
        report = {'status': 'fail', 'stage': args.cmd, 'error': str(exc)}
        out = getattr(args, 'json_out', None)
        try:
            dump_json(report, out)
        except Exception:
            dump_json(report, None)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
