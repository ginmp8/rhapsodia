#!/usr/bin/env python3
"""Validate and package a repaired target skill as skill.zip."""
from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path
from typing import Iterable

from consistency_audit import audit

EXCLUDED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'reports', 'benchmark-reports', 'test-results'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}
SECRET_WORDS = {'secret', 'credential', 'token', 'private_key', 'id_rsa', '.env'}


def should_exclude(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in rel_parts):
        return True
    name = path.name.lower()
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if name.endswith('.zip'):
        return True
    if any(word in name for word in SECRET_WORDS):
        return True
    return False


def files_to_zip(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if not should_exclude(path, root):
                yield path


def validate_archive(zip_path: Path) -> list[str]:
    errors: list[str] = []
    if not zip_path.exists():
        return ['archive was not created']
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        tops = {name.split('/', 1)[0] for name in names if name and '/' in name}
        if len(tops) != 1:
            errors.append(f'archive must contain exactly one top-level skill directory, found {sorted(tops)}')
        if not any(name.endswith('/SKILL.md') for name in names):
            errors.append('archive is missing SKILL.md')
        blocked = [name for name in names if any(part in EXCLUDED_DIRS for part in Path(name).parts)]
        if blocked:
            errors.append(f'archive includes excluded paths: {blocked[:10]}')
        secretish = [name for name in names if any(word in Path(name).name.lower() for word in SECRET_WORDS)]
        if secretish:
            errors.append(f'archive includes secret-like paths: {secretish[:10]}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Package a target skill after consistency validation.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--allow-findings', action='store_true', help='Package even if audit has high/blocker findings.')
    args = parser.parse_args()

    target = Path(args.target).resolve()
    output = Path(args.output).resolve()
    result = audit(target)
    if args.validate and result['score']['status'] != 'pass' and not args.allow_findings:
        print(json.dumps({'status': 'fail', 'reason': 'consistency audit failed', 'score': result['score'], 'findings': result['findings'][:10]}, indent=2, ensure_ascii=False))
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    root_name = target.name
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files_to_zip(target):
            arcname = f'{root_name}/{path.relative_to(target).as_posix()}'
            zf.write(path, arcname)
    errors = validate_archive(output)
    if errors:
        print(json.dumps({'status': 'fail', 'errors': errors, 'output': output.as_posix()}, indent=2))
        return 1
    print(json.dumps({'status': 'pass', 'output': output.as_posix(), 'size_bytes': output.stat().st_size, 'audit_score': result['score']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
