import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_search_candidate_context.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def data():return json.loads((ROOT/'assets/templates/search-candidate-context.json.template').read_text())
def test_template_valid():assert m.validate(data())==[]
def test_missing_policy():d=data();d['evaluation_identity'].pop('policy_id');assert 'evaluation_identity.policy_id:invalid' in m.validate(d)
def test_v1_rejected():d=data();d['context_version']=1;assert 'context_version:unsupported' in m.validate(d)
