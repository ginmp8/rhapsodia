from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'scripts' / 'validate_skill_evolution.py'


def run_validator(target: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), '--target', str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, json.loads(proc.stdout)


def copy_skill(tmp_path: Path) -> Path:
    target = tmp_path / 'skill-evolution'
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
    return target


def test_package_validator_requires_integration_manifest(tmp_path):
    target = copy_skill(tmp_path)
    (target / 'contracts' / 'integration-manifest.json').unlink()
    code, report = run_validator(target)
    assert code == 2
    assert 'missing:contracts/integration-manifest.json' in report['errors']


def test_package_validator_requires_candidate_evaluation_surface(tmp_path):
    target = copy_skill(tmp_path)
    (target / 'assets' / 'templates' / 'candidate-evaluation.json.template').unlink()
    (target / 'scripts' / 'validate_candidate_evaluation.py').unlink()
    code, report = run_validator(target)
    assert code == 2
    assert 'missing:assets/templates/candidate-evaluation.json.template' in report['errors']
    assert 'missing:scripts/validate_candidate_evaluation.py' in report['errors']


def test_package_validator_rejects_semantically_invalid_integration_manifest(tmp_path):
    target = copy_skill(tmp_path)
    manifest = target / 'contracts' / 'integration-manifest.json'
    payload = json.loads(manifest.read_text(encoding='utf-8'))
    payload['exports'] = []
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    code, report = run_validator(target)
    assert code == 2
    assert any(error.startswith('integration-manifest:') for error in report['errors'])


def test_package_validator_rejects_wrong_manifest_identity(tmp_path):
    target = copy_skill(tmp_path)
    manifest = target / 'contracts' / 'integration-manifest.json'
    payload = json.loads(manifest.read_text(encoding='utf-8'))
    payload['manifest_version'] = 99
    payload['skill'] = 'wrong-skill'
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    code, report = run_validator(target)
    assert code == 2
    assert 'integration-manifest:manifest_version' in report['errors']
    assert 'integration-manifest:skill' in report['errors']


def test_package_validator_rejects_missing_declared_surface(tmp_path):
    target = copy_skill(tmp_path)
    manifest = target / 'contracts' / 'integration-manifest.json'
    payload = json.loads(manifest.read_text(encoding='utf-8'))
    payload['exports'][0]['surface_paths'].append('missing/public-surface.json')
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    code, report = run_validator(target)
    assert code == 2
    assert any('missing_surface:missing/public-surface.json' in error for error in report['errors'])


def test_package_validator_requires_generation_receipt_v3_import_when_missing(tmp_path):
    target = copy_skill(tmp_path)
    manifest = target / 'contracts' / 'integration-manifest.json'
    payload = json.loads(manifest.read_text(encoding='utf-8'))
    payload['imports'] = []
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    code, report = run_validator(target)
    assert code == 2
    assert 'integration-manifest:import:skill-opt.candidate-generation-receipt:v3' in report['errors']

def test_package_validator_requires_generation_receipt_v3_import(tmp_path):
    root = copy_skill(tmp_path)
    path = root / 'contracts/integration-manifest.json'
    manifest = json.loads(path.read_text())
    imp = next(x for x in manifest['imports'] if x.get('contract_id') == 'skill-opt.candidate-generation-receipt')
    imp['accepted_versions'] = [2]
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    code, report = run_validator(root)
    assert code != 0
    assert 'integration-manifest:import:skill-opt.candidate-generation-receipt:v3' in report['errors']


def test_package_validator_allows_missing_openai_adapter(tmp_path):
    target = copy_skill(tmp_path)
    (target / 'agents' / 'openai.yaml').unlink()
    code, report = run_validator(target)
    assert code == 0
    assert report['status'] == 'pass'
