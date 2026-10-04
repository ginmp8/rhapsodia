import json
from pathlib import Path
from scripts.validate_execution_evidence import validate_environment, validate_stochastic

ROOT=Path(__file__).resolve().parents[1]

def test_environment_template_validates_and_hashes():
    data=json.loads((ROOT/'assets/templates/execution-environment.json.template').read_text())
    result=validate_environment(data)
    assert result['status']=='pass', result
    assert len(result['identity_digest'])==64

def test_stochastic_template_uses_paired_validator():
    data=json.loads((ROOT/'assets/templates/paired-trials.json.template').read_text())
    result=validate_stochastic(data)
    assert result['status']=='pass', result
    assert result['runtime_comparable'] is True
