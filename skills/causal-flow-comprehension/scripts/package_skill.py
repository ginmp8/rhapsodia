#!/usr/bin/env python3
"""Build a deterministic ZIP of an already validated portable skill (Python stdlib).

Excludes runtime caches. Refuses output aliases and overwrites. Validates staged
exact files, checks ZIP CRC and hashes, then writes ZIP + SHA-256 receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from validate_skill import validate

SKIP_DIRS = {'__pycache__', '.git', '.venv', '.pytest_cache'}
SKIP_FILES = {'.DS_Store', 'Thumbs.db'}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_package_file(path: Path) -> bool:
    return not any(s in SKIP_DIRS for s in path.parts) and path.name not in SKIP_FILES and path.suffix not in {'.pyc', '.pyo'}


def package(root: Path, output: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents or output.suffix.lower() != '.zip':
        raise ValueError('Output ZIP must be outside the skill and end in .zip')
    receipt = output.with_name(output.name + '.receipt.json')
    if output.exists() or receipt.exists():
        raise FileExistsError('Refusing to overwrite existing ZIP or receipt (version or path must change)')
    if root == receipt or root in receipt.parents:
        raise ValueError('Receipt destination aliases source tree')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='skill-stage-', dir=output.parent) as tmp:
        tmpdir = Path(tmp)
        staged = tmpdir / root.name
        staged.mkdir()
        for path in sorted(root.rglob('*')):
            relative = path.relative_to(root)
            if not is_package_file(relative):
                continue
            if path.is_symlink():
                raise ValueError(f'Unsafe symbolic link in skill: {relative}')
            if path.is_file():
                target = staged / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        problems = validate(staged)
        if problems:
            raise ValueError('Staged skill failed validation:\n' + '\n'.join(problems))
        ordered_files = sorted(f for f in staged.rglob('*') if f.is_file())
        if not ordered_files:
            raise ValueError('Empty skill archive')
        bundle_tmp = tmpdir / 'candidate.zip'
        manifest = {}
        with zipfile.ZipFile(bundle_tmp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for path in ordered_files:
                arcname = path.relative_to(tmpdir).as_posix()
                raw = path.read_bytes()
                manifest[arcname] = sha256(raw)
                info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(bundle_tmp) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP CRC test failed')
            if set(z.namelist()) != set(manifest):
                raise ValueError('Archive manifest mismatch')
            if any(sha256(z.read(name)) != digest for name, digest in manifest.items()):
                raise ValueError('Archive content identity mismatch')
        bundle_sha = sha256(bundle_tmp.read_bytes())
        receipt_data = {'receipt_version': 1, 'status': 'pass',
                        'skill': root.name, 'version': (staged/'VERSION').read_text().strip(),
                        'zip_sha256': bundle_sha, 'entry_count': len(manifest),
                        'files_sha256': manifest, 'validated': 'staged static package, refs, version, trace; ZIP CRC + entry hashes',
                        'not_run': ['host/runtime activation trials', 'real-repository causal correctness benchmark']}
        receipt_tmp = tmpdir / 'receipt.json'
        receipt_tmp.write_text(json.dumps(receipt_data, indent=2, sort_keys=True) + '\n', encoding='utf8')
        try:
            os.replace(bundle_tmp, output)
            try:
                os.replace(receipt_tmp, receipt)
            except Exception:
                output.unlink(missing_ok=True)
                raise
        except Exception:
            raise
    return {'archive': str(output), 'receipt': str(receipt),
            'sha256': bundle_sha, 'entry_count': len(manifest)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        response = package(args.root, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print('FAIL:', error, file=sys.stderr)
        return 1
    print(json.dumps(response, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
