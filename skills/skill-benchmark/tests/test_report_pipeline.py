from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / 'scripts' / 'snapshot_target.py'
GEN = ROOT / 'scripts' / 'generate_benchmark_report.py'
VALIDATE = ROOT / 'scripts' / 'validate_benchmark_report.py'


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)


def make_skill(path: Path) -> None:
    path.mkdir()
    (path / 'SKILL.md').write_text('''---
name: demo-skill
description: use when asked to convert a provided deterministic demo input into a small report with explicit validation. do not use for unrelated writing or code tasks.
---

# Demo Skill

## Purpose
Produce one repeatable demo report.

## Workflow
1. Read the target input.
2. Validate required fields.
3. Produce the report.

## Output contract
Return a Markdown report with evidence and validation status.

## Stop conditions
Stop if required input is missing or validation fails.
''', encoding='utf-8')


def test_frozen_report_contains_identity_and_validates() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / 'demo-skill'
        snapshot = base / 'snapshot'
        manifest = base / 'manifest.json'
        out = base / 'reports'
        make_skill(source)
        assert run(SNAP, 'capture', '--target', str(source), '--snapshot-dir', str(snapshot), '--out', str(manifest)).returncode == 0
        generated = run(GEN, '--target', str(snapshot), '--source-manifest', str(manifest), '--out', str(out), '--hosts', 'all')
        assert generated.returncode == 0, generated.stderr or generated.stdout
        receipt = json.loads(generated.stdout)
        report = Path(receipt['report_path'])
        assert report.is_file()
        text = report.read_text(encoding='utf-8')
        assert receipt['target_identity_sha256'] in text
        assert receipt['evaluator_identity_sha256'] in text
        validated = run(VALIDATE, '--report', str(report))
        assert validated.returncode == 0, validated.stderr or validated.stdout
        result = json.loads(validated.stdout)
        assert result['checks']['source_evidence_state'] == 'frozen-snapshot'


def test_output_inside_target_fails_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / 'demo-skill'
        make_skill(source)
        marker = source / 'marker.txt'
        marker.write_text('keep', encoding='utf-8')
        result = run(GEN, '--target', str(source), '--out', str(source / 'reports'))
        assert result.returncode == 1
        assert marker.read_text(encoding='utf-8') == 'keep'
        failure = json.loads(result.stdout)
        assert failure['last_good_preserved_on_failure'] is True


if __name__ == '__main__':
    test_frozen_report_contains_identity_and_validates()
    test_output_inside_target_fails_without_mutation()
    print('ok')
