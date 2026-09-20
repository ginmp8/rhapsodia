import importlib.util,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_candidate_request.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def signature(base,ts):return hashlib.sha256(json.dumps({'base_parent_id':base,'transformation_ids':sorted(ts)},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def data():
 ts=['T1'];return {'request_version':2,'candidate_id':'C2','operator':'bounded-mutation','base_parent_id':'C1','donor_parent_ids':[],'transformation_ids':ts,'expected_capability_effects':['cap.a'],'reason':'bounded experiment','request_signature':signature('C1',ts)}
def test_valid():assert m.validate(data())==[]
def test_v1_rejected():d=data();d['request_version']=1;assert 'request_version:unsupported' in m.validate(d)
def test_bad_signature():d=data();d['request_signature']='x';assert 'request_signature:mismatch' in m.validate(d)
