"""Portable stdlib regression tests for the Premortem Analysis package.

Runtime model activation and scientific truth are intentionally out of scope.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from unittest import mock
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_package import validate_package
from validate_report import validate_report
from validate_traceability import validate_traceability
from package import build


class TestReportContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads((ROOT / "examples/messaging-migration.json").read_text(encoding="utf-8"))

    def changed(self, fn):
        report = copy.deepcopy(self.good)
        fn(report)
        return validate_report(report)

    def test_valid_fictional_example(self):
        self.assertEqual(validate_report(self.good), [])

    def test_model_does_not_turn_hypothesis_into_observation(self):
        errors = self.changed(lambda x: x.update(hypothetical=False))
        self.assertTrue(any("hypothetical" in e for e in errors))

    def test_unsupported_probability_field_rejected(self):
        errors = self.changed(lambda x: x["risks"][0].update(probability=0.97))
        self.assertTrue(any("unexpected key 'probability'" in e for e in errors))

    def test_supported_claim_requires_real_source(self):
        errors = self.changed(lambda x: x["risks"][0].update(evidence_status="supported", source_ids=[]))
        self.assertTrue(any("requires a source reference" in e for e in errors))

    def test_unknown_source_reference_rejected(self):
        errors = self.changed(lambda x: x["risks"][0].update(source_ids=["SRC-999"]))
        self.assertTrue(any("unknown source" in e for e in errors))

    def test_duplicate_risk_ids_rejected(self):
        errors = self.changed(lambda x: x["risks"][1].update(risk_id="RISK-001"))
        self.assertTrue(any("duplicate ID" in e for e in errors))

    def test_missing_causal_mechanism_rejected(self):
        errors = self.changed(lambda x: x["risks"][0].update(causal_chain=["cause", "consequence"]))
        self.assertTrue(any("fewer array items" in e for e in errors))

    def test_unknown_related_risk_rejected(self):
        errors = self.changed(lambda x: x["plan_changes"][0].update(related_risk_ids=["RISK-999"]))
        self.assertTrue(any("unknown risk" in e for e in errors))

    def test_unsupported_owner_approval_rejected(self):
        errors = self.changed(lambda x: x["plan_changes"][0].update(disposition="accepted"))
        self.assertTrue(any("decision evidence" in e for e in errors))

    def test_approval_with_owner_and_documented_decision_allowed(self):
        report = copy.deepcopy(self.good)
        report["plan_changes"][0].update(disposition="accepted", decision_owner="System owner", decision_evidence="Recorded decision reference DEC-2026-1014")
        self.assertEqual(validate_report(report), [])

    def test_governed_cannot_omit_approval_gates(self):
        errors = self.changed(lambda x: x.update(approval_gates=[]))
        self.assertTrue(any("approval/stop gates" in e for e in errors))

    def test_gate_cannot_self_approve(self):
        errors = self.changed(lambda x: x["approval_gates"][0].update(status="satisfied"))
        self.assertTrue(any("satisfied gate" in e for e in errors))

    def test_empty_complete_does_not_prove_safety(self):
        errors = self.changed(lambda x: x.update(status="complete", risks=[], residual_risks=[], plan_changes=[]))
        self.assertTrue(any("zero risks" in e for e in errors))

    def test_partial_requires_limitation(self):
        errors = self.changed(lambda x: x.update(unknowns=[], limitations=[]))
        self.assertTrue(any("unknowns or limitations" in e for e in errors))

    def test_unsafe_source_uri(self):
        errors = self.changed(lambda x: x["sources"][0].update(locator="javascript:alert(1)"))
        self.assertTrue(any("unsafe locator" in e for e in errors))

    def test_malformed_nested_object_does_not_crash(self):
        errors = self.changed(lambda x: x["risks"][0].update(source_ids=[{"bad": "type"}]))
        self.assertTrue(errors)

    def test_missing_entire_required_branch(self):
        errors = self.changed(lambda x: x.pop("failure_criterion"))
        self.assertTrue(any("missing key" in e for e in errors))


class TestTraceAndActivationFixtures(unittest.TestCase):
    def test_full_bidirectional_trace(self):
        trace = json.loads((ROOT / "evidence/traceability.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_traceability(trace), [])
        self.assertEqual(len(trace["findings"]), 12)
        self.assertEqual(len(trace["requirements"]), 18)
        self.assertIn("rejected", {x["disposition"] for x in trace["findings"]})

    def test_mismatched_research_reverse_link_is_rejected(self):
        trace = json.loads((ROOT / "evidence/traceability.json").read_text(encoding="utf-8"))
        trace["requirements"][0]["finding_ids"] = []
        self.assertTrue(validate_traceability(trace))

    def test_unknown_evaluation_is_rejected(self):
        trace = json.loads((ROOT / "evidence/traceability.json").read_text(encoding="utf-8"))
        trace["requirements"][0]["evaluation_ids"] = ["E-999"]
        self.assertTrue(validate_traceability(trace))

    def test_activation_suite_exercises_overlap(self):
        suite = json.loads((ROOT / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
        labels = {case["expected"] for case in suite["cases"]}
        self.assertEqual(labels, {"activate", "do-not-activate", "delegate"})
        self.assertGreaterEqual(len(suite["cases"]), 12)
        self.assertEqual(len({case["id"] for case in suite["cases"]}), len(suite["cases"]))
        self.assertTrue(all(case["prompt"] and case["reason"] for case in suite["cases"]))

    def test_behavior_suite_no_fabricated_measured_claims(self):
        suite = json.loads((ROOT / "evals/behavior-scenarios.json").read_text(encoding="utf-8"))
        self.assertIn("not-executed", suite["status"])
        self.assertTrue(all(x["must"] and x["must_not"] for x in suite["cases"]))


class TestPackage(unittest.TestCase):
    def test_validation_and_top100_control_surface(self):
        self.assertEqual(validate_package(ROOT), [])
        lines = (ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 100)
        intro = "\n".join(lines[:100])
        for anchor in ("quick", "standard", "governed", "hypothetical", "not-run", "risk", "## Direct resources"):
            self.assertIn(anchor, intro)

    def test_package_hashes_repeat_with_distinct_output_paths(self):
        with tempfile.TemporaryDirectory(prefix="premortem-test-") as temp:
            d = Path(temp)
            a = build(ROOT, d / "a.zip", d / "a.json")
            b = build(ROOT, d / "b.zip", d / "b.json")
            self.assertEqual(a["archive_sha256"], b["archive_sha256"])
            self.assertEqual(hashlib.sha256((d / "a.zip").read_bytes()).hexdigest(), a["archive_sha256"])
            self.assertEqual((d / "a.zip").read_bytes(), (d / "b.zip").read_bytes())

    def test_no_writes_inside_skill_tree(self):
        with tempfile.TemporaryDirectory(prefix="premortem-test-") as temp:
            d = Path(temp)
            with self.assertRaises(ValueError):
                build(ROOT, ROOT / "bad.zip", d / "receipt.json")

    def test_atomic_output_rollback_preserves_prior_bytes(self):
        with tempfile.TemporaryDirectory(prefix="premortem-test-") as temp:
            d = Path(temp)
            out, receipt = d / "prior.zip", d / "prior.json"
            out.write_bytes(b"prior-archive")
            receipt.write_bytes(b"prior-receipt")
            original_replace = os.replace
            calls = 0

            def fail_second_commit(src, dst):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated receipt commit failure")
                return original_replace(src, dst)

            with mock.patch("package.os.replace", side_effect=fail_second_commit):
                with self.assertRaises(OSError):
                    build(ROOT, out, receipt, overwrite=True)
            self.assertEqual(out.read_bytes(), b"prior-archive")
            self.assertEqual(receipt.read_bytes(), b"prior-receipt")

    def test_package_root_matches_skill_identity(self):
        with tempfile.TemporaryDirectory(prefix="premortem-test-") as temp:
            d = Path(temp)
            with self.assertRaises(ValueError):
                build(ROOT, d / "archive.txt", d / "receipt.json")

    def test_release_mismatch_caught(self):
        with tempfile.TemporaryDirectory(prefix="premortem-test-") as temp:
            d = Path(temp) / "premortem-analysis"
            d.mkdir()
            (d / "SKILL.md").write_text((ROOT / "SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
            (d / "VERSION").write_text("9.9.9\n", encoding="utf-8")
            (d / "CHANGELOG.md").write_text((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), encoding="utf-8")
            self.assertTrue(any("CHANGELOG" in e for e in validate_package(d)))


if __name__ == "__main__":
    unittest.main()
