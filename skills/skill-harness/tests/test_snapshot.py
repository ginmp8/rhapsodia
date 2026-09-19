from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / 'scripts' / 'skill_harness_snapshot.py'


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SNAP), *args], capture_output=True, text=True)


def test_snapshot_is_immutable_and_live_target_change_is_detected() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = base / 'demo-skill'
        skill.mkdir()
        file = skill / 'SKILL.md'
        file.write_text('---\nname: demo-skill\ndescription: x\n---\n', encoding='utf-8')
        snap = base / 'snapshot'
        manifest = base / 'manifest.json'
        proc = run('capture', '--target', str(skill), '--snapshot-dir', str(snap), '--manifest', str(manifest))
        assert proc.returncode == 0, proc.stderr or proc.stdout
        original = (snap / 'SKILL.md').read_bytes()
        file.write_text('---\nname: demo-skill\ndescription: changed\n---\n', encoding='utf-8')
        check_snapshot = run('verify', '--manifest', str(manifest), '--snapshot-only')
        assert check_snapshot.returncode == 0
        assert (snap / 'SKILL.md').read_bytes() == original
        check_live = run('verify', '--manifest', str(manifest))
        assert check_live.returncode == 1
        assert json.loads(check_live.stdout)['source_match'] is False


if __name__ == '__main__':
    test_snapshot_is_immutable_and_live_target_change_is_detected()
    print('ok')
