from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from validate_benchmark_health import validate
SHA='a'*64

def healthy():
    return {'schema_version':1,'scenario_suite_sha256':SHA,'suite_role':'capability','distribution_profile':'diagnostic-balanced','distribution_evidence_status':'not-run','isolation_status':'pass','gaming_resistance':'pass','contamination_risk':'low','saturation_state':'active','grader':{'type':'deterministic','correctness_status':'pass','calibration_status':'not-run'},'tasks':[{'id':'A1','reference_solution_status':'pass','grader_status':'pass','ambiguity_status':'pass','flakiness_rate':0.0}]}

def test_healthy_suite_passes_health_gate():
    r=validate(healthy()); assert r['status']=='pass'; assert r['gate']=='pass'; assert r['strong_claim_eligible'] is True

def test_broken_reference_fails_health_gate():
    d=healthy(); d['tasks'][0]['reference_solution_status']='fail'
    r=validate(d); assert r['gate']=='fail'; assert r['strong_claim_eligible'] is False

def test_unknown_contamination_requires_review():
    d=healthy(); d['contamination_risk']='unknown'
    assert validate(d)['gate']=='review'
