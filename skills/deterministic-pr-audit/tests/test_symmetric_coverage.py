"""Regression cases for explicit criterion identity and symmetric test evidence."""
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_core import AuditError, canonical, extract_requirements, normalize_source
from implementation_review import COVERAGE_POLICY, blob_sha, compare_grades, grade, init_review


class SymmetricCoverageTests(unittest.TestCase):
    def setUp(self):
        self.body = ("## Request matching (REQ-03)\nDistinguish absent values from explicit null.\n"
                     "## Acceptance criteria\n- [ ] AC-07: Header matching is tested; missing/null and quantifiers have positive and negative tests.\n"
                     "- [x] AC-08: Reject invalid conditions.\n")
        self.raw = {"repository": "example/audit", "pull_request": {"number": 3, "head_sha": "a" * 40,
                    "base_sha": "b" * 40, "files": ["matcher.py", "test_matcher.py"]},
                    "issue": {"number": 1, "body": self.body, "comments": []}}
        self.raw["capture"] = {"method": "offline_input", "issue_completeness": "not_verified"}
        self.source = normalize_source(self.raw)
        self.requirements = extract_requirements(self.source, canonical_ids=True)
        self.review = init_review(self.source, self.requirements, coverage=True)
        self.code = "def matches(value):\n    return value is None\n"
        self.test = "def test_matches():\n    assert matches(None)\n"
        self.impl = {"path": "matcher.py", "blob_sha": blob_sha(self.code.encode()),
                     "line_start": 1, "line_end": 2, "role": "implementation", "claim": "The matcher evaluates explicit null correctly."}
        self.test_ref = {"path": "test_matcher.py", "blob_sha": blob_sha(self.test.encode()),
                         "line_start": 1, "line_end": 2, "role": "test", "claim": "Source-backed assertion for the named test obligation."}
        self.counter = {**self.test_ref, "role": "counterexample", "claim": "The bounded example lacks the negative test witness."}
        self.anchor = "test_matcher.py:L1-L2"
        self.quote = "missing/null and quantifiers have positive and negative tests"
        self.row = self.review["criteria"]["AC-07"]
        self.row.update(status="COMPLETE", rationale="All required cases have mapped source observations for this structural fixture.",
                        trace="Inspect input, evaluation of the named condition, and its asserted response.",
                        evidence=[self.impl, self.test_ref])
        # Synthetic structural witnesses only: the validator cannot certify their semantic truth.
        self.row["coverage"] = [self.witness(s, p) for s in ("missing/null", "quantifiers") for p in ("positive", "negative")]

    def witness(self, subject, polarity, verdict="SATISFIED"):
        return {"kind": "mandatory_test", "quote": self.quote, "subject": subject,
                "polarity": polarity, "verdict": verdict, "anchor": self.anchor,
                "witness": "Concrete fixture input | Named condition is reached | Assert the observable outcome"}

    def evaluate(self):
        return grade(self.source, self.requirements, self.review, allow_provisional=True, require_coverage=True)

    def test_canonical_checkbox_id_and_heading_parent(self):
        self.assertEqual([r["id"] for r in self.requirements["criteria"]], ["AC-07", "AC-08", "REQ-03"])
        legacy = extract_requirements(self.source)
        self.assertEqual(len(legacy["criteria"]), 2)
        self.assertTrue(all(r["id"].startswith("CHK-") for r in legacy["criteria"]))
        with self.assertRaisesRegex(AuditError, "canonical requirements"):
            init_review(self.source, legacy, coverage=True)
        # Same numbered item in two Markdown forms is one obligation, not two votes.
        raw = copy.deepcopy(self.raw)
        raw["issue"]["body"] += "\nAC-08: Reject invalid conditions.\n"
        self.assertEqual(len(extract_requirements(normalize_source(raw), canonical_ids=True)["criteria"]), 3)
        raw["issue"]["body"] += "\nAC-08: Allow invalid conditions.\n"
        with self.assertRaisesRegex(AuditError, "Conflicting criterion AC-08"):
            extract_requirements(normalize_source(raw), canonical_ids=True)

    def test_complete_requires_each_explicit_subject_and_polarity(self):
        self.assertEqual(self.evaluate()["adjudication_policy"], COVERAGE_POLICY)
        self.row["coverage"] = self.row["coverage"][1:]
        with self.assertRaisesRegex(AuditError, "missing explicit test polarity coverage"):
            self.evaluate()
        self.row["coverage"] = [self.witness("all test cases", p) for p in ("positive", "negative")]
        with self.assertRaisesRegex(AuditError, "missing explicit test polarity coverage"):
            self.evaluate()

    def test_production_code_or_test_name_is_not_a_test_witness(self):
        case = self.row["coverage"][0]
        case["anchor"] = "matcher.py:L1-L2"
        with self.assertRaisesRegex(AuditError, "test/result anchor"):
            self.evaluate()
        case["anchor"] = self.anchor
        case["witness"] = "The matching tests have broad coverage of all required cases."
        with self.assertRaisesRegex(AuditError, "input.*reached predicate/path.*asserted effect"):
            self.evaluate()

    def mark_gap(self):
        self.row["coverage"][1]["verdict"] = "GAP"
        self.row["evidence"].append(self.counter)
        self.row["remaining"] = [f"mandatory_test | {self.quote} | {self.anchor} | Negative case stops before the relevant predicate. | The positive case exercises the predicate but cannot reject incorrect absence."]
        self.row["status"] = "PARTIAL"

    def test_gap_cannot_be_called_complete_and_unknown_stays_unknown(self):
        self.mark_gap()
        report = self.evaluate()
        self.assertEqual(report["summary"]["numeric_delivery_grade_pct"], "25.00")
        self.row["status"] = "COMPLETE"
        self.row["remaining"] = []
        with self.assertRaisesRegex(AuditError, "verdicts imply PARTIAL"):
            self.evaluate()
        self.row["coverage"][1]["verdict"] = "UNKNOWN"
        with self.assertRaisesRegex(AuditError, "verdicts imply UNVERIFIED"):
            self.evaluate()
        self.row["status"] = "UNVERIFIED"
        self.assertEqual(self.evaluate()["summary"]["assessed"], 0)

    def test_same_head_disagreement_and_scope_drift_are_not_progress(self):
        complete = self.evaluate()
        self.mark_gap()
        partial = self.evaluate()
        self.assertEqual(complete["coverage_scope_digest"], partial["coverage_scope_digest"])
        with self.assertRaisesRegex(AuditError, "Same HEAD has divergent semantic verdicts"):
            compare_grades(complete, partial)
        self.row["coverage"].append({"kind": "behavior", "quote": "Header matching is tested", "subject": "header", "polarity": "none", "verdict": "SATISFIED", "anchor": "matcher.py:L1-L2", "witness": "Concrete source observation for this structural fixture."})
        with self.assertRaisesRegex(AuditError, "coverage scopes differ"):
            compare_grades(partial, self.evaluate())

    def test_v2_cannot_bypass_gate_and_legacy_replay_is_unchanged(self):
        self.row["coverage"] = []
        with self.assertRaisesRegex(AuditError, "needs obligation coverage"):
            grade(self.source, self.requirements, self.review, allow_provisional=True)
        legacy = init_review(self.source, self.requirements)
        with self.assertRaisesRegex(AuditError, "requires a v2 review"):
            grade(self.source, self.requirements, legacy, allow_provisional=True, require_coverage=True)

    def test_short_circuit_negative_is_not_a_null_discriminator(self):
        # A tiny local synthetic oracle: the old negative and positive cases
        # both survive an incorrect missing-as-null implementation.
        def match(body, broken=False):
            if type(body.get("value")) is not int:
                return False
            return body.get("nullable") is None if broken else ("nullable" in body and body["nullable"] is None)
        positive = {"value": 42, "nullable": None}
        masked_negative = {"value": "42", "nullable": None}
        discriminator = {"value": 42}
        for broken in (False, True):
            self.assertTrue(match(positive, broken))
            self.assertFalse(match(masked_negative, broken))
        self.assertFalse(match(discriminator))
        self.assertTrue(match(discriminator, broken=True))
        self.row["coverage"] = [item for item in self.row["coverage"]
                                if (item["subject"], item["polarity"]) != ("missing/null", "negative")]
        with self.assertRaisesRegex(AuditError, "missing explicit test polarity coverage"):
            self.evaluate()

    def test_cli_bundle_verify_freezes_same_canonical_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw.json"
            raw.write_bytes(canonical(self.raw))
            def run(script, *args):
                result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / script), *map(str,args)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            capture = root / "capture"
            run("pr_audit.py", "capture", "--from-json", raw, "--require-coverage", "--out", capture)
            self.assertEqual((capture / "requirements.json").read_bytes(), canonical(self.requirements))
            review = root / "review.json"
            run("pr_audit.py", "init-code-review", "--source", capture / "source.json", "--requirements", capture / "requirements.json", "--require-coverage", "--out", root / "scaffold.json")
            review.write_bytes(canonical(self.review))
            out = root / "bundle"
            run("audit_bundle.py", "--from-json", raw, "--review", review, "--allow-provisional", "--require-review", "--require-coverage", "--out", out)
            self.assertEqual((out / "requirements.json").read_bytes(), canonical(self.requirements))
            run("pr_audit.py", "verify-code-grade", "--source", out / "source.json", "--requirements", out / "requirements.json", "--review", review, "--allow-provisional", "--require-coverage", "--report-json", out / "implementation-grade.json", "--report-md", out / "implementation-grade.md")
