from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts'/'validate_scenario_results.py'
SHA='a'*64

def payload():
    return {
        'schema_version':3,'evidence_origin':'executed','arm_type':'candidate',
        'target_identity_sha256':'b'*64,'evaluator_identity_sha256':SHA,
        'scenario_suite_sha256':'c'*64,'runtime_profile_sha256':'d'*64,
        'suite_role':'capability','distribution_profile':'diagnostic-balanced','grader_type':'deterministic',
        'scenarios':[{'id':'A1','category':'should_activate','prompt':'Benchmark it','expected_activation':True,
            'trials':[{'trial_id':'t1','actual_activation':True,'output_conforms':True,'quality_score':5,'needs_rework':False,'input_tokens':100},
                      {'trial_id':'t2','actual_activation':True,'output_conforms':True,'quality_score':5,'needs_rework':False,'input_tokens':110}]}]
    }

def run(data):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'r.json'; p.write_text(json.dumps(data))
        return subprocess.run([sys.executable,str(SCRIPT),'--results',str(p)],capture_output=True,text=True)

def test_v3_repeated_trials_are_accepted():
    r=run(payload()); assert r.returncode==0, r.stdout
    out=json.loads(r.stdout); assert out['checks']['shape']=='envelope-v3'; assert out['checks']['trial_row_count']==2

def test_v3_requires_runtime_identity():
    d=payload(); d.pop('runtime_profile_sha256')
    r=run(d); assert r.returncode==1; assert 'runtime_profile_sha256' in r.stdout

def test_model_grader_calibration_shape_is_validated():
    d=payload(); d['grader_type']='llm'; d['grader_calibration']={'status':'pass','calibration_set_sha256':'e'*64,'human_agreement':0.9,'position_balanced':True,'length_controlled':True,'abstention_supported':True}
    r=run(d); assert r.returncode==0, r.stdout
