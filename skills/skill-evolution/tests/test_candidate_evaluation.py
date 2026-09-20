import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_candidate_evaluation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def contract():return json.loads((ROOT/'assets/templates/search-contract.json.template').read_text())
def envelope():return json.loads((ROOT/'assets/templates/candidate-evaluation.json.template').read_text())
def test_template_passes():assert m.validate(contract(),envelope())==[]
def test_policy_drift_fails():
 e=envelope();e['evaluation']['identity']['policy_id']='other';assert 'identity:mismatch' in m.validate(contract(),e)
def test_missing_metric_fails():
 e=envelope();del e['evaluation']['metrics']['quality'];assert 'metrics:set_mismatch' in m.validate(contract(),e)
