import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_activation_evidence
import freeze_activation_evaluator
import validate_activation_evidence
import validate_activation_suite


def canonical_suite():
    return json.loads((ROOT / "evals" / "activation-scenarios.json").read_text(encoding="utf-8"))


def expected_activated(route):
    if route in {"activate", "activate-constrained", "split-handoff"}:
        return True
    if isinstance(route, str) and route.startswith("reject-"):
        return True
    return False


def routing_profile(catalog_hash="a" * 64):
    return {
        "host": "test-host",
        "host_version": "1.0",
        "model_provider": "test-provider",
        "model_name": "test-model",
        "model_snapshot": "snapshot-1",
        "discovery_mode": "hybrid",
        "skill_catalog_sha256": catalog_hash,
        "skill_catalog_size": 12,
        "metadata_extensions": [],
    }


def evidence_for(suite, trials_per_case=3, execution_kind="host-routing"):
    profile = routing_profile()
    cases = []
    for scenario in suite["scenarios"]:
        route = scenario["expected_route"]
        trials = [
            {
                "activated": expected_activated(route),
                "observed_route": route,
                "evidence": f"trace:{scenario['id']}:{idx}",
            }
            for idx in range(trials_per_case)
        ]
        cases.append({
            "id": scenario["id"],
            "invocation_mode": scenario["invocation_mode"],
            "trials": trials,
        })
    return {
        "evidence_version": 2,
        "suite_sha256": compare_activation_evidence.canonical_suite_hash(suite),
        "evaluator_sha256": "b" * 64,
        "execution_kind": execution_kind,
        "evidence_status": "executed",
        "executed_at": "2026-10-04T16:00:00-03:00",
        "evaluator_visibility": "candidate-visible",
        "candidate_saw_evaluator_only_assets": False,
        "routing_profile": profile,
        "routing_fingerprint_sha256": validate_activation_evidence.routing_fingerprint(profile),
        "trial_policy": {"mode": "fixed-trials", "trials_per_case": trials_per_case},
        "cases": cases,
    }


class ValidateSuiteTests(unittest.TestCase):
    def test_canonical_suite_passes(self):
        report = validate_activation_suite.validate_suite(canonical_suite())
        self.assertEqual("pass", report["status"])
        self.assertGreater(report["invocation_mode_counts"]["contextual"], 0)
        self.assertGreater(report["negative_kind_counts"]["alternative-owner"], 0)
        self.assertGreater(report["negative_kind_counts"]["abstain"], 0)

    def test_group_type_mismatch_fails(self):
        suite = canonical_suite()
        suite["scenarios"][0]["type"] = "should_not_activate"
        report = validate_activation_suite.validate_suite(suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/group-type-mismatch", {e["code"] for e in report["errors"]})

    def test_category_type_mismatch_fails(self):
        suite = canonical_suite()
        suite["scenarios"][0]["category"] = "should_not_activate"
        report = validate_activation_suite.validate_suite(suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/category-type-mismatch", {e["code"] for e in report["errors"]})

    def test_bundled_evaluator_only_visibility_fails(self):
        suite = canonical_suite()
        suite["scenarios"][0]["visibility"] = "evaluator-only"
        report = validate_activation_suite.validate_suite(suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/bundled-evaluator-only", {e["code"] for e in report["errors"]})

    def test_explicit_auto_routing_fails(self):
        suite = canonical_suite()
        suite["scenarios"][0]["measurement_scope"] = "auto-routing"
        report = validate_activation_suite.validate_suite(suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/explicit-auto-routing", {e["code"] for e in report["errors"]})

    def test_alternative_owner_requires_neighbor_owner(self):
        suite = canonical_suite()
        near_miss = next(s for s in suite["scenarios"] if s.get("negative_kind") == "alternative-owner")
        near_miss.pop("neighbor_owner", None)
        report = validate_activation_suite.validate_suite(suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("scenario/neighbor-owner", {e["code"] for e in report["errors"]})


class FreezeEvaluatorTests(unittest.TestCase):
    def test_manifest_detects_changed_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("one", encoding="utf-8")
            manifest = freeze_activation_evaluator.build_manifest(root, ["a.txt"])
            self.assertEqual("pass", freeze_activation_evaluator.verify_manifest(root, manifest)["status"])
            (root / "a.txt").write_text("two", encoding="utf-8")
            self.assertEqual("fail", freeze_activation_evaluator.verify_manifest(root, manifest)["status"])


class EvidenceValidationTests(unittest.TestCase):
    def test_valid_v2_evidence_passes_and_derives_trigger_rates(self):
        suite = canonical_suite()
        evidence = evidence_for(suite)
        report = validate_activation_evidence.validate_evidence(evidence, suite)
        self.assertEqual("pass", report["status"])
        self.assertEqual(3, report["cases"][0]["trial_count"])
        self.assertIsNotNone(report["cases"][0]["trigger_rate"])

    def test_trial_count_mismatch_fails(self):
        suite = canonical_suite()
        evidence = evidence_for(suite)
        evidence["cases"][0]["trials"].pop()
        report = validate_activation_evidence.validate_evidence(evidence, suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("evidence/trial-count-mismatch", {e["code"] for e in report["errors"]})

    def test_invocation_mode_mismatch_fails(self):
        suite = canonical_suite()
        evidence = evidence_for(suite)
        evidence["cases"][0]["invocation_mode"] = "implicit"
        report = validate_activation_evidence.validate_evidence(evidence, suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("evidence/invocation-mode-mismatch", {e["code"] for e in report["errors"]})

    def test_hidden_evaluator_leak_fails(self):
        suite = canonical_suite()
        evidence = evidence_for(suite)
        evidence["evaluator_visibility"] = "hidden"
        evidence["candidate_saw_evaluator_only_assets"] = True
        report = validate_activation_evidence.validate_evidence(evidence, suite)
        self.assertEqual("fail", report["status"])
        self.assertIn("evidence/evaluator-leakage", {e["code"] for e in report["errors"]})


class CompareEvidenceTests(unittest.TestCase):
    def test_non_host_evidence_never_emits_behavioral_metrics(self):
        suite = canonical_suite()
        base = evidence_for(suite, execution_kind="static-adjudication")
        cand = copy.deepcopy(base)
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("pass", report["status"])
        self.assertEqual("not-claimable", report["behavioral_comparison"]["status"])
        self.assertIsNone(report["behavioral_comparison"]["deltas"])

    def test_routing_fingerprint_mismatch_is_blocking(self):
        suite = canonical_suite()
        base = evidence_for(suite)
        cand = copy.deepcopy(base)
        cand["routing_profile"] = routing_profile("c" * 64)
        cand["routing_fingerprint_sha256"] = validate_activation_evidence.routing_fingerprint(cand["routing_profile"])
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("fail", report["status"])
        self.assertIn("comparison/routing-fingerprint", {e["code"] for e in report["errors"]})

    def test_trial_policy_mismatch_is_blocking(self):
        suite = canonical_suite()
        base = evidence_for(suite, trials_per_case=3)
        cand = evidence_for(suite, trials_per_case=2)
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("fail", report["status"])
        self.assertIn("comparison/trial-policy", {e["code"] for e in report["errors"]})

    def test_repeated_trials_report_separate_metrics(self):
        suite = canonical_suite()
        base = evidence_for(suite)
        cand = copy.deepcopy(base)
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("pass", report["status"])
        behavioral = report["behavioral_comparison"]
        self.assertEqual("measured-repeated", behavioral["status"])
        metrics = behavioral["candidate"]
        self.assertIn("auto_activation_precision", metrics)
        self.assertIn("auto_activation_recall", metrics)
        self.assertIn("abstention_accuracy", metrics)
        self.assertIn("near_miss_false_activation_rate", metrics)
        self.assertIn("explicit_route_accuracy", metrics)
        self.assertEqual(1.0, metrics["abstention_accuracy"]["rate"])
        self.assertEqual(0.0, metrics["near_miss_false_activation_rate"]["rate"])

    def test_explicit_failure_does_not_change_auto_precision_or_recall(self):
        suite = canonical_suite()
        base = evidence_for(suite)
        cand = copy.deepcopy(base)
        explicit_id = next(s["id"] for s in suite["scenarios"] if s["invocation_mode"] == "explicit")
        case = next(c for c in cand["cases"] if c["id"] == explicit_id)
        for trial in case["trials"]:
            trial["activated"] = False
            trial["observed_route"] = "do-not-activate"
        report = compare_activation_evidence.compare(suite, base, cand)
        self.assertEqual("pass", report["status"])
        bm = report["behavioral_comparison"]["baseline"]
        cm = report["behavioral_comparison"]["candidate"]
        self.assertEqual(bm["auto_activation_precision"]["rate"], cm["auto_activation_precision"]["rate"])
        self.assertEqual(bm["auto_activation_recall"]["rate"], cm["auto_activation_recall"]["rate"])
        self.assertLess(cm["explicit_route_accuracy"]["rate"], bm["explicit_route_accuracy"]["rate"])


if __name__ == "__main__":
    unittest.main()
