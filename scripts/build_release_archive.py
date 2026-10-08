#!/usr/bin/env python3
"""Build a deterministic full-project RhapsodIA ZIP and print a SHA-256 receipt."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import package_policy


def include(path: Path) -> bool:
    return package_policy.include(path, ROOT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?', args.version):
        parser.error('version must be a bounded SemVer-style identity, not a path')
    if len(args.version) > 100 or args.output.is_symlink():
        parser.error('invalid version length or symbolic-link output')
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    selected = sorted((p for p in package_policy.files(ROOT) if p.resolve() != output), key=lambda p: p.relative_to(ROOT).as_posix())
    descriptor, temporary = tempfile.mkstemp(prefix='.rhapsodia-release-', suffix='.zip', dir=output.parent)
    os.close(descriptor)
    temporary = Path(temporary)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in selected:
                relative = path.relative_to(ROOT).as_posix()
                entry = zipfile.ZipInfo(f'rhapsodia-{args.version}/{relative}', date_time=(1980, 1, 1, 0, 0, 0))
                entry.create_system = 3  # Stable Unix-mode metadata on every host.
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = (0o755 if path.suffix in {'.py', '.sh'} else 0o644) << 16
                archive.writestr(entry, path.read_bytes())
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps({'archive': str(output), 'version': args.version, 'file_count': len(selected),
                      'sha256': sha256(output), 'size': output.stat().st_size}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
