from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SCRIPT=ROOT/'scripts'/'compare_benchmark_arms.py'
E='a'*64; S='b'*64; R='c'*64

def arm(kind:str, conforms:bool, runtime:str=R):
    target={} if kind=='without-skill' else {'target_identity_sha256':('d' if kind=='candidate' else 'e')*64}
    return {'schema_version':3,'evidence_origin':'executed','arm_type':kind,**target,'evaluator_identity_sha256':E,'scenario_suite_sha256':S,'runtime_profile_sha256':runtime,'suite_role':'capability','distribution_profile':'diagnostic-balanced','grader_type':'deterministic','scenarios':[{'id':'A1','category':'should_activate','prompt':'x','expected_activation':True,'trials':[{'trial_id':f't{i}','actual_activation':True,'output_conforms':conforms,'quality_score':5 if conforms else 1,'needs_rework':not conforms,'input_tokens':100+i,'output_tokens':50,'latency_ms':1000,'tool_calls':1,'cost_usd':0.01} for i in range(1,9)]}]}

def run(candidate, **refs):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); cp=td/'c.json'; cp.write_text(json.dumps(candidate)); cmd=[sys.executable,str(SCRIPT),'--candidate',str(cp)]
        for flag,data in refs.items():
            p=td/f'{flag}.json'; p.write_text(json.dumps(data)); cmd += ['--'+flag.replace('_','-'),str(p)]
        r=subprocess.run(cmd,capture_output=True,text=True); return r,json.loads(r.stdout)

def test_v3_strong_claim_uses_uncertainty():
    r,out=run(arm('candidate',True),baseline=arm('baseline',False)); assert r.returncode==0, r.stdout
    m=out['baseline_comparison']['capability_delta']['output_conformance']; assert m['classification']=='improved'; assert m['claim_classification']=='improved'; assert m['confidence_interval_95'] is not None

def test_v2_compatibility_remains_directional_only():
    def v2(kind, conforms):
        target={} if kind=='without-skill' else {'target_identity_sha256':('d' if kind=='candidate' else 'e')*64}
        return {'schema_version':2,'evidence_origin':'executed','arm_type':kind,**target,'evaluator_identity_sha256':E,'scenario_suite_sha256':S,'scenarios':[{'id':'A1','category':'should_activate','prompt':'x','expected_activation':True,'actual_activation':True,'output_conforms':conforms,'quality_score':5,'needs_rework':not conforms}]}
    r,out=run(v2('candidate',True),baseline=v2('baseline',False)); assert r.returncode==0
    m=out['baseline_comparison']['capability_delta']['output_conformance']; assert m['classification']=='improved'; assert m['claim_classification']=='inconclusive'

def test_runtime_drift_blocks_v3_delta():
    r,out=run(arm('candidate',True),baseline=arm('baseline',False,runtime='f'*64)); assert r.returncode==0
    assert out['baseline_comparison']['comparable'] is False; assert 'runtime_profile_sha256' in out['baseline_comparison']['non_comparable_reasons']

def test_length_control_is_separate_arm():
    lc=arm('length-control',False); r,out=run(arm('candidate',True),length_control=lc); assert r.returncode==0
    assert out['length_control_comparison'] is not None; assert out['claim_rules']['context_length_control_source']=='length-control'
