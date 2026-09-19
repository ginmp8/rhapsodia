#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

EXCLUDE_PARTS = {'__pycache__', '.git', '.pytest_cache', '.mypy_cache'}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo'}
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def include(path: Path) -> bool:
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name == 'skill.zip' or path.name.endswith('.receipt.json'):
        return False
    return True


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_preflight(root: Path, output: Path, receipt: Path) -> None:
    root_real = root.resolve()
    output_real = output.resolve(strict=False)
    receipt_real = receipt.resolve(strict=False)
    if output.suffix.lower() != '.zip':
        raise ValueError('output must end with .zip')
    if output_real == receipt_real:
        raise ValueError('output and receipt must be different paths')
    for candidate, label in [(output_real, 'output'), (receipt_real, 'receipt')]:
        try:
            candidate.relative_to(root_real)
        except ValueError:
            pass
        else:
            raise ValueError(f'{label} must be outside the target skill root')


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def deterministic_zip(root: Path, out: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in root.rglob('*') if p.is_file()):
            rel = path.relative_to(root)
            if not include(rel):
                continue
            arcname = (Path(root.name) / rel).as_posix()
            data = path.read_bytes()
            info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIME)
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)
            entries.append({'path': rel.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', default='.')
    parser.add_argument('--output', required=True)
    parser.add_argument('--receipt')
    args = parser.parse_args()

    root = Path(args.target).resolve()
    output = Path(args.output).resolve(strict=False)
    receipt = Path(args.receipt).resolve(strict=False) if args.receipt else output.with_name(output.name + '.receipt.json')

    try:
        canonical_preflight(root, output, receipt)
    except Exception as exc:
        print(f'PRECHECK_FAIL: {exc}', file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='streamlit-skill-package-') as tmpdir:
        tmp = Path(tmpdir)
        validation_receipt = tmp / 'validation.json'
        subprocess.check_call([
            sys.executable,
            str(root / 'scripts' / 'validate_streamlit_skill.py'),
            str(root),
            '--json',
            str(validation_receipt),
        ])
        staged_zip = tmp / 'skill.zip'
        entries = deterministic_zip(root, staged_zip)
        package_sha = sha256_file(staged_zip)
        validation_sha = sha256_file(validation_receipt)
        staged_receipt = tmp / 'package-receipt.json'
        package_receipt = {
            'receipt_version': 1,
            'status': 'pass',
            'stage': 'packaging',
            'target': str(root),
            'output': str(output),
            'receipt': str(receipt),
            'hashes': {
                'package_sha256': package_sha,
                'validation_receipt_sha256': validation_sha,
            },
            'metrics': {
                'file_count': len(entries),
                'package_bytes': staged_zip.stat().st_size,
            },
            'files': entries,
            'recovery': [],
        }
        write_json(staged_receipt, package_receipt)

        output_backup = output.with_name(f'.{output.name}.last-good')
        receipt_backup = receipt.with_name(f'.{receipt.name}.last-good')
        recovery: list[str] = []
        try:
            if output.exists():
                if output_backup.exists():
                    output_backup.unlink()
                os.replace(output, output_backup)
            if receipt.exists():
                if receipt_backup.exists():
                    receipt_backup.unlink()
                os.replace(receipt, receipt_backup)
            os.replace(staged_zip, output)
            try:
                os.replace(staged_receipt, receipt)
            except Exception:
                if output.exists():
                    output.unlink()
                if output_backup.exists():
                    os.replace(output_backup, output)
                raise
            if output_backup.exists():
                output_backup.unlink()
            if receipt_backup.exists():
                receipt_backup.unlink()
        except Exception as exc:
            if output_backup.exists():
                recovery.append(str(output_backup))
            if receipt_backup.exists():
                recovery.append(str(receipt_backup))
            print(f'COMMIT_FAIL: {exc}', file=sys.stderr)
            if recovery:
                print('RECOVERY: ' + ', '.join(recovery), file=sys.stderr)
            return 3

    print(output)
    print(receipt)
    print(package_sha)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
