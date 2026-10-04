from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from validate_skill_coverage import validate
SHA='a'*64

def test_coverage_and_adherence_are_separate():
    d={'schema_version':1,'skill_identity_sha256':SHA,'constraint_set_sha256':'b'*64,
       'constraints':[{'id':'C1','source':'s1','condition':'always','expected_behavior':'b1'},{'id':'C2','source':'s2','condition':'always','expected_behavior':'b2'},{'id':'C3','source':'s3','condition':'always','expected_behavior':'b3'}],
       'results':[{'constraint_id':'C1','status':'covered_pass'},{'constraint_id':'C2','status':'covered_fail'},{'constraint_id':'C3','status':'uncovered'}]}
    r=validate(d); assert r['status']=='pass'; assert r['metrics']['coverage']==2/3; assert r['metrics']['covered_adherence']==0.5

def test_every_constraint_requires_one_result():
    d={'schema_version':1,'skill_identity_sha256':SHA,'constraint_set_sha256':'b'*64,'constraints':[{'id':'C1','source':'s','condition':'always','expected_behavior':'b'}],'results':[]}
    r=validate(d); assert r['status']=='fail'; assert 'missing results' in ' '.join(r['errors'])
