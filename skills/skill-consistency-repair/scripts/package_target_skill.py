#!/usr/bin/env python3
"""Validate and atomically package a target skill while preserving last-known-good output."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable

from consistency_audit import audit
from inventory_skill import scan_target

EXCLUDED_DIRS = {
    '.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'tmp', '.tmp', 'reports', 'benchmark-reports', 'test-results',
}
EXCLUDED_NAMES = {'.ds_store', 'test-results.json', 'hardening-audit.json'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo', '.swp', '.swo'}
SENSITIVE_NAME_PATTERNS = (
    re.compile(r'(^|[-_.])secret(s)?($|[-_.])', re.IGNORECASE),
    re.compile(r'(^|[-_.])credential(s)?($|[-_.])', re.IGNORECASE),
    re.compile(r'(^|[-_.])token(s)?($|[-_.])', re.IGNORECASE),
    re.compile(r'private[-_.]?key', re.IGNORECASE),
    re.compile(r'^id_rsa($|\.)', re.IGNORECASE),
    re.compile(r'^\.env($|\.)', re.IGNORECASE),
)
ZIP_FORMAT_VERSION = 1
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_REGULAR_MODE = 0o100644
ZIP_EXECUTABLE_MODE = 0o100755


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


def is_sensitive_name(name: str) -> bool:
    return any(pattern.search(name) for pattern in SENSITIVE_NAME_PATTERNS)


def should_exclude(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in rel_parts):
        return True
    name = path.name.lower()
    if name in EXCLUDED_NAMES:
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES or name.endswith(('.zip', '~')):
        return True
    if is_sensitive_name(name):
        return True
    return False


def files_to_zip(root: Path) -> Iterable[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        for filename in filenames:
            path = Path(dirpath) / filename
            if not path.is_symlink() and not should_exclude(path, root):
                files.append(path)
    yield from sorted(files, key=lambda path: path.relative_to(root).as_posix())


def write_normalized_archive(zip_path: Path, target: Path, skill_name: str, files: Iterable[Path]) -> list[str]:
    """Write deterministic ZIP entries independent of source mtime and permissions."""
    names: list[str] = []
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            arcname = f'{skill_name}/{path.relative_to(target).as_posix()}'
            info = zipfile.ZipInfo(arcname, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = ZIP_EXECUTABLE_MODE if path.suffix.lower() in {'.py', '.sh'} else ZIP_REGULAR_MODE
            info.external_attr = mode << 16
            info.flag_bits |= 0x800
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            names.append(arcname)
    return names


def validate_archive(zip_path: Path, skill_name: str | None = None, *, require_normalized: bool = False) -> list[str]:
    errors: list[str] = []
    if not zip_path.exists():
        return ['archive was not created']
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f'archive CRC failure: {bad}')
            infos = zf.infolist()
            names = [info.filename for info in infos]
            tops = {name.split('/', 1)[0] for name in names if name and '/' in name}
            if len(tops) != 1:
                errors.append(f'archive must contain exactly one top-level skill directory, found {sorted(tops)}')
            if skill_name and tops and tops != {skill_name}:
                errors.append(f'archive root must be {skill_name!r}, found {sorted(tops)}')
            if not any(name.endswith('/SKILL.md') for name in names):
                errors.append('archive is missing SKILL.md')
            unsafe = [
                name for name in names
                if name.startswith('/') or '..' in PurePosixPath(name).parts
            ]
            if unsafe:
                errors.append(f'archive includes unsafe paths: {unsafe[:10]}')
            blocked = [name for name in names if any(part in EXCLUDED_DIRS for part in PurePosixPath(name).parts)]
            if blocked:
                errors.append(f'archive includes excluded paths: {blocked[:10]}')
            secretish = [name for name in names if is_sensitive_name(PurePosixPath(name).name.lower())]
            if secretish:
                errors.append(f'archive includes secret-like paths: {secretish[:10]}')
            if require_normalized:
                non_normalized: list[str] = []
                for info in infos:
                    suffix = PurePosixPath(info.filename).suffix.lower()
                    expected_mode = ZIP_EXECUTABLE_MODE if suffix in {'.py', '.sh'} else ZIP_REGULAR_MODE
                    actual_mode = (info.external_attr >> 16) & 0o177777
                    if info.date_time != ZIP_TIMESTAMP or info.create_system != 3 or actual_mode != expected_mode:
                        non_normalized.append(info.filename)
                if non_normalized:
                    errors.append(f'archive includes non-normalized ZIP metadata: {non_normalized[:10]}')
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
    parser.add_argument(
        '--json-output', '--receipt', dest='receipt',
        help='Optional JSON package receipt path.',
    )
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
        included = write_normalized_archive(staged_package, target, skill_name, files_to_zip(target))
        errors = validate_archive(staged_package, skill_name, require_normalized=True)
        if errors:
            staged_package.unlink(missing_ok=True)
            print(json.dumps({'status': 'fail', 'stage': 'archive-validation', 'errors': errors}, indent=2))
            return 1

        staged_targets: list[tuple[Path, Path]] = []
        previous_valid = output.exists() and not validate_archive(output, skill_name, require_normalized=False)
        if previous_valid:
            last_good.parent.mkdir(parents=True, exist_ok=True)
            fd, lkg_name = tempfile.mkstemp(prefix=f'.{last_good.name}.', suffix='.tmp', dir=last_good.parent)
            os.close(fd)
            staged_lkg = Path(lkg_name)
            shutil.copy2(output, staged_lkg)
            staged_targets.append((staged_lkg, last_good))

        package_sha = sha256_file(staged_package)
        receipt = {
            'receipt_version': 2,
            'status': 'pass',
            'stage': 'committed',
            'candidate_identity': inventory.get('inventory_fingerprint'),
            'candidate_sha256': inventory.get('inventory_fingerprint'),
            'package_sha256': package_sha,
            'archive_sha256': package_sha,
            'package_bytes': staged_package.stat().st_size,
            'file_count': len(included),
            'skill_name': skill_name,
            'zip_format_version': ZIP_FORMAT_VERSION,
            'zip_timestamp': '1980-01-01T00:00:00',
            'validation_status': 'pass',
            'final_path': output.as_posix(),
            'atomic_replace': True,
            'previous_valid_package_preserved': bool(previous_valid),
            'last_known_good': last_good.as_posix() if previous_valid else None,
            'output_preserved_on_precommit_failure': True,
            'last_good_preserved_on_failure': True,
            'recovery': [],
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
