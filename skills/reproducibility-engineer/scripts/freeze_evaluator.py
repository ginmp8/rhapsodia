#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path

from _common import is_noise, sha256_file


def collect(root: Path, rel_paths: list[str]) -> list[dict]:
    rows = []
    seen = set()
    for rel in rel_paths:
        base = (root / rel).resolve()
        try:
            base.relative_to(root)
        except ValueError:
            raise ValueError(f'path escapes root: {rel}')
        if not base.exists():
            raise FileNotFoundError(rel)
        items = [base] if base.is_file() else sorted(base.rglob('*'))
        for p in items:
            if not p.is_file() or p.is_symlink():
                continue
            rp = p.relative_to(root)
            if is_noise(rp) or rp.as_posix() in seen:
                continue
            seen.add(rp.as_posix())
            rows.append({'path':rp.as_posix(),'size':p.stat().st_size,'sha256':sha256_file(p)})
    return sorted(rows, key=lambda x: x['path'])


def freeze(args) -> int:
    root = Path(args.root).resolve()
    rows = collect(root, args.path)
    manifest = {'manifest_version':1,'root':str(root),'selected_paths':args.path,'files':rows}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status':'pass','file_count':len(rows),'manifest':str(out)}, indent=2))
    return 0


def verify(args) -> int:
    root = Path(args.root).resolve()
    manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    selected = manifest.get('selected_paths', [])
    current = collect(root, selected)
    expected = manifest.get('files', [])
    exp_map = {x['path']:x for x in expected}
    cur_map = {x['path']:x for x in current}
    added = sorted(set(cur_map) - set(exp_map))
    removed = sorted(set(exp_map) - set(cur_map))
    changed = sorted(p for p in set(exp_map) & set(cur_map) if exp_map[p]['sha256'] != cur_map[p]['sha256'] or exp_map[p]['size'] != cur_map[p]['size'])
    ok = not (added or removed or changed)
    print(json.dumps({'status':'pass' if ok else 'fail','added':added,'removed':removed,'changed':changed,'file_count':len(current)}, indent=2))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description='Freeze or verify evaluator files by SHA-256.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('freeze')
    f.add_argument('--root', required=True)
    f.add_argument('--path', action='append', required=True)
    f.add_argument('--out', required=True)
    v = sub.add_parser('verify')
    v.add_argument('--root', required=True)
    v.add_argument('--manifest', required=True)
    args = ap.parse_args()
    try:
        return freeze(args) if args.cmd == 'freeze' else verify(args)
    except Exception as exc:
        print(json.dumps({'status':'fail','error':str(exc)}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
