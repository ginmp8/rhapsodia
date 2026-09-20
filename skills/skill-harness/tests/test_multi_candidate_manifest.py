import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_multi_candidate_manifest.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(cid,n):return {'candidate_id':cid,'candidate_identity':cid+'hash','run_id':f'R{n}','trace_id':f'T{n}','work_dir':f'/tmp/w{n}','evaluator_id':'E','scenario_set_id':'S','evaluation_policy_id':'P','holdout_blind':True,'candidate_saw_evaluator_only_assets':False}
def test_v2_valid():assert m.validate({'contract_version':2,'runs':[row('C1',1),row('C2',2)]})==[]
def test_shared_workdir():
 d={'contract_version':2,'runs':[row('C1',1),row('C2',2)]};d['runs'][1]['work_dir']=d['runs'][0]['work_dir'];assert 'work_dir:shared' in m.validate(d)
def test_policy_mismatch():
 d={'contract_version':2,'runs':[row('C1',1),row('C2',2)]};d['runs'][1]['evaluation_policy_id']='P2';assert 'comparability:evaluation_policy_id:mismatch' in m.validate(d)
def test_legacy_v1_valid():
 r=row('C1',1);r.pop('trace_id');r.pop('evaluation_policy_id');assert m.validate({'runs':[r]})==[]
