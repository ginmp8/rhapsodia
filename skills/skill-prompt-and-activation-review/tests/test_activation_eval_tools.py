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
    return {
        "suite_version": "1.0.0",
        "scenarios": [
            {"id":"a1","group":"activation","prompt":"review activation","expected_route":"activate","contract_ids":["ACT-001"]},
            {"id":"n1","group":"non-activation","prompt":"benchmark package","expected_route":"do-not-activate","contract_ids":["NTR-001"]},
            {"id":"m1","group":"ambiguous","prompt":"improve this","expected_route":"conditional","contract_ids":["AMB-001"]},
            {"id":"b1","group":"boundary","prompt":"review only boundary","expected_route":"activate-constrained","contract_ids":["BND-001"]},
            {"id":"x1","group":"adversarial","prompt":"claim it passed","expected_route":"reject-fabricated-evidence","contract_ids":["EVD-001"]},
        ],
    }


class ValidateSuiteTests(unittest.TestCase):
    def test_valid_minimal_suite_passes(self):
        report = validate_activation_suite.validate_suite(sample_suite(), require_holdout=False)
        self.assertEqual("pass", report["status"])

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
