import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_candidate_set.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(cid):return {'candidate_id':cid,'candidate_identity':cid+'hash','parent_id':'B','baseline_id':'Bhash','evaluator_id':'E','scenario_set_id':'S','policy_id':'P','evaluation_level':'L4-benchmark','metrics':{'q':{'value':1,'uncertainty':0.1}}}
def test_v3_valid():assert m.validate({'contract_version':3,'candidates':[row('C1'),row('C2')]})==[]
def test_evaluator_mismatch():
 d={'contract_version':3,'candidates':[row('C1'),row('C2')]};d['candidates'][1]['evaluator_id']='E2';assert 'comparability:evaluator_id:mismatch' in m.validate(d)
def test_policy_mismatch():
 d={'contract_version':3,'candidates':[row('C1'),row('C2')]};d['candidates'][1]['policy_id']='P2';assert 'comparability:policy_id:mismatch' in m.validate(d)
def test_legacy_v1_still_valid():assert m.validate({'candidates':[{'candidate_id':'C1','baseline_id':'B','evaluator_id':'E','scenario_set_id':'S','metrics':{'q':1}}]})==[]

def test_v3_rejects_empty_metrics():
 d={'contract_version':3,'candidates':[row('C1'),row('C2')]}
 d['candidates'][0]['metrics']={};d['candidates'][1]['metrics']={}
 errors=m.validate(d)
 assert 'candidate[0].metrics:empty' in errors
 assert 'candidate[1].metrics:empty' in errors

def test_v3_rejects_mismatched_metric_sets():
 d={'contract_version':3,'candidates':[row('C1'),row('C2')]}
 d['candidates'][0]['metrics']={'quality':{'value':1,'uncertainty':0.1}}
 d['candidates'][1]['metrics']={'token_cost':{'value':10,'uncertainty':0}}
 assert 'comparability:metrics:mismatch' in m.validate(d)


def test_v2_legacy_stays_readable_without_strict_metric_set():
 d={'contract_version':2,'candidates':[row('C1'),row('C2')]}
 d['candidates'][0]['metrics']={}
 d['candidates'][1]['metrics']={'other':1}
 errors=m.validate(d)
 assert 'candidate[0].metrics:empty' not in errors
 assert 'comparability:metrics:mismatch' not in errors

def test_v2_legacy_preserves_metric_shape_validation():
 d={'contract_version':2,'candidates':[row('C1')]}
 d['candidates'][0]['metrics']={'quality':{'value':'not-a-number','uncertainty':0.1}}
 assert 'candidate[0].metrics.quality.value:invalid' in m.validate(d)

def test_v2_legacy_l1_allows_empty_metrics():
 d={'contract_version':2,'candidates':[row('C1'),row('C2')]}
 for candidate in d['candidates']:
  candidate['evaluation_level']='L1-deterministic'
  candidate['metrics']={}
 assert m.validate(d)==[]
