#!/usr/bin/env python3
"""Validate and atomically package a target skill while preserving last-known-good output."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

from consistency_audit import audit
from inventory_skill import scan_target

EXCLUDED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'reports', 'benchmark-reports', 'test-results'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}
SECRET_WORDS = {'secret', 'credential', 'private_key', 'id_rsa', '.env'}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def path_is_inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def paths_alias(a: Path, b: Path) -> bool:
    return a.resolve() == b.resolve()


def should_exclude(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in rel_parts):
        return True
    name = path.name.lower()
    if path.suffix.lower() in EXCLUDED_SUFFIXES or name.endswith('.zip'):
        return True
    if any(word in name for word in SECRET_WORDS):
        return True
    return False


def files_to_zip(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        for filename in sorted(filenames):
            path = Path(dirpath) / filename
            if not path.is_symlink() and not should_exclude(path, root):
                yield path


def validate_archive(zip_path: Path, skill_name: str | None = None) -> list[str]:
    errors: list[str] = []
    if not zip_path.exists():
        return ['archive was not created']
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f'archive CRC failure: {bad}')
            names = zf.namelist()
            tops = {name.split('/', 1)[0] for name in names if name and '/' in name}
            if len(tops) != 1:
                errors.append(f'archive must contain exactly one top-level skill directory, found {sorted(tops)}')
            if skill_name and tops and tops != {skill_name}:
                errors.append(f'archive root must be {skill_name!r}, found {sorted(tops)}')
            if not any(name.endswith('/SKILL.md') for name in names):
                errors.append('archive is missing SKILL.md')
            blocked = [name for name in names if any(part in EXCLUDED_DIRS for part in Path(name).parts)]
            if blocked:
                errors.append(f'archive includes excluded paths: {blocked[:10]}')
            secretish = [name for name in names if any(word in Path(name).name.lower() for word in SECRET_WORDS)]
            if secretish:
                errors.append(f'archive includes secret-like paths: {secretish[:10]}')
    except zipfile.BadZipFile as exc:
        errors.append(f'invalid zip: {exc}')
    return errors


def stage_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        Path(name).unlink(missing_ok=True)
        raise
    return Path(name)


def transactional_commit(staged_targets: list[tuple[Path, Path]]) -> dict[str, object]:
    token = secrets.token_hex(8)
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict[str, str]] = []
    try:
        for _, target in staged_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                backup = target.with_name(f'.{target.name}.consistency-backup-{token}')
                os.replace(target, backup)
                backups[target] = backup
        for staged, target in staged_targets:
            os.replace(staged, target)
            committed.append(target)
        for backup in backups.values():
            backup.unlink(missing_ok=True)
        return {'status': 'pass', 'recovery': []}
    except Exception as exc:
        rollback_errors: list[dict[str, str]] = []
        for target in reversed(committed):
            if target.exists():
                failed = target.with_name(f'.{target.name}.consistency-failed-{token}')
                try:
                    os.replace(target, failed)
                    recovery.append({'kind': 'failed-candidate', 'preserved_at': failed.as_posix()})
                except Exception as rollback_exc:
                    rollback_errors.append({'target': target.as_posix(), 'error': str(rollback_exc)})
        for target, backup in backups.items():
            if backup.exists():
                try:
                    os.replace(backup, target)
                except Exception as rollback_exc:
                    recovery.append({'kind': 'previous-output-backup', 'preserved_at': backup.as_posix()})
                    rollback_errors.append({'target': target.as_posix(), 'error': str(rollback_exc)})
        raise RuntimeError(json.dumps({'commit_error': str(exc), 'rollback_errors': rollback_errors, 'recovery': recovery})) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description='Package a target skill after consistency validation with atomic delivery.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--allow-findings', action='store_true', help='Package even if static audit has high/blocker findings.')
    parser.add_argument('--last-good', help='Path for preserving the previous validated package. Defaults beside output.')
    parser.add_argument('--receipt', help='Optional JSON package receipt path; must be outside target.')
    args = parser.parse_args()

    target = Path(args.target).resolve()
    output = Path(args.output).expanduser().resolve()
    last_good = Path(args.last_good).expanduser().resolve() if args.last_good else output.with_name(output.stem + '.last-good' + output.suffix)
    receipt_path = Path(args.receipt).expanduser().resolve() if args.receipt else None

    try:
        if output.suffix.lower() != '.zip':
            raise ValueError('output must use .zip')
        if path_is_inside(target, output) or path_is_inside(target, last_good) or (receipt_path and path_is_inside(target, receipt_path)):
            raise ValueError('output, last-good, and receipt paths must stay outside the target so candidate identity remains frozen')
        if paths_alias(output, last_good):
            raise ValueError('output and last-good paths must differ')
        if receipt_path and (paths_alias(output, receipt_path) or paths_alias(last_good, receipt_path)):
            raise ValueError('receipt must not alias package or last-good output')

        result = audit(target)
        if args.validate and result['score']['status'] != 'pass' and not args.allow_findings:
            print(json.dumps({'status': 'fail', 'stage': 'validation', 'reason': 'consistency audit failed', 'score': result['score'], 'findings': result['findings'][:10]}, indent=2, ensure_ascii=False))
            return 2

        inventory = scan_target(target)
        skill_name = inventory.get('frontmatter', {}).get('fields', {}).get('name') or target.name
        output.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f'.{output.name}.', suffix='.tmp', dir=output.parent)
        os.close(fd)
        staged_package = Path(temp_name)
        included: list[str] = []
        with zipfile.ZipFile(staged_package, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for path in files_to_zip(target):
                arcname = f'{skill_name}/{path.relative_to(target).as_posix()}'
                zf.write(path, arcname)
                included.append(arcname)
        errors = validate_archive(staged_package, skill_name)
        if errors:
            staged_package.unlink(missing_ok=True)
            print(json.dumps({'status': 'fail', 'stage': 'archive-validation', 'errors': errors}, indent=2))
            return 1

        staged_targets: list[tuple[Path, Path]] = []
        previous_valid = output.exists() and not validate_archive(output, skill_name)
        if previous_valid:
            last_good.parent.mkdir(parents=True, exist_ok=True)
            fd, lkg_name = tempfile.mkstemp(prefix=f'.{last_good.name}.', suffix='.tmp', dir=last_good.parent)
            os.close(fd)
            staged_lkg = Path(lkg_name)
            shutil.copy2(output, staged_lkg)
            staged_targets.append((staged_lkg, last_good))

        package_sha = sha256_file(staged_package)
        receipt = {
            'receipt_version': 1,
            'status': 'pass',
            'candidate_identity': inventory.get('inventory_fingerprint'),
            'package_sha256': package_sha,
            'package_bytes': staged_package.stat().st_size,
            'file_count': len(included),
            'skill_name': skill_name,
            'previous_valid_package_preserved': bool(previous_valid),
            'last_known_good': last_good.as_posix() if previous_valid else None,
            'output_preserved_on_precommit_failure': True,
        }
        staged_targets.append((staged_package, output))
        if receipt_path:
            staged_targets.append((stage_json(receipt_path, receipt), receipt_path))
        transactional_commit(staged_targets)
        print(json.dumps({**receipt, 'output': output.as_posix(), 'receipt': receipt_path.as_posix() if receipt_path else None}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'fail', 'stage': 'preflight-or-commit', 'error': str(exc), 'output_preserved': output.exists()}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
