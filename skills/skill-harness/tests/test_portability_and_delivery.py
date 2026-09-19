from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'scripts' / 'skill_harness_portability.py'
PACKAGE = ROOT / 'scripts' / 'skill_harness_package.py'


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)


def make_skill(base: Path, name: str = 'demo-skill') -> Path:
    skill = base / name
    skill.mkdir()
    (skill / 'SKILL.md').write_text(
        f'---\nname: {name}\ndescription: Validate and package this existing demo skill. Use when testing harness delivery behavior. Do not use for unrelated tasks.\n---\n\n# Demo\n',
        encoding='utf-8',
    )
    (skill / 'evals').mkdir()
    scenarios = {
        'status': 'planned',
        'scenarios': [
            {'id':'a','type':'should_activate','prompt':'x','expected_behavior':'x','acceptance_criteria':['x']},
            {'id':'n','type':'should_not_activate','prompt':'x','expected_behavior':'x','acceptance_criteria':['x']},
            {'id':'m','type':'ambiguous','prompt':'x','expected_behavior':'x','acceptance_criteria':['x']},
            {'id':'e','type':'edge_case','prompt':'x','expected_behavior':'x','acceptance_criteria':['x']},
        ],
    }
    (skill / 'evals' / 'scenarios.json').write_text(json.dumps(scenarios), encoding='utf-8')
    return skill


def test_portable_core_name_matches_directory() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = make_skill(Path(td))
        proc = run(PORT, '--target', str(skill), '--profile', 'portable')
        assert proc.returncode == 0, proc.stderr or proc.stdout
        report = json.loads(proc.stdout)
        assert report['portable_core_pass'] is True


def test_package_report_alias_preserves_last_good() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / 'skill.zip'
        report = base / 'report.json'
        output.write_bytes(b'last-good')
        try:
            os.link(output, report)
        except OSError:
            return
        before = output.read_bytes()
        proc = run(PACKAGE, '--target', str(skill), '--output', str(output), '--report', str(report), '--strict')
        assert proc.returncode == 1
        failure = json.loads(proc.stdout)
        assert failure['code'] == 'output/target-alias'
        assert output.read_bytes() == before
        assert report.read_bytes() == before


def test_success_archive_has_canonical_skill_root_and_matching_receipt() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / 'skill.zip'
        report = base / 'report.json'
        proc = run(PACKAGE, '--target', str(skill), '--output', str(output), '--report', str(report), '--profile', 'portable')
        assert proc.returncode == 0, proc.stderr or proc.stdout
        receipt = json.loads(report.read_text(encoding='utf-8'))
        assert receipt['status'] == 'pass'
        assert receipt['stage'] == 'committed'
        assert hashlib.sha256(output.read_bytes()).hexdigest() == receipt['package_sha256']
        with zipfile.ZipFile(output, 'r') as zf:
            assert zf.testzip() is None
            assert all(name.startswith('demo-skill/') for name in zf.namelist())
            assert 'demo-skill/SKILL.md' in zf.namelist()


if __name__ == '__main__':
    test_portable_core_name_matches_directory()
    test_package_report_alias_preserves_last_good()
    test_success_archive_has_canonical_skill_root_and_matching_receipt()
    print('ok')
