#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from collections import Counter
from pathlib import Path

from _common import dump_json, iter_files, markdown_local_links, parse_frontmatter, sha256_file, tree_hash


def main() -> int:
    ap = argparse.ArgumentParser(description='Inventory one skill package without modifying it.')
    ap.add_argument('--target', required=True)
    ap.add_argument('--json', dest='json_out')
    args = ap.parse_args()

    root = Path(args.target).resolve()
    skill_md = root / 'SKILL.md'
    errors = []
    warnings = []
    if not root.is_dir():
        errors.append(f'target is not a directory: {root}')
    if not skill_md.is_file():
        errors.append('missing root SKILL.md')

    nested = []
    if root.is_dir():
        nested = [p.relative_to(root).as_posix() for p in root.rglob('SKILL.md') if p != skill_md]
        if nested:
            warnings.append(f'found nested SKILL.md files: {nested}')

    files = []
    ext_counts = Counter()
    total_bytes = 0
    if root.is_dir():
        for p in iter_files(root):
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                files.append({'path': rel, 'type': 'symlink'})
                continue
            size = p.stat().st_size
            total_bytes += size
            ext_counts[p.suffix.lower() or '<none>'] += 1
            row = {'path': rel, 'size': size}
            if rel == 'SKILL.md' or rel.startswith(('evals/', 'scripts/')):
                row['sha256'] = sha256_file(p)
            files.append(row)

    fm = parse_frontmatter(skill_md) if skill_md.is_file() else {}
    root_dirs = sorted([p.name for p in root.iterdir() if p.is_dir()]) if root.is_dir() else []
    local_links = []
    if skill_md.is_file():
        for target in markdown_local_links(skill_md):
            local_links.append(target)

    report = {
        'status': 'fail' if errors else 'pass',
        'target': str(root),
        'identity': {
            'name': fm.get('name', ''),
            'description': fm.get('description', ''),
            'skill_sha256': sha256_file(skill_md) if skill_md.is_file() else None,
            'tree_sha256': tree_hash(root) if root.is_dir() else None,
        },
        'root_dirs': root_dirs,
        'file_count': len(files),
        'total_bytes': total_bytes,
        'extension_counts': dict(sorted(ext_counts.items())),
        'local_links_from_skill_md': local_links,
        'nested_skill_files': nested,
        'files': files,
        'errors': errors,
        'warnings': warnings,
    }
    dump_json(report, args.json_out)
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
