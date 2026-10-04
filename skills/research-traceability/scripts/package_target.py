#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import tempfile
import zipfile
from pathlib import Path

from _common import (
    atomic_write_bytes,
    canonical_future_path,
    fsync_dir,
    is_noise,
    is_secret_like,
    path_is_inside,
    paths_alias,
    sha256_file,
    tree_hash,
)
from validate_target_skill import run_validation


def stage_bytes(parent: Path, name: str, data: bytes) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{name}.', suffix='.tmp', dir=parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return temp
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def target_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if is_noise(rel):
            continue
        if path.is_symlink():
            raise ValueError(f'symlink path blocked: {rel.as_posix()}')
        if not path.is_file():
            continue
        if path.suffix.lower() in {'.zip', '.pyc', '.pyo'}:
            continue
        if is_secret_like(rel):
            raise ValueError(f'secret-like file blocked: {rel.as_posix()}')
        files.append(path)
    return files


def transactional_commit(staged: list[tuple[Path, Path]]) -> dict:
    token = secrets.token_hex(8)
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict] = []
    try:
        for _, target in staged:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                backup = target.with_name(f'.{target.name}.research-traceability-backup-{token}')
                if backup.exists() or backup.is_symlink():
                    raise RuntimeError(f'backup already exists: {backup}')
                os.replace(target, backup)
                backups[target] = backup
        for source, target in staged:
            os.replace(source, target)
            committed.append(target)
            fsync_dir(target.parent)
        for backup in backups.values():
            backup.unlink(missing_ok=True)
        return {'status': 'pass', 'recovery': []}
    except Exception as exc:
        for target in reversed(committed):
            if target.exists() or target.is_symlink():
                failed = target.with_name(f'.{target.name}.research-traceability-failed-{token}')
                try:
                    os.replace(target, failed)
                    recovery.append({'kind': 'failed-candidate', 'preserved_at': str(failed)})
                except OSError:
                    recovery.append({'kind': 'unrecovered-target', 'preserved_at': str(target)})
        for target, backup in backups.items():
            if backup.exists() or backup.is_symlink():
                try:
                    os.replace(backup, target)
                except OSError:
                    recovery.append({'kind': 'previous-output-backup', 'preserved_at': str(backup)})
        for source, _ in staged:
            if source.exists():
                recovery.append({'kind': 'staged-candidate', 'preserved_at': str(source)})
        raise RuntimeError(json.dumps({'error': str(exc), 'recovery': recovery})) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate and atomically package one frozen target skill.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--receipt')
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    output = canonical_future_path(args.output)
    receipt = canonical_future_path(args.receipt) if args.receipt else None

    if Path(args.output).suffix.lower() != '.zip' or output.suffix.lower() != '.zip':
        print(json.dumps({'status': 'fail', 'stage': 'preflight', 'error': 'output must use and resolve to .zip'}, indent=2))
        return 1
    if path_is_inside(root, output):
        print(json.dumps({'status': 'fail', 'stage': 'preflight', 'error': 'output must be outside the target'}, indent=2))
        return 1
    if receipt:
        if Path(args.receipt).suffix.lower() != '.json' or receipt.suffix.lower() != '.json':
            print(json.dumps({'status': 'fail', 'stage': 'preflight', 'error': 'receipt must use and resolve to .json'}, indent=2))
            return 1
        if path_is_inside(root, receipt) or paths_alias(output, receipt):
            print(json.dumps({'status': 'fail', 'stage': 'preflight', 'error': 'receipt must be outside target and not alias package'}, indent=2))
            return 1

    validation = run_validation(root)
    if validation['status'] == 'fail':
        print(json.dumps({'status': 'fail', 'stage': 'validation', 'validation': validation}, indent=2))
        return 1

    from _common import parse_frontmatter
    skill_name = parse_frontmatter(root / 'SKILL.md').get('name', '')
    if not skill_name:
        print(json.dumps({'status': 'fail', 'stage': 'validation', 'error': 'missing skill name'}, indent=2))
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{output.name}.', suffix='.tmp', dir=output.parent)
    os.close(fd)
    staged_zip = Path(temp_name)
    staged_receipt: Path | None = None
    try:
        files = target_files(root)
        included: list[str] = []
        with zipfile.ZipFile(staged_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in files:
                rel = path.relative_to(root).as_posix()
                arc = f'{skill_name}/{rel}'
                info = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                mode = 0o755 if path.suffix.lower() in {'.py', '.sh'} else 0o644
                info.external_attr = mode << 16
                zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
                included.append(arc)
        with staged_zip.open('rb') as handle:
            os.fsync(handle.fileno())
        with zipfile.ZipFile(staged_zip, 'r') as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f'archive CRC failure: {bad}')
            names = zf.namelist()
            if set(names) != set(included):
                raise RuntimeError('archive entry set differs from staged source set')
            if any(not name.startswith(skill_name + '/') or '..' in Path(name).parts for name in names):
                raise RuntimeError('archive contains an unsafe entry')

        result = {
            'receipt_version': 1,
            'status': 'pass',
            'stage': 'committed',
            'target': str(root),
            'skill_name': skill_name,
            'output': str(output),
            'source_tree_sha256': tree_hash(root),
            'package_sha256': sha256_file(staged_zip),
            'package_bytes': staged_zip.stat().st_size,
            'file_count': len(included),
            'validation_status': validation['status'],
            'output_preserved_on_failure': True,
            'recovery': []
        }
        staged: list[tuple[Path, Path]] = [(staged_zip, output)]
        if receipt:
            staged_receipt = stage_bytes(receipt.parent, receipt.name, (json.dumps(result, indent=2) + '\n').encode('utf-8'))
            staged.append((staged_receipt, receipt))
        transactional_commit(staged)
        staged_zip = Path('')
        staged_receipt = None
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        recovery: list[dict] = []
        try:
            parsed = json.loads(str(exc))
            recovery.extend(parsed.get('recovery', []))
        except Exception:
            pass
        if staged_zip and str(staged_zip) and staged_zip.exists():
            recovery.append({'kind': 'staged-package', 'preserved_at': str(staged_zip)})
        if staged_receipt and staged_receipt.exists():
            recovery.append({'kind': 'staged-receipt', 'preserved_at': str(staged_receipt)})
        print(json.dumps({'status': 'fail', 'stage': 'package', 'error': str(exc), 'recovery': recovery}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
