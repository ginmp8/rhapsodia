#!/usr/bin/env python3
import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v",ROOT/"scripts"/"validate_oracle_artifact.py")
v=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(v)
def spec_doc():
    return {"contract":"test-oracle-spec/v1","oracle_id":"o1","claim":"candidate returns 200","claim_type":"api-contract","source_identity":"spec:x","candidate_identity":"sha256:c","target_scope":["src/**"],"verification_write_scope":["tests/**"],"protected_paths":[],"observable":{"setup":"service running","input":"valid request","action":"POST /x","expected":"200 and durable row","failure_signal":"non-200 or missing row"},"execution":{"layer":"integration-public-stack","mode":"integration","requirements":["run-bounded-process"],"working_directory":".","command_argv":["dotnet","test"]},"evaluator_identity":"criteria:v1","max_attempts":3}
def proof_doc():
    return {"contract":"test-oracle-proof/v1","oracle_id":"o1","oracle_spec_identity":"sha256:s","candidate_identity":"sha256:c","verifier_identity":"verifier:v1","environment_identity":"env:v1","execution_state":"pass","verdict":"proven","command_argv":["dotnet","test"],"exit_code":0,"evidence_refs":["log:1"],"test_artifacts":["tests/X.cs"],"production_mutation_performed":False,"criteria_changed":False}
class Tests(unittest.TestCase):
    def test_valid_spec(self): self.assertEqual(v.validate(spec_doc())["status"],"pass")
    def test_executable_spec_requires_command(self):
        d=spec_doc(); d["execution"]["command_argv"]=[]; self.assertIn("E_COMMAND",{x["code"] for x in v.validate(d)["errors"]})
    def test_valid_proof(self): self.assertEqual(v.validate(proof_doc())["status"],"pass")
    def test_proven_requires_pass(self):
        d=proof_doc(); d["execution_state"]="fail"; self.assertIn("E_VERDICT_STATE",{x["code"] for x in v.validate(d)["errors"]})
    def test_production_mutation_rejected(self):
        d=proof_doc(); d["production_mutation_performed"]=True; self.assertIn("E_PRODUCTION_MUTATION",{x["code"] for x in v.validate(d)["errors"]})
    def test_criteria_drift_rejected(self):
        d=proof_doc(); d["criteria_changed"]=True; self.assertIn("E_CRITERIA_DRIFT",{x["code"] for x in v.validate(d)["errors"]})


class SchemaParityAndProofTruthTests(unittest.TestCase):
    def test_spec_rejects_unexpected_property(self):
        d=spec_doc(); d["unexpected"]=True
        self.assertIn("E_SCHEMA_ADDITIONAL_PROPERTY", {x["code"] for x in v.validate(d)["errors"]})

    def test_spec_rejects_unexpected_nested_property(self):
        d=spec_doc(); d["observable"]["unexpected"]=True
        self.assertIn("E_SCHEMA_ADDITIONAL_PROPERTY", {x["code"] for x in v.validate(d)["errors"]})

    def test_spec_rejects_duplicate_requirements(self):
        d=spec_doc(); d["execution"]["requirements"]=["run-bounded-process","run-bounded-process"]
        self.assertIn("E_DUPLICATE", {x["code"] for x in v.validate(d)["errors"]})

    def test_spec_rejects_empty_working_directory_when_present(self):
        d=spec_doc(); d["execution"]["working_directory"]=""
        self.assertIn("E_WORKING_DIRECTORY", {x["code"] for x in v.validate(d)["errors"]})

    def test_proof_rejects_unexpected_property(self):
        d=proof_doc(); d["unexpected"]=True
        self.assertIn("E_SCHEMA_ADDITIONAL_PROPERTY", {x["code"] for x in v.validate(d)["errors"]})

    def test_proof_rejects_duplicate_evidence(self):
        d=proof_doc(); d["evidence_refs"]=["log:1","log:1"]
        self.assertIn("E_DUPLICATE", {x["code"] for x in v.validate(d)["errors"]})

    def test_proven_pass_requires_zero_exit_code(self):
        d=proof_doc(); d["exit_code"]=7
        self.assertIn("E_EXIT_CODE_STATE", {x["code"] for x in v.validate(d)["errors"]})

    def test_rejected_fail_requires_nonzero_exit_code(self):
        d=proof_doc(); d["execution_state"]="fail"; d["verdict"]="rejected"; d["exit_code"]=0
        self.assertIn("E_EXIT_CODE_STATE", {x["code"] for x in v.validate(d)["errors"]})

    def test_exit_code_rejects_boolean(self):
        d=proof_doc(); d["exit_code"]=True
        self.assertIn("E_EXIT_CODE", {x["code"] for x in v.validate(d)["errors"]})

if __name__=="__main__": unittest.main()
