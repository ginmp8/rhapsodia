from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'snapshot_target.py'


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def make_skill(path: Path) -> None:
    path.mkdir()
    (path / 'SKILL.md').write_text('---\nname: demo-skill\ndescription: use when asked to demonstrate a deterministic portable benchmark target with explicit output and validation guidance. do not use for unrelated tasks.\n---\n\n# Demo\n\n## Output contract\nReturn a deterministic report.\n', encoding='utf-8')


def test_source_drift_is_detected_without_corrupting_snapshot() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / 'demo-skill'
        snapshot = base / 'snapshot'
        manifest = base / 'manifest.json'
        make_skill(source)
        captured = run('capture', '--target', str(source), '--snapshot-dir', str(snapshot), '--out', str(manifest))
        assert captured.returncode == 0, captured.stderr or captured.stdout
        original = (snapshot / 'SKILL.md').read_bytes()
        (source / 'SKILL.md').write_text((source / 'SKILL.md').read_text() + '\nchanged\n', encoding='utf-8')
        verified = run('verify', '--manifest', str(manifest))
        assert verified.returncode == 1
        report = json.loads(verified.stdout)
        assert report['source_errors']
        assert (snapshot / 'SKILL.md').read_bytes() == original
        snapshot_only = run('verify', '--manifest', str(manifest), '--snapshot-only')
        assert snapshot_only.returncode == 0


if __name__ == '__main__':
    test_source_drift_is_detected_without_corrupting_snapshot()
    print('ok')
