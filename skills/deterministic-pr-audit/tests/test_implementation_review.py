"""Frozen implementation grades use source code, NEVER CI outcomes."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_core import AuditError, canonical, digest, extract_requirements, normalize_source
from implementation_review import (
    REVIEW_SCHEMA, SNAPSHOTS_SCHEMA, blob_sha, compare_grades, grade, init_review, markdown_grade,
)
from audit_bundle import build_bundle


def shell(*args, cwd=None):
    r = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if r.returncode:
        raise AssertionError(f"{args}: {r.stderr}")
    return r.stdout.strip()


class SourceCodeGradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        shell("git", "init", "-q", str(self.repo))
        shell("git", "config", "user.email", "audit@example.invalid", cwd=self.repo)
        shell("git", "config", "user.name", "Audit fixture", cwd=self.repo)
        self.code = """def approve(record):
    if not record or not record.get('verified'):
        return 'blocked'
    return 'approved'


def old_mode(value):
    return value
"""
        (self.repo / "app.py").write_text(self.code, encoding="utf-8")
        shell("git", "add", "app.py", cwd=self.repo)
        shell("git", "commit", "-qm", "baseline implementation", cwd=self.repo)
        self.head = shell("git", "rev-parse", "HEAD", cwd=self.repo)
        self.sha = blob_sha(self.code.encode())
        self.raw = {
            "repository": "test/code-review",
            "pull_request": {"number": 7, "head_sha": self.head, "base_sha": "a" * 40, "files": ["app.py"]},
            "issue": {"number": 11, "body": "\n".join([
                "## Acceptance criteria", "AC-01: Reject unverified approvals.",
                "AC-02: Preserve legacy mode with backwards compatibility.",
                "AC-03: Support durable operations after restart.",
                "AC-04: Validate a second independent behavior.",
                "REQ-01: Deliver stable gated approval semantics.",
            ]), "comments": []},
        }
        self.source = normalize_source(self.raw)
        self.req = extract_requirements(self.source)
        self.review = init_review(self.source, self.req)

    def ref(self, role="implementation", start=1, end=4, sha=None, path="app.py"):
        return {"path": path, "blob_sha": sha or self.sha, "line_start": start,
                "line_end": end, "role": role,
                "claim": "The pinned entrypoint validates this behavior through its result path."}

    def assess(self, ident="AC-01", status="COMPLETE", *, remaining=None, evidence=None):
        self.review["criteria"][ident] = {
            "status": status,
            "rationale": "The exact pinned implementation is traced through validation, branch, and final return paths.",
            "trace": "approve receives the record, checks verified, rejects invalid data and returns approved only when verified.",
            "evidence": evidence if evidence is not None else [self.ref()],
            "remaining": remaining if remaining is not None else ([] if status == "COMPLETE" else ["The required integration path remains incomplete."]),
        }

    def test_requires_review_and_proves_git_identity(self):
        self.assess()
        report = grade(self.source, self.req, self.review, repo_path=self.repo)
        self.assertEqual(report["code_provenance"], "git_commit_verified")
        self.assertEqual(report["summary"]["total"], 4)
        self.assertEqual(report["summary"]["assessed"], 1)
        self.assertEqual(report["summary"]["development_progress_assessed_pct"], "100.00")
        self.assertEqual(report["summary"]["functional_completion_lower_pct"], "25.00")
        self.assertEqual(report["summary"]["functional_completion_upper_pct"], "100.00")
        self.assertFalse(report["ci_affects_grade"])
        self.assertEqual(report["parent_requirements"]["total"], 1)
        self.assertIn("AC-01", markdown_grade(report))

    def test_mixed_delivery_fraction_is_not_test_pass_rate(self):
        self.assess("AC-01", "COMPLETE")
        self.assess("AC-02", "PARTIAL")
        self.assess("AC-03", "MISSING", evidence=[self.ref(role="counterexample")])
        report = grade(self.source, self.req, self.review, repo_path=self.repo)
        self.assertEqual(report["summary"]["assessed"], 3)
        self.assertEqual(report["summary"]["development_progress_assessed_pct"], "50.00")
        self.assertEqual(report["summary"]["functional_completion_assessed_pct"], "33.33")
        self.assertEqual(report["summary"]["development_progress_lower_pct"], "37.50")
        self.assertEqual(report["summary"]["development_progress_upper_pct"], "62.50")
        self.assertEqual(report["summary"]["assessed_pct"], "75.00")
        self.assertEqual(report["parent_requirements"]["assessed"], 0)

    def test_same_frozen_inputs_replay_identical_even_with_ci_failure(self):
        self.assess()
        first = grade(self.source, self.req, self.review, repo_path=self.repo)
        # A failing CI summary is intentionally not an accepted scoring input.
        self.review["ci"] = {"state": "failure"}
        with self.assertRaisesRegex(AuditError, "forbids extra fields"):
            grade(self.source, self.req, self.review, repo_path=self.repo)
        del self.review["ci"]
        (self.repo / "app.py").write_text("def approve(record): return 'broken'\n", encoding="utf-8")
        second = grade(self.source, self.req, self.review, repo_path=self.repo)
        self.assertEqual(canonical(first), canonical(second))

    def test_stale_or_fake_source_ref_is_rejected(self):
        self.assess()
        self.review["criteria"]["AC-01"]["evidence"][0]["blob_sha"] = "f" * 40
        with self.assertRaisesRegex(AuditError, "blob SHA mismatch"):
            grade(self.source, self.req, self.review, repo_path=self.repo)

    def test_missing_no_counterexample_is_not_negative_proof(self):
        self.assess("AC-03", "MISSING")
        with self.assertRaisesRegex(AuditError, "observed negative code path"):
            grade(self.source, self.req, self.review, repo_path=self.repo)

    def test_complete_requires_code_not_pr_text(self):
        self.assess()
        self.review["criteria"]["AC-01"]["evidence"] = [self.ref(role="test")]
        with self.assertRaisesRegex(AuditError, "source-code implementation/result trace"):
            grade(self.source, self.req, self.review, repo_path=self.repo)

    def test_partial_requires_specific_remaining_behavior(self):
        self.assess("AC-02", "PARTIAL", remaining=[])
        with self.assertRaisesRegex(AuditError, "must identify"):
            grade(self.source, self.req, self.review, repo_path=self.repo)

    def test_no_source_file_no_numeric_grade(self):
        self.assess()
        with self.assertRaisesRegex(AuditError, "SOURCE_REQUIRED"):
            grade(self.source, self.req, self.review)
        self.review["criteria"]["AC-01"] = init_review(self.source, self.req)["criteria"]["AC-01"]
        result = grade(self.source, self.req, self.review)
        self.assertIsNone(result["summary"]["development_progress_assessed_pct"])
        self.assertEqual(result["summary"]["counts"]["UNVERIFIED"], 4)

    def test_connector_blob_snapshots_work_without_git(self):
        self.assess()
        snapshots = {"schema": SNAPSHOTS_SCHEMA, "source_digest": digest(self.source),
                     "head_sha": self.head, "files": [{"path": "app.py", "blob_sha": self.sha, "content": self.code}]}
        result = grade(self.source, self.req, self.review, snapshots=snapshots)
        self.assertEqual(result["summary"]["development_progress_assessed_pct"], "100.00")
        self.assertIn("unverified_tree_membership", result["code_provenance"])
        snapshots["files"][0]["content"] = "tampered"
        with self.assertRaisesRegex(AuditError, "blob integrity failure"):
            grade(self.source, self.req, self.review, snapshots=snapshots)

    def test_reject_changed_normative_issue(self):
        self.assess()
        source = copy.deepcopy(self.source)
        source["issue"]["body"] = "AC-01: Changed spec"
        with self.assertRaisesRegex(AuditError, "not bound to the current normative specification"):
            grade(source, self.req, self.review, repo_path=self.repo)

    def test_full_40_criteria_matrix_without_ci(self):
        other = copy.deepcopy(self.raw)
        other["issue"]["body"] = "\n".join(f"AC-{i:02d}: Implement behavior number {i}" for i in range(1, 41))
        source = normalize_source(other)
        requirements = extract_requirements(source)
        review = init_review(source, requirements)
        for i in range(1, 41):
            review["criteria"][f"AC-{i:02d}"] = {
                "status": "COMPLETE" if i <= 20 else "PARTIAL", 
                "rationale": "The exact pinned implementation has been examined against this acceptance requirement.",
                "trace": "The pinned code enters approve, rejects invalid records, and finishes through the verified return.",
                "evidence": [self.ref()],
                "remaining": [] if i <= 20 else ["The next required behavior remains unfinished."],
            }
        result = grade(source, requirements, review, repo_path=self.repo)
        self.assertEqual(result["summary"]["total"], 40)
        self.assertEqual(result["summary"]["development_progress_assessed_pct"], "75.00")
        self.assertEqual(result["summary"]["functional_completion_assessed_pct"], "50.00")

    def test_comparison_uses_fixed_scope_and_no_ci(self):
        self.assess("AC-01", "COMPLETE")
        self.assess("AC-02", "PARTIAL")
        left = grade(self.source, self.req, self.review, repo_path=self.repo)
        self.assess("AC-02", "COMPLETE")
        right = grade(self.source, self.req, self.review, repo_path=self.repo)
        comparison = compare_grades(left, right)
        self.assertEqual(comparison["progress_delta_points"], "25.00")
        self.assertEqual(comparison["transitions"], [{"id": "AC-02", "before": "PARTIAL", "after": "COMPLETE"}])
        self.review["criteria"]["AC-02"] = init_review(self.source, self.req)["criteria"]["AC-02"]
        incomplete = grade(self.source, self.req, self.review, repo_path=self.repo)
        with self.assertRaisesRegex(AuditError, "assessed code coverage differs"):
            compare_grades(left, incomplete)

    def test_cli_and_bundle_include_code_grade(self):
        self.assess()
        src, req, review = [self.root / x for x in ("source.json", "req.json", "review.json")]
        src.write_bytes(canonical(self.source))
        req.write_bytes(canonical(self.req))
        review.write_bytes(canonical(self.review))
        cli = [sys.executable, str(ROOT / "scripts" / "pr_audit.py")]
        output = self.root / "score"
        shell(*cli, "code-grade", "--source", str(src), "--requirements", str(req),
              "--review", str(review), "--repo-path", str(self.repo), "--out", str(output))
        shell(*cli, "verify-code-grade", "--source", str(src), "--requirements", str(req),
              "--review", str(review), "--repo-path", str(self.repo),
              "--report-json", str(output / "implementation-grade.json"),
              "--report-md", str(output / "implementation-grade.md"))
        bundle = self.root / "bundle"
        build_bundle(source_input=self.raw, output=bundle, review=self.review, repo_path=self.repo)
        self.assertTrue((bundle / "implementation-grade.md").exists())
        grade_report = json.loads((bundle / "implementation-grade.json").read_text())
        self.assertEqual(grade_report["summary"]["development_progress_assessed_pct"], "100.00")


if __name__ == "__main__":
    unittest.main()
