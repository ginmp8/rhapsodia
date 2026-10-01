#!/usr/bin/env python3
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_workflow_plan.py"

spec = importlib.util.spec_from_file_location("workflow_validator", VALIDATOR)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def valid_plan():
    return {
        "contract": "workflow-plan/v1",
        "workflow_id": "wf-1",
        "objective": "Inspect independent repository areas and synthesize findings.",
        "success_criteria": ["all required findings synthesized"],
        "strategy": "fan-out-synthesize",
        "authority": {
            "owner": "mago",
            "allowed_effects": ["read-only"],
            "forbidden_effects": ["mutating", "external-side-effect"],
            "write_scope": [],
        },
        "stages": [
            {
                "id": "a",
                "mode": "parallel",
                "work_source": "context-map:unit-a",
                "depends_on": [],
                "max_parallel": 2,
                "isolation": "fresh-context",
                "effects": "read-only",
                "read_set": ["src/a/**"],
                "write_set": [],
                "success": "finding returned",
                "on_failure": "continue-independent",
            },
            {
                "id": "b",
                "mode": "parallel",
                "work_source": "context-map:unit-b",
                "depends_on": [],
                "max_parallel": 2,
                "isolation": "fresh-context",
                "effects": "read-only",
                "read_set": ["src/b/**"],
                "write_set": [],
                "success": "finding returned",
                "on_failure": "continue-independent",
            },
            {
                "id": "synth",
                "mode": "synthesize",
                "work_source": "stage-results:a,b",
                "depends_on": ["a", "b"],
                "max_parallel": 1,
                "isolation": "serial",
                "effects": "read-only",
                "read_set": ["result:a", "result:b"],
                "write_set": [],
                "success": "synthesis complete",
                "on_failure": "stop",
            },
        ],
        "budgets": {
            "max_workers": 3,
            "max_parallel": 2,
            "max_retries_per_unit": 1,
            "max_reentries": 1,
        },
        "termination": {
            "success_predicate": "synthesis complete",
            "terminal_states": ["completed", "blocked", "escalated", "failed", "budget_exhausted"],
        },
        "capabilities": {
            "required": ["read-context"],
            "optional": ["parallelize-independent-work"],
            "degradation": {"parallelize-independent-work": "serial"},
        },
        "evidence": {
            "input_identity": "sha256:input",
            "planner_identity": "planner:v1",
            "evaluator_identity": "criteria:v1",
        },
    }


def codes(report):
    return {x["code"] for x in report["errors"]}


class WorkflowPlanValidatorTests(unittest.TestCase):
    def test_valid_plan_passes_and_hash_is_stable(self):
        plan = valid_plan()
        a = mod.validate(plan)
        b = mod.validate(copy.deepcopy(plan))
        self.assertEqual(a["status"], "pass", a)
        self.assertEqual(a["plan_sha256"], b["plan_sha256"])
        self.assertEqual(len(a["plan_sha256"]), 64)

    def test_missing_evidence_is_rejected(self):
        plan = valid_plan()
        del plan["evidence"]
        report = mod.validate(plan)
        self.assertEqual(report["status"], "fail")
        self.assertIn("E_EVIDENCE", codes(report))

    def test_missing_work_source_is_rejected(self):
        plan = valid_plan()
        plan["stages"][0].pop("work_source")
        report = mod.validate(plan)
        self.assertIn("E_WORK_SOURCE", codes(report))

    def test_stage_parallelism_cannot_exceed_global(self):
        plan = valid_plan()
        plan["stages"][0]["max_parallel"] = 99
        report = mod.validate(plan)
        self.assertIn("E_STAGE_PARALLEL", codes(report))

    def test_read_only_stage_cannot_write(self):
        plan = valid_plan()
        plan["stages"][0]["write_set"] = ["src/a/file.cs"]
        report = mod.validate(plan)
        self.assertIn("E_READONLY_WRITE", codes(report))

    def test_mutation_requires_authority(self):
        plan = valid_plan()
        stage = plan["stages"][0]
        stage["effects"] = "mutating"
        stage["write_set"] = ["src/a/file.cs"]
        report = mod.validate(plan)
        self.assertIn("E_AUTHORITY_EXPANSION", codes(report))

    def test_mutation_outside_write_scope_is_rejected(self):
        plan = valid_plan()
        plan["authority"]["allowed_effects"] = ["read-only", "mutating"]
        plan["authority"]["forbidden_effects"] = ["external-side-effect"]
        plan["authority"]["write_scope"] = ["src/allowed/**"]
        stage = plan["stages"][0]
        stage["effects"] = "mutating"
        stage["write_set"] = ["src/other/file.cs"]
        report = mod.validate(plan)
        self.assertIn("E_WRITE_SCOPE", codes(report))

    def test_unordered_write_write_overlap_is_rejected(self):
        plan = valid_plan()
        plan["authority"]["allowed_effects"] = ["read-only", "mutating"]
        plan["authority"]["forbidden_effects"] = ["external-side-effect"]
        plan["authority"]["write_scope"] = ["src/shared/**"]
        for stage in plan["stages"][:2]:
            stage["effects"] = "mutating"
            stage["read_set"] = []
            stage["write_set"] = ["src/shared/file.cs"]
        report = mod.validate(plan)
        self.assertIn("E_PARALLEL_CONFLICT", codes(report))

    def test_unordered_write_read_overlap_is_rejected(self):
        plan = valid_plan()
        plan["authority"]["allowed_effects"] = ["read-only", "mutating"]
        plan["authority"]["forbidden_effects"] = ["external-side-effect"]
        plan["authority"]["write_scope"] = ["src/shared/**"]
        plan["stages"][0]["effects"] = "mutating"
        plan["stages"][0]["read_set"] = []
        plan["stages"][0]["write_set"] = ["src/shared/**"]
        plan["stages"][1]["read_set"] = ["src/shared/file.cs"]
        report = mod.validate(plan)
        self.assertIn("E_PARALLEL_CONFLICT", codes(report))

    def test_dependency_serializes_conflicting_resources(self):
        plan = valid_plan()
        plan["authority"]["allowed_effects"] = ["read-only", "mutating"]
        plan["authority"]["forbidden_effects"] = ["external-side-effect"]
        plan["authority"]["write_scope"] = ["src/shared/**"]
        plan["stages"][0]["effects"] = "mutating"
        plan["stages"][0]["read_set"] = []
        plan["stages"][0]["write_set"] = ["src/shared/file.cs"]
        plan["stages"][1]["read_set"] = ["src/shared/file.cs"]
        plan["stages"][1]["depends_on"] = ["a"]
        report = mod.validate(plan)
        self.assertNotIn("E_PARALLEL_CONFLICT", codes(report))

    def test_dependency_cycle_is_rejected(self):
        plan = valid_plan()
        plan["stages"][0]["depends_on"] = ["b"]
        plan["stages"][1]["depends_on"] = ["a"]
        report = mod.validate(plan)
        self.assertIn("E_DEP_CYCLE", codes(report))

    def test_verify_requires_independent_isolation(self):
        plan = valid_plan()
        plan["strategy"] = "adversarial-verify"
        plan["stages"][0]["mode"] = "verify"
        plan["stages"][0]["isolation"] = "shared-readonly"
        report = mod.validate(plan)
        self.assertIn("E_VERIFY_ISOLATION", codes(report))

    def test_retry_requires_budget(self):
        plan = valid_plan()
        plan["budgets"]["max_retries_per_unit"] = 0
        plan["stages"][0]["on_failure"] = "retry"
        report = mod.validate(plan)
        self.assertIn("E_RETRY_BUDGET", codes(report))

    def test_parallel_plan_requires_capability(self):
        plan = valid_plan()
        plan["capabilities"]["optional"] = []
        plan["capabilities"]["degradation"] = {}
        report = mod.validate(plan)
        self.assertIn("E_PARALLEL_CAPABILITY", codes(report))

    def test_optional_parallel_capability_requires_safe_degradation(self):
        plan = valid_plan()
        plan["capabilities"]["degradation"] = {"parallelize-independent-work": "not-run"}
        report = mod.validate(plan)
        self.assertIn("E_PARALLEL_DEGRADATION", codes(report))

    def test_single_strategy_is_strictly_single(self):
        plan = valid_plan()
        plan["strategy"] = "single"
        report = mod.validate(plan)
        self.assertIn("E_STRATEGY_SHAPE", codes(report))

    def test_bounded_loop_requires_loop_stage(self):
        plan = valid_plan()
        plan["strategy"] = "bounded-loop"
        report = mod.validate(plan)
        self.assertIn("E_STRATEGY_SHAPE", codes(report))


def valid_v2_plan():
    plan = valid_plan()
    plan["contract"] = "workflow-plan/v2"
    plan["strategy"] = "gated-convergence"
    plan["authority"] = {
        "owner": "magia",
        "allowed_effects": ["read-only", "mutating"],
        "forbidden_effects": ["external-side-effect"],
        "write_scope": ["src/**"],
    }
    plan["stages"] = [
        {
            "id": "produce",
            "mode": "single",
            "work_source": "task:cp",
            "depends_on": [],
            "max_parallel": 1,
            "isolation": "serial",
            "effects": "mutating",
            "read_set": ["src/**"],
            "write_set": ["src/**"],
            "success": "candidate produced",
            "on_failure": "repair",
        }
    ]
    plan["budgets"] = {
        "max_workers": 2,
        "max_parallel": 1,
        "max_retries_per_unit": 1,
        "max_reentries": 2,
        "max_checkpoints": 3,
        "max_checkpoint_repairs": 2,
    }
    plan["capabilities"] = {
        "required": ["isolated-context"],
        "optional": [],
        "degradation": {},
    }
    plan["gates"] = [
        {
            "id": "proof",
            "kind": "executable-proof",
            "required": True,
            "isolation": "fresh-context",
            "evaluator_identity": "oracle:v1",
            "on_failure": "repair",
            "rerun_after_repair": True,
            "max_attempts": 3,
        },
        {
            "id": "review",
            "kind": "adversarial-review",
            "required": True,
            "isolation": "fresh-context",
            "evaluator_identity": "rubric:v1",
            "on_failure": "repair",
            "rerun_after_repair": True,
            "max_attempts": 3,
        },
    ]
    plan["checkpoints"] = [
        {
            "id": "cp-1",
            "objective": "first increment",
            "depends_on": [],
            "producer_stage": "produce",
            "gate_ids": ["proof", "review"],
            "success": "required gates pass",
        },
        {
            "id": "cp-2",
            "objective": "second increment",
            "depends_on": ["cp-1"],
            "producer_stage": "produce",
            "gate_ids": ["proof", "review"],
            "success": "required gates pass",
        },
    ]
    plan["promotion"] = {
        "requires_all_required_gates": True,
        "next_checkpoint_requires_promoted_dependencies": True,
        "accepted_feedback_only": True,
    }
    return plan


class WorkflowPlanV2ValidatorTests(unittest.TestCase):
    def test_valid_v2_gated_convergence_passes(self):
        report = mod.validate(valid_v2_plan())
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["validator"], "workflow-plan-validator/v2")

    def test_v1_remains_supported(self):
        report = mod.validate(valid_plan())
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["validator"], "workflow-plan-validator/v1")

    def test_v2_requires_gated_convergence_strategy(self):
        plan = valid_v2_plan()
        plan["strategy"] = "sequential"
        report = mod.validate(plan)
        self.assertIn("E_V2_STRATEGY", codes(report))

    def test_checkpoint_dependency_cycle_is_rejected(self):
        plan = valid_v2_plan()
        plan["checkpoints"][0]["depends_on"] = ["cp-2"]
        report = mod.validate(plan)
        self.assertIn("E_CHECKPOINT_CYCLE", codes(report))

    def test_checkpoint_requires_at_least_one_required_gate(self):
        plan = valid_v2_plan()
        for gate in plan["gates"]:
            gate["required"] = False
        report = mod.validate(plan)
        self.assertIn("E_CHECKPOINT_REQUIRED_GATE", codes(report))

    def test_executable_proof_requires_independent_isolation(self):
        plan = valid_v2_plan()
        plan["gates"][0]["isolation"] = "same-context"
        report = mod.validate(plan)
        self.assertIn("E_GATE_INDEPENDENCE", codes(report))

    def test_required_gate_capability_must_be_required(self):
        plan = valid_v2_plan()
        plan["gates"][0]["capability"] = "run-bounded-process"
        plan["capabilities"]["optional"] = ["run-bounded-process"]
        report = mod.validate(plan)
        self.assertIn("E_REQUIRED_GATE_CAPABILITY", codes(report))

    def test_repair_gate_requires_bounded_repairs(self):
        plan = valid_v2_plan()
        plan["budgets"]["max_checkpoint_repairs"] = 0
        report = mod.validate(plan)
        self.assertIn("E_REPAIR_BUDGET", codes(report))

    def test_required_repair_gate_must_rerun(self):
        plan = valid_v2_plan()
        plan["gates"][0]["rerun_after_repair"] = False
        report = mod.validate(plan)
        self.assertIn("E_STALE_GATE_PASS", codes(report))

    def test_promotion_invariant_cannot_be_disabled(self):
        plan = valid_v2_plan()
        plan["promotion"]["next_checkpoint_requires_promoted_dependencies"] = False
        report = mod.validate(plan)
        self.assertIn("E_PROMOTION_INVARIANT", codes(report))

    def test_perceptual_recapture_is_valid_but_other_recapture_is_not(self):
        plan = valid_v2_plan()
        plan["gates"][0]["on_failure"] = "recapture"
        report = mod.validate(plan)
        self.assertIn("E_RECAPTURE_GATE", codes(report))



if __name__ == "__main__":
    unittest.main()
