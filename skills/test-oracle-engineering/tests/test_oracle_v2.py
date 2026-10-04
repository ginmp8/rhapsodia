#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v",ROOT/"scripts"/"validate_oracle_artifact.py")
v=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(v)

def spec_doc():
    return {
        "contract":"test-oracle-spec/v2","oracle_id":"o2","claim":"duplicate delivery has one effect","claim_type":"idempotency",
        "source_identity":"declared:req","candidate_identity":"sha256:"+"a"*64,
        "target_scope":["src/**"],"verification_write_scope":["tests/**"],"protected_paths":[],
        "oracle_strategy":{"type":"property","rationale":"idempotency invariant","property":"effect_count == 1","assumptions":[],"blind_spots":[]},
        "oracle_origin":{"type":"specification","generator_identity":"declared:author","independent_validation":"req"},
        "quality":{"soundness_assumptions":[],"completeness_limits":[],"strength_check":"not-required","strength_rationale":"direct durable effect"},
        "observable":{"setup":"empty","input":"two deliveries","action":"run concurrently","expected":"one effect","failure_signal":"effect count != 1"},
        "execution":{"layer":"integration-public-stack","mode":"integration","requirements":["run-bounded-process"],"working_directory":".","command_argv":["python3","tests/case.py"]},
        "nondeterminism":{"mode":"controlled","repetitions":2,"seed_policy":"recorded","order_policy":"systematic","clock_policy":"controlled","scheduler_policy":"systematic"},
        "evaluator_identity":"declared:evaluator","max_attempts":3
    }

def proof_doc(spec_identity=None):
    return {
        "contract":"test-oracle-proof/v2","oracle_id":"o2","oracle_spec_identity":spec_identity or "sha256:"+"c"*64,
        "candidate_identity":"sha256:"+"a"*64,"verifier_identity":"declared:verifier","environment_identity":"declared:env",
        "attempt":2,"execution_state":"pass","outcome_kind":"expected-observation","verdict":"proven","command_argv":["python3","tests/case.py"],"exit_code":0,
        "observation":{"expected_observed":True,"failure_observed":False,"summary":"one effect","evidence_refs":["log:2"]},
        "attempts":[{"attempt":1,"execution_state":"pass","outcome_kind":"expected-observation","exit_code":0},{"attempt":2,"execution_state":"pass","outcome_kind":"expected-observation","exit_code":0}],
        "evidence_refs":["log:1","log:2"],"test_artifacts":["tests/case.py"],"production_mutation_performed":False,"criteria_changed":False
    }

class V2ContractTests(unittest.TestCase):
    def test_v2_spec_valid(self): self.assertEqual(v.validate(spec_doc())["status"],"pass")
    def test_v2_proof_valid(self): self.assertEqual(v.validate(proof_doc())["status"],"pass")
    def test_llm_origin_requires_independent_validation(self):
        d=spec_doc(); d["oracle_origin"]={"type":"llm-assisted","generator_identity":"declared:model","independent_validation":""}
        self.assertIn("E_ORACLE_ORIGIN_VALIDATION",{x["code"] for x in v.validate(d)["errors"]})
    def test_metamorphic_requires_relation(self):
        d=spec_doc(); d["oracle_strategy"]={"type":"metamorphic","rationale":"r","assumptions":[],"blind_spots":[]}
        self.assertIn("E_STRATEGY_DETAIL",{x["code"] for x in v.validate(d)["errors"]})
    def test_differential_requires_references_and_rule(self):
        d=spec_doc(); d["oracle_strategy"]={"type":"differential","rationale":"r","assumptions":[],"blind_spots":[]}
        codes={x["code"] for x in v.validate(d)["errors"]}; self.assertIn("E_STRATEGY_DETAIL",codes)
    def test_harness_error_cannot_reject(self):
        d=proof_doc(); d.update({"execution_state":"fail","outcome_kind":"harness-error","verdict":"rejected","exit_code":2}); d["observation"]={"expected_observed":False,"failure_observed":False,"summary":"runner crash","evidence_refs":["stderr:1"]}; d["attempts"]=[{"attempt":1,"execution_state":"fail","outcome_kind":"harness-error","exit_code":2}]; d["attempt"]=1
        self.assertIn("E_OUTCOME_VERDICT",{x["code"] for x in v.validate(d)["errors"]})
    def test_unstable_cannot_prove(self):
        d=proof_doc(); d["outcome_kind"]="unstable-observation"; d["verdict"]="proven"
        self.assertIn("E_OUTCOME_VERDICT",{x["code"] for x in v.validate(d)["errors"]})

class CrossVerifierTests(unittest.TestCase):
    def run_verify(self,s,p,candidate=None):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); sp=td/"s.json"; pp=td/"p.json"; rp=td/"r.json"
            sp.write_text(json.dumps(s),encoding="utf-8")
            p=json.loads(json.dumps(p)); p["oracle_spec_identity"]="sha256:"+hashlib.sha256(json.dumps(s,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest(); pp.write_text(json.dumps(p),encoding="utf-8")
            cmd=[sys.executable,str(ROOT/"scripts"/"verify_oracle_proof.py"),"--spec",str(sp),"--proof",str(pp),"--candidate-identity",candidate or s["candidate_identity"],"--json",str(rp)]
            proc=subprocess.run(cmd,text=True,capture_output=True); report=json.loads(rp.read_text(encoding="utf-8")); return proc,report
    def test_bound_proof_passes(self):
        proc,r=self.run_verify(spec_doc(),proof_doc()); self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr); self.assertEqual(r["status"],"pass")
    def test_candidate_mismatch_fails(self):
        proc,r=self.run_verify(spec_doc(),proof_doc(),"sha256:"+"d"*64); self.assertNotEqual(proc.returncode,0); self.assertIn("E_CANDIDATE_IDENTITY",{x["code"] for x in r["errors"]})
    def test_command_drift_fails(self):
        p=proof_doc(); p["command_argv"]=["python3","other.py"]; proc,r=self.run_verify(spec_doc(),p); self.assertNotEqual(proc.returncode,0); self.assertIn("E_COMMAND_DRIFT",{x["code"] for x in r["errors"]})
    def test_mixed_semantic_outcomes_fail_strong_proof(self):
        p=proof_doc(); p["attempts"][0]={"attempt":1,"execution_state":"fail","outcome_kind":"oracle-rejection","exit_code":1}; proc,r=self.run_verify(spec_doc(),p); self.assertNotEqual(proc.returncode,0); self.assertIn("E_UNSTABLE_OBSERVATION",{x["code"] for x in r["errors"]})

if __name__=="__main__": unittest.main()
