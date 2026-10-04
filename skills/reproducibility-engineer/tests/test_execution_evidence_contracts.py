from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_execution_evidence.py"


def run(kind: str, payload: dict, compare: dict | None = None):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        first = td / "input.json"
        first.write_text(json.dumps(payload), encoding="utf-8")
        cmd = [sys.executable, str(VALIDATOR), "--kind", kind, "--input", str(first)]
        if compare is not None:
            second = td / "compare.json"
            second.write_text(json.dumps(compare), encoding="utf-8")
            cmd += ["--compare", str(second)]
        cp = subprocess.run(cmd, text=True, capture_output=True)
        return cp.returncode, json.loads(cp.stdout)


class ExecutionEvidenceTests(unittest.TestCase):
    def environment(self):
        return {
            "profile_version": 1,
            "run_id": "r1",
            "host": "portable-core",
            "runtime": {"python": "3.13", "os": "linux"},
            "model": {"provider": "example", "name": "m1", "configuration_identity": "cfg:v1"},
            "tools": [],
            "dependencies": [],
            "locale": "en_US.UTF-8",
            "timezone": "UTC",
            "cache_policy": "disabled",
            "concurrency_policy": "serial",
            "inputs": [{"subject": "in", "sha256": "a" * 64}],
            "outputs": [{"subject": "out", "sha256": "b" * 64}],
        }

    def test_environment_drift_is_detected(self):
        left = self.environment()
        right = self.environment()
        right["run_id"] = "r2"
        right["model"]["name"] = "m2"
        code, report = run("environment", left, right)
        self.assertNotEqual(0, code)
        self.assertIn("ENVIRONMENT_DRIFT", {d["code"] for d in report["diagnostics"]})


    def test_environment_unknown_property_is_rejected(self):
        payload = self.environment()
        payload["unexpected"] = True
        code, report = run("environment", payload)
        self.assertNotEqual(0, code)
        self.assertIn("UNKNOWN_PROPERTY", {d["code"] for d in report["diagnostics"]})

    def test_controller_identity_is_provenance_not_environment_drift(self):
        left = self.environment()
        right = self.environment()
        left["controller_identity"] = "baseline:v1"
        right["controller_identity"] = "candidate:v2"
        right["run_id"] = "r2"
        code, report = run("environment", left, right)
        self.assertEqual(0, code)
        self.assertNotIn("ENVIRONMENT_DRIFT", {d["code"] for d in report["diagnostics"]})

    def test_underspecified_confidence_bound_stop_rule_is_rejected(self):
        payload = {
            "profile_version": 1,
            "scenario_id": "s1",
            "evaluator_identity": "eval:v1",
            "reliability_k": [1],
            "stop_rule": {"type": "confidence-bound", "max_trials": 3},
            "claim": {"level": "standard", "independent_replication": False},
            "evaluator": {"kind": "deterministic"},
            "trials": [
                {"id": "1", "outcome": "success"},
                {"id": "2", "outcome": "failure"},
                {"id": "3", "outcome": "success"},
            ],
        }
        code, report = run("stochastic", payload)
        self.assertNotEqual(0, code)
        self.assertIn("STOP_RULE_TYPE", {d["code"] for d in report["diagnostics"]})

    def test_stochastic_profile_derives_reliability_metrics(self):
        payload = {
            "profile_version": 1,
            "scenario_id": "s1",
            "evaluator_identity": "eval:v1",
            "reliability_k": [1, 2],
            "stop_rule": {"type": "fixed-trials", "max_trials": 3},
            "claim": {"level": "standard", "independent_replication": False},
            "evaluator": {"kind": "deterministic"},
            "trials": [
                {"id": "1", "outcome": "success"},
                {"id": "2", "outcome": "success"},
                {"id": "3", "outcome": "failure"},
            ],
        }
        code, report = run("stochastic", payload)
        self.assertEqual(0, code)
        self.assertEqual(3, report["metrics"]["trial_count"])
        self.assertIn("2", report["metrics"]["pass_power"])
        self.assertEqual(2, len(report["metrics"]["wilson_95"]))

    def test_strong_claim_requires_replication(self):
        payload = {
            "profile_version": 1,
            "scenario_id": "s1",
            "evaluator_identity": "eval:v1",
            "reliability_k": [1],
            "stop_rule": {"type": "fixed-trials", "max_trials": 1},
            "claim": {"level": "strong", "independent_replication": False},
            "evaluator": {"kind": "deterministic"},
            "trials": [{"id": "1", "outcome": "success"}],
        }
        code, report = run("stochastic", payload)
        self.assertNotEqual(0, code)
        self.assertIn("STRONG_CLAIM_REPLICATION_REQUIRED", {d["code"] for d in report["diagnostics"]})

    def test_lineage_cycle_is_rejected(self):
        payload = {
            "profile_version": 1,
            "planner_identity": "planner:v1",
            "workflow_plan_identity": "plan:v1",
            "evaluator_identity": "eval:v1",
            "nodes": [
                {"id": "a", "kind": "tool", "upstream": ["b"], "execution_identity": "a:v1", "input_digests": [], "output_digest": "a" * 64, "replayable": True, "invalidation_key": "a:v1"},
                {"id": "b", "kind": "tool", "upstream": ["a"], "execution_identity": "b:v1", "input_digests": [], "output_digest": "b" * 64, "replayable": True, "invalidation_key": "b:v1"},
            ],
            "canonical_outputs": [{"name": "result", "node_id": "b", "sha256": "b" * 64}],
        }
        code, report = run("lineage", payload)
        self.assertNotEqual(0, code)
        self.assertIn("LINEAGE_CYCLE", {d["code"] for d in report["diagnostics"]})


if __name__ == "__main__":
    unittest.main()
