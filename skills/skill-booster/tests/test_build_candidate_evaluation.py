import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/build_candidate_evaluation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def contract():
 return {'contract_version':4,'evaluation_identity':{'evaluator_id':'E','scenario_set_id':'S','policy_id':'P'},'allowed_evaluation_levels':['L3-harness','L4-benchmark','L5-holdout'],'hard_gates':['activation','validation'],'objectives':[{'name':'quality'},{'name':'token_cost'}]}
def bench():return {'contract_version':4,'candidates':[{'candidate_id':'C1','candidate_identity':'CID','evaluator_id':'E','scenario_set_id':'S','policy_id':'P','evaluation_level':'L4-benchmark','metrics':{'quality':{'value':.9,'uncertainty':.01},'token_cost':{'value':100,'uncertainty':0}}}]}
def harness():return {'contract_version':4,'runs':[{'candidate_id':'C1','candidate_identity':'CID','evaluator_id':'E','scenario_set_id':'S','evaluation_policy_id':'P','holdout_blind':True,'candidate_saw_evaluator_only_assets':False}]}
def test_build_from_benchmark_and_harness():
 out=m.build(contract(),'C1','CID',bench(),harness(),{'activation':'pass','validation':'pass'});assert out['contract_version']==2;assert out['evaluation']['identity']['policy_id']=='P';assert out['evaluation']['level']=='L4-benchmark'
def test_identity_drift_fails():
 b=bench();b['candidates'][0]['policy_id']='X'
 try:m.build(contract(),'C1','CID',b,None,{'activation':'pass','validation':'pass'})
 except ValueError as exc:assert 'evaluation_identity_mismatch' in str(exc)
 else:assert False


def test_v3_benchmark_evidence_is_rejected_for_evolutionary_bridge():
 b=bench();b['contract_version']=3
 import pytest
 with pytest.raises(ValueError,match='benchmark:unsupported_contract'):
  m.build(contract(),'C1','CID',b,harness(),{'activation':'pass','validation':'pass'})

def test_v3_harness_evidence_is_rejected_for_evolutionary_bridge():
 h=harness();h['contract_version']=3
 import pytest
 with pytest.raises(ValueError,match='harness:unsupported_contract'):
  m.build(contract(),'C1','CID',bench(),h,{'activation':'pass','validation':'pass'})
