import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_activation_evidence
import freeze_activation_evaluator
import validate_activation_suite


def sample_suite():
    rows = [
        ("a1", "activation", "should_activate", "review activation", "activate", ["ACT-001"]),
        ("n1", "non-activation", "should_not_activate", "benchmark package", "do-not-activate", ["NTR-001"]),
        ("m1", "ambiguous", "ambiguous", "improve this", "conditional", ["AMB-001"]),
        ("b1", "boundary", "edge_case", "review only boundary", "activate-constrained", ["BND-001"]),
        ("x1", "adversarial", "adversarial", "claim it passed", "reject-fabricated-evidence", ["EVD-001"]),
    ]
    scenarios = []
    for sid, group, harness_type, prompt, route, contract_ids in rows:
        scenarios.append({
            "id": sid,
            "group": group,
            "type": harness_type,
            "category": harness_type,
            "prompt": prompt,
            "expected_route": route,
            "expected_behavior": f"route as {route}",
            "acceptance_criteria": [f"expected_route remains {route}"],
            "contract_ids": contract_ids,
            "evaluation_tier": "L2-focused",
            "visibility": "candidate-visible",
        })
    return {
        "suite_version": "2.0.0",
        "target_skill": "skill-prompt-and-activation-review",
        "status": "planned",
        "scenarios": scenarios,
    }


class ValidateSuiteTests(unittest.TestCase):
    def test_valid_minimal_suite_passes(self):
        report = validate_activation_suite.validate_suite(sample_suite(), require_holdout=False)
        self.assertEqual("pass", report["status"])


    def test_group_type_mismatch_fails(self):
        suite = sample_suite()
        suite["scenarios"][0]["type"] = "should_not_activate"
        report = validate_activation_suite.validate_suite(suite, require_holdout=False)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/group-type-mismatch", {e["code"] for e in report["errors"]})


    def test_category_type_mismatch_fails(self):
        suite = sample_suite()
        suite["scenarios"][0]["category"] = "should_not_activate"
        report = validate_activation_suite.validate_suite(suite, require_holdout=False)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/category-type-mismatch", {e["code"] for e in report["errors"]})

    def test_bundled_evaluator_only_visibility_fails(self):
        suite = sample_suite()
        suite["scenarios"][0]["visibility"] = "evaluator-only"
        report = validate_activation_suite.validate_suite(suite, require_holdout=False)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/bundled-evaluator-only", {e["code"] for e in report["errors"]})

    def test_duplicate_ids_fail(self):
        suite = sample_suite()
        suite["scenarios"].append(dict(suite["scenarios"][0]))
        report = validate_activation_suite.validate_suite(suite, require_holdout=False)
        self.assertEqual("fail", report["status"])
        self.assertIn("suite/unique-ids", {e["code"] for e in report["errors"]})


class FreezeEvaluatorTests(unittest.TestCase):
    def test_manifest_detects_changed_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("one", encoding="utf-8")
            manifest = freeze_activation_evaluator.build_manifest(root, ["a.txt"])
            ok = freeze_activation_evaluator.verify_manifest(root, manifest)
            self.assertEqual("pass", ok["status"])
            (root / "a.txt").write_text("two", encoding="utf-8")
            changed = freeze_activation_evaluator.verify_manifest(root, manifest)
            self.assertEqual("fail", changed["status"])


class CompareEvidenceTests(unittest.TestCase):
    def test_non_host_evidence_never_emits_behavioral_metrics(self):
        suite = sample_suite()
        suite_bytes = json.dumps(suite, sort_keys=True, separators=(",", ":")).encode()
        suite_hash = hashlib.sha256(suite_bytes).hexdigest()
        base = {"suite_sha256":suite_hash,"evaluator_sha256":"e1","execution_kind":"static-adjudication","evidence_status":"executed","cases":[]}
        cand = {"suite_sha256":suite_hash,"evaluator_sha256":"e1","execution_kind":"static-adjudication","evidence_status":"executed","cases":[]}
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("not-claimable", report["behavioral_comparison"]["status"])
        self.assertIsNone(report["behavioral_comparison"]["activation_precision_delta"])

    def test_mismatched_suite_hash_is_blocking(self):
        suite = sample_suite()
        base = {"suite_sha256":"wrong","evaluator_sha256":"e1","execution_kind":"host-routing","evidence_status":"executed","cases":[]}
        cand = {"suite_sha256":"wrong","evaluator_sha256":"e1","execution_kind":"host-routing","evidence_status":"executed","cases":[]}
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("fail", report["status"])
        self.assertIn("comparison/suite-identity", {e["code"] for e in report["errors"]})

    def test_hidden_evaluator_leak_is_blocking(self):
        suite = sample_suite()
        suite_hash = hashlib.sha256(json.dumps(suite, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        cases = [{"id": scenario["id"], "observed_route": scenario["expected_route"], "activated": scenario["expected_route"] in {"activate", "activate-constrained"}} for scenario in suite["scenarios"]]
        base = {"suite_sha256": suite_hash, "evaluator_sha256": "e1", "execution_kind": "host-routing", "evidence_status": "executed", "host_profile": "h1", "evaluator_visibility": "hidden", "candidate_saw_evaluator_only_assets": False, "cases": cases}
        cand = dict(base)
        cand["candidate_saw_evaluator_only_assets"] = True
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("fail", report["status"])
        self.assertIn("comparison/evaluator-leakage", {e["code"] for e in report["errors"]})

    def test_host_profile_mismatch_is_blocking(self):
        suite = sample_suite()
        suite_hash = hashlib.sha256(json.dumps(suite, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        cases = [{"id": scenario["id"], "observed_route": scenario["expected_route"], "activated": scenario["expected_route"] in {"activate", "activate-constrained"}} for scenario in suite["scenarios"]]
        base = {"suite_sha256": suite_hash, "evaluator_sha256": "e1", "execution_kind": "host-routing", "evidence_status": "executed", "host_profile": "h1", "cases": cases}
        cand = dict(base)
        cand["host_profile"] = "h2"
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("fail", report["status"])
        self.assertIn("comparison/host-profile", {e["code"] for e in report["errors"]})


if __name__ == "__main__":
    unittest.main()
