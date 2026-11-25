"""Structural regression checks for new, source-backed penalty adjudication."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_core import AuditError, canonical, extract_requirements, normalize_source
from implementation_review import ADJUDICATION_POLICY, blob_sha, compare_grades, grade, init_review


class AdjudicationGateTests(unittest.TestCase):
    def setUp(self):
        self.raw = {"repository": "example/audit", "pull_request": {
            "number": 3, "head_sha": "a" * 40, "base_sha": "b" * 40,
            "files": ["service.py", "test_service.py"]}, "issue": {"number": 2,
            "body": "## Acceptance criteria\nAC-01: Reject unverified approvals and test the rejection and success paths.\nAC-02: Preserve the explicit override.",
            "comments": []}}
        self.raw["capture"] = {"method": "offline_input", "issue_completeness": "not_verified"}
        self.source = normalize_source(self.raw)
        self.requirements = extract_requirements(self.source)
        self.review = init_review(self.source, self.requirements)
        self.code = "def approve(verified):\n    return 'approved' if verified else 'blocked'\n"
        self.test = "def test_approve():\n    assert approve(True) == 'approved'\n"
        self.implementation = {"path": "service.py", "blob_sha": blob_sha(self.code.encode()),
            "line_start": 1, "line_end": 2, "role": "implementation",
            "claim": "Both runtime branches select the correct approval result."}
        self.negative = {"path": "test_service.py", "blob_sha": blob_sha(self.test.encode()),
            "line_start": 1, "line_end": 2, "role": "counterexample",
            "claim": "The sole fixture test asserts only the successful branch."}
        self.gap = ("mandatory_test | test the rejection and success paths | test_service.py:L1-L2 | "
                    "Only the success result is asserted in the bounded fixture test inventory. | "
                    "The reachable runtime guard works; the existing success assertion does not exercise rejection.")
        self.review["criteria"]["AC-01"] = {"status": "PARTIAL", "rationale":
            "The approval path is implemented, but its explicitly required rejection assertion is absent.",
            "trace": "approve returns blocked for false and approved for true; the only test asserts true.",
            "evidence": [self.implementation, self.negative], "remaining": [self.gap]}

    def evaluate(self, strict=True):
        return grade(self.source, self.requirements, self.review, allow_provisional=True,
                     require_adjudication=strict)

    def test_gate_accepts_typed_source_backed_gap_without_changing_score(self):
        legacy, strict = self.evaluate(False), self.evaluate()
        self.assertEqual(legacy["summary"], strict["summary"])
        self.assertEqual(strict["summary"]["numeric_delivery_grade_pct"], "25.00")
        self.assertEqual(strict["adjudication_policy"], ADJUDICATION_POLICY)
        self.assertFalse(strict["ci_affects_grade"])
        self.assertNotIn("adjudication_policy", legacy)
        self.assertEqual(canonical(strict), canonical(self.evaluate()))
        with self.assertRaisesRegex(AuditError, "adjudication policies differ"):
            compare_grades(legacy, strict)

    def test_gate_rejects_vague_partial_and_legacy_remains_replayable(self):
        self.review["criteria"]["AC-01"]["remaining"] = ["The matching implementation may be incomplete."]
        self.assertEqual(self.evaluate(False)["summary"]["numeric_delivery_grade_pct"], "25.00")
        with self.assertRaisesRegex(AuditError, "adjudication gap needs"):
            self.evaluate()

    def test_each_gap_requires_own_negative_anchor_and_normative_quote(self):
        row = self.review["criteria"]["AC-01"]
        for bad, error in [
            (self.gap.replace("test the rejection and success paths", "test every possible input"), "exact quote"),
            (self.gap.replace("test_service.py:L1-L2", "service.py:L1-L2"), "counterexample source anchor"),
            (self.gap.replace("mandatory_test", "optional"), "unsupported normative gap kind"),
            (self.gap.rsplit(" | ", 1)[0] + " | unknown", "counterevidence reconciliation"),
        ]:
            with self.subTest(bad=bad):
                row["remaining"] = [self.gap, bad]
                with self.assertRaisesRegex(AuditError, error):
                    self.evaluate()
        row["remaining"] = [self.gap]
        row["evidence"] = [self.implementation]
        with self.assertRaisesRegex(AuditError, "counterexample source anchor"):
            self.evaluate()

    def test_unknown_is_not_forced_into_a_penalty(self):
        self.review = init_review(self.source, self.requirements)
        result = self.evaluate()
        self.assertEqual(result["summary"]["assessed"], 0)
        self.assertEqual(result["summary"]["counts"]["UNVERIFIED"], 2)
        self.assertIsNone(result["summary"]["development_progress_assessed_pct"])

    def test_bundle_and_cli_grade_verify_use_same_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            inputs = {"source": self.source, "requirements": self.requirements,
                      "review": self.review, "raw": self.raw}
            for name, value in inputs.items():
                (directory / (name + ".json")).write_bytes(canonical(value))
            common = ["--source", str(directory / "source.json"), "--requirements", str(directory / "requirements.json"),
                      "--review", str(directory / "review.json"), "--allow-provisional", "--require-review", "--require-adjudication"]
            output = directory / "graded"
            def run(script, *args):
                return subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / script), *args],
                                      capture_output=True, text=True)
            result = run("pr_audit.py", "code-grade", *common, "--out", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            result = run("pr_audit.py", "verify-code-grade", *common,
                         "--report-json", str(output / "implementation-grade.json"),
                         "--report-md", str(output / "implementation-grade.md"))
            self.assertEqual(result.returncode, 0, result.stderr)
            bundle = directory / "bundle"
            args = ["--from-json", str(directory / "raw.json"), "--review", str(directory / "review.json"),
                    "--allow-provisional", "--require-review", "--require-adjudication"]
            result = run("audit_bundle.py", *args, "--out", str(bundle))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((bundle / "implementation-grade.json").read_bytes(),
                             (output / "implementation-grade.json").read_bytes())
            self.review["criteria"]["AC-01"]["remaining"] = ["Unverified concern about the existing test suite."]
            (directory / "review.json").write_bytes(canonical(self.review))
            result = run("audit_bundle.py", *args, "--out", str(directory / "rejected"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("adjudication gap needs", result.stderr)
            self.assertFalse((directory / "rejected" / "audit-bundle.zip").exists())
