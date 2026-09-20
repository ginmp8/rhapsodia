import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_generation_receipt.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def data():return json.loads((ROOT/'assets/templates/generation-receipt.json.template').read_text())
def test_template_valid():assert m.validate(data())==[]
def test_v1_rejected():d=data();d['receipt_version']=1;assert 'receipt_version:unsupported' in m.validate(d)

def test_v3_is_current_contract():
    assert data()['receipt_version'] == 3

def test_rejects_tampered_request_signature():
    d=data();d['request_signature']='tampered-but-nonempty'
    assert 'request_signature:mismatch' in m.validate(d)

def test_rejects_candidate_as_base_parent():
    d=data();d['candidate_id']=d['base_parent_id']
    assert 'candidate:self_parent' in m.validate(d)

def test_rejects_base_parent_as_donor_parent():
    d=data();d['donor_parent_ids']=[d['base_parent_id']]
    assert 'donor_parent_ids:contains_base' in m.validate(d)
