import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_multi_candidate_manifest.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(cid,n):return {'candidate_id':cid,'candidate_identity':cid+'hash','run_id':f'R{n}','trace_id':f'T{n}','trace_manifest_id':f'TM{n}','trace_manifest_sha256':f'sha256:{n:064x}','work_dir':f'/tmp/w{n}','evaluator_id':'E','scenario_set_id':'S','evaluation_policy_id':'P','holdout_blind':True,'candidate_saw_evaluator_only_assets':False}
def test_v3_valid():assert m.validate({'contract_version':3,'runs':[row('C1',1),row('C2',2)]})==[]
def test_shared_workdir():
 d={'contract_version':3,'runs':[row('C1',1),row('C2',2)]};d['runs'][1]['work_dir']=d['runs'][0]['work_dir'];assert 'work_dir:shared' in m.validate(d)
def test_policy_mismatch():
 d={'contract_version':3,'runs':[row('C1',1),row('C2',2)]};d['runs'][1]['evaluation_policy_id']='P2';assert 'comparability:evaluation_policy_id:mismatch' in m.validate(d)
def test_legacy_v1_valid():
 r=row('C1',1);r.pop('trace_id');r.pop('evaluation_policy_id');assert m.validate({'runs':[r]})==[]


def test_v3_rejects_duplicate_candidate_identity():
 d={'contract_version':3,'runs':[row('C1',1),row('C2',2)]}
 d['runs'][1]['candidate_identity']=d['runs'][0]['candidate_identity']
 assert 'candidate_identity:duplicate' in m.validate(d)

def test_v3_requires_trace_manifest_identity():
 d={'contract_version':3,'runs':[row('C1',1),row('C2',2)]}
 d['runs'][1].pop('trace_manifest_id')
 d['runs'][1].pop('trace_manifest_sha256')
 errors=m.validate(d)
 assert 'run[1].trace_manifest_id:missing' in errors
 assert 'run[1].trace_manifest_sha256:missing' in errors

def test_v3_rejects_shared_trace_manifest_identity():
 d={'contract_version':3,'runs':[row('C1',1),row('C2',2)]}
 d['runs'][1]['trace_manifest_id']=d['runs'][0]['trace_manifest_id']
 d['runs'][1]['trace_manifest_sha256']=d['runs'][0]['trace_manifest_sha256']
 errors=m.validate(d)
 assert 'trace_manifest_id:duplicate' in errors
 assert 'trace_manifest_sha256:duplicate' in errors


def test_v2_legacy_stays_readable_with_old_trace_shape():
 a=row('C1',1);b=row('C2',2)
 for r in (a,b):
  r.pop('trace_manifest_id');r.pop('trace_manifest_sha256')
 b['candidate_identity']=a['candidate_identity']
 errors=m.validate({'contract_version':2,'runs':[a,b]})
 assert 'candidate_identity:duplicate' not in errors
 assert not any('trace_manifest_' in error for error in errors)
