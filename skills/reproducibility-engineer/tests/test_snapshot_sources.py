from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'snapshot_sources.py'


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_capture_then_source_mutation_is_detected() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / 'source'
        work = base / 'work'
        source.mkdir()
        work.mkdir()
        (source / 'input.txt').write_text('alpha\n', encoding='utf-8')
        manifest = work / 'manifest.json'
        snapshot = work / 'bytes'

        captured = run('capture', '--root', str(source), '--path', 'input.txt', '--snapshot-dir', str(snapshot), '--out', str(manifest))
        assert captured.returncode == 0, captured.stderr or captured.stdout
        data = json.loads(manifest.read_text(encoding='utf-8'))
        assert data['file_count'] == 1
        assert (snapshot / 'input.txt').read_text(encoding='utf-8') == 'alpha\n'

        (source / 'input.txt').write_text('beta\n', encoding='utf-8')
        verified = run('verify', '--manifest', str(manifest))
        assert verified.returncode == 1
        report = json.loads(verified.stdout)
        assert report['snapshot_changed'] == []
        assert report['source_changed'][0]['reason'] == 'source-bytes-changed'

        snapshot_only = run('verify', '--manifest', str(manifest), '--snapshot-only')
        assert snapshot_only.returncode == 0
        assert json.loads(snapshot_only.stdout)['status'] == 'pass'


def test_symlink_escape_fails_closed() -> None:
    if not hasattr(os, 'symlink'):
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / 'source'
        work = base / 'work'
        source.mkdir()
        work.mkdir()
        outside = base / 'outside.txt'
        outside.write_text('secret\n', encoding='utf-8')
        link = source / 'escape.txt'
        try:
            link.symlink_to(outside)
        except OSError:
            return
        result = run('capture', '--root', str(source), '--path', 'escape.txt', '--snapshot-dir', str(work / 'bytes'), '--out', str(work / 'manifest.json'))
        assert result.returncode == 1
        report = json.loads(result.stdout)
        assert 'symlink escapes root' in report['error']


if __name__ == '__main__':
    test_capture_then_source_mutation_is_detected()
    test_symlink_escape_fails_closed()
    print('ok')
