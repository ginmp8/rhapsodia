#!/usr/bin/env python3
"""Freeze and verify evaluator inputs using SHA-256 manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

NOISE_PARTS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
NOISE_SUFFIXES = {'.pyc', '.pyo'}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def collect(root: Path, selected_paths: list[str]) -> list[dict[str, object]]:
    root = root.resolve()
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw in selected_paths:
        base = (root / raw).resolve()
        try:
            base.relative_to(root)
        except ValueError as exc:
            raise ValueError(f'path escapes target root: {raw}') from exc
        if not base.exists():
            raise FileNotFoundError(raw)
        items = [base] if base.is_file() else sorted(base.rglob('*'))
        for path in items:
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(root)
            if any(part in NOISE_PARTS for part in rel.parts) or path.suffix.lower() in NOISE_SUFFIXES:
                continue
            rel_s = rel.as_posix()
            if rel_s in seen:
                continue
            seen.add(rel_s)
            rows.append({'path': rel_s, 'size_bytes': path.stat().st_size, 'sha256': sha256_file(path)})
    return sorted(rows, key=lambda row: str(row['path']))


def freeze(root: Path, selected_paths: list[str], out: Path) -> dict[str, object]:
    rows = collect(root, selected_paths)
    manifest = {
        'manifest_version': 1,
        'root': root.resolve().as_posix(),
        'selected_paths': selected_paths,
        'files': rows,
    }
    out = out.resolve()
    try:
        out.relative_to(root.resolve())
        raise ValueError('evaluator manifest must be outside the target package so freezing does not change candidate identity')
    except ValueError as exc:
        if str(exc).startswith('evaluator manifest'):
            raise
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return {'status': 'pass', 'file_count': len(rows), 'manifest': out.as_posix()}


def verify(root: Path, manifest_path: Path) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    selected = manifest.get('selected_paths', [])
    if not isinstance(selected, list) or not selected:
        raise ValueError('manifest selected_paths must be a non-empty list')
    expected = manifest.get('files', [])
    current = collect(root, [str(x) for x in selected])
    exp = {str(row['path']): row for row in expected}
    cur = {str(row['path']): row for row in current}
    added = sorted(set(cur) - set(exp))
    removed = sorted(set(exp) - set(cur))
    changed = sorted(
        path for path in set(exp) & set(cur)
        if exp[path].get('sha256') != cur[path].get('sha256') or exp[path].get('size_bytes') != cur[path].get('size_bytes')
    )
    ok = not (added or removed or changed)
    return {'status': 'pass' if ok else 'fail', 'added': added, 'removed': removed, 'changed': changed, 'file_count': len(current)}


def main() -> int:
    parser = argparse.ArgumentParser(description='Freeze or verify evaluator files by SHA-256.')
    sub = parser.add_subparsers(dest='command', required=True)
    freeze_p = sub.add_parser('freeze')
    freeze_p.add_argument('--root', required=True)
    freeze_p.add_argument('--path', action='append', required=True)
    freeze_p.add_argument('--out', required=True)
    verify_p = sub.add_parser('verify')
    verify_p.add_argument('--root', required=True)
    verify_p.add_argument('--manifest', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'freeze':
            result = freeze(Path(args.root), args.path, Path(args.out))
        else:
            result = verify(Path(args.root).resolve(), Path(args.manifest).resolve())
    except Exception as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result.get('status') == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
