from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'validate_scenario_results.py'


def run(payload: object) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'results.json'
        path.write_text(json.dumps(payload), encoding='utf-8')
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--results', str(path)],
            capture_output=True,
            text=True,
        )


def scenario() -> dict[str, object]:
    return {
        'id': 'A1',
        'category': 'should_activate',
        'prompt': 'Benchmark this skill package.',
        'expected_activation': True,
        'actual_activation': True,
        'output_conforms': True,
        'quality_score': 5,
        'needs_rework': False,
    }


def test_v2_envelope_is_accepted() -> None:
    result = run({'schema_version': 2, 'scenarios': [scenario()]})
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload['checks']['shape'] == 'envelope-v2'


def test_top_level_array_is_rejected() -> None:
    result = run([scenario()])
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert 'versioned v2 object envelope' in payload['errors'][0]


def test_unversioned_object_is_rejected() -> None:
    result = run({'scenarios': [scenario()]})
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert 'schema_version: 2' in payload['errors'][0]
