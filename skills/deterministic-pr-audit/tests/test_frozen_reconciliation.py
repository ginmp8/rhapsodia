"""V3 reproducibility contract: synthetic structural cases, not model accuracy claims."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_core import AuditError, canonical, digest, extract_requirements, normalize_source
from implementation_review import FROZEN_POLICY, blob_sha, compare_grades, grade, init_review, markdown_grade
from reproducible_review import freeze_plan, markdown_inventory, prepare_history


class FrozenReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.raw = {"repository": "example/audit", "pull_request": {"number": 3, "head_sha": "a" * 40,
                    "base_sha": "b" * 40, "files": ["source.py"]}, "issue": {"number": 1, "body":
                    "## Acceptance criteria\nAC-01: The first mode accepts enabled and disabled sources.\n"
                    "AC-02: The second mode completes without disabled source quota.\n"
                    "AC-03: The final result preserves the selected sources.\n", "comments": []},
                    "capture": {"method": "offline_input", "issue_completeness": "not_verified"}}
        self.source = normalize_source(self.raw)
        self.req = extract_requirements(self.source, canonical_ids=True)
        self.texts = {c["id"]: c["text"] for c in self.req["criteria"]}
        self.draft = {"criteria": {ident: [{"kind": "behavior", "quote": text, "subject": "main behavior", "polarity": "none"},
                      {"kind": "behavior", "quote": text, "subject": "boundary behavior", "polarity": "none"}]
                      for ident, text in self.texts.items()}}
        self.plan = freeze_plan(self.source, self.req, self.draft)
        self.history = prepare_history("Searched supplied artifacts and current audit workspace; no prior grade available.", [])
        self.review = init_review(self.source, self.req, obligation_plan=self.plan, audit_history=self.history)
        self.code = "def source_quota(enabled, count):\n    return count\n\ndef unrelated():\n    return True\n"
        self.ref = {"path": "source.py", "blob_sha": blob_sha(self.code.encode()), "line_start": 1, "line_end": 2,
                    "role": "implementation", "claim": "Synthetic evidence for a reachable source path."}
        self.anchor = "source.py:L1-L2"

    def adjudicate(self, ident, status="COMPLETE", *, unrelated=False):
        row = self.review["criteria"][ident]
        anchor = "source.py:L4-L5" if unrelated else self.anchor
        ref = {**self.ref, **({"line_start": 4, "line_end": 5} if unrelated else {})}
        row.update(status=status, rationale="Synthetic criterion-level rationale for structural evaluation only.",
                   trace="Synthetic input, entrypoint, guard and observable final source effect.", evidence=[ref], remaining=[])
        for o in row["coverage"]:
            o.update(verdict="SATISFIED", anchor=anchor, witness="Synthetic affirmative source witness for the structural validator.")
        if status == "PARTIAL":
            row["coverage"][0].update(verdict="GAP", witness="Synthetic counterexample shows a mandatory source quota failure.")
            row["evidence"].append({**ref, "role": "counterexample"})
            row["remaining"] = [f"behavior | {self.texts[ident]} | {anchor} | Synthetic observed failing path for the contract. | The other supported path is explicitly present and does not cover this failure."]

    def evaluate(self, **kwargs):
        args = dict(obligation_plan=self.plan, audit_history=self.history, allow_provisional=True, require_coverage=True)
        args.update(kwargs)
        return grade(self.source, self.req, self.review, **args)

    def test_plan_covers_every_criterion_and_unknown_obligation(self):
        self.assertEqual(set(self.plan["criteria"]), set(self.texts))
        self.assertTrue(all(len(r["coverage"]) == 2 for r in self.review["criteria"].values()))
        result = self.evaluate()
        self.assertEqual(result["review_closure"]["state"], "INCOMPLETE")
        self.assertEqual(result["review_closure"]["unknown_obligation_count"], 6)
        self.assertIn("NOT a final audit", markdown_grade(result))
        self.review["criteria"]["AC-01"]["coverage"].pop()
        with self.assertRaisesRegex(AuditError, "scope drift"):
            self.evaluate()

    def test_freeze_rejects_omission_and_candidate_verdict(self):
        draft = copy.deepcopy(self.draft)
        del draft["criteria"]["AC-01"]
        with self.assertRaisesRegex(AuditError, "every canonical"):
            freeze_plan(self.source, self.req, draft)
        draft = copy.deepcopy(self.draft)
        draft["criteria"]["AC-01"][0]["verdict"] = "SATISFIED"
        with self.assertRaisesRegex(AuditError, "no candidate verdicts"):
            freeze_plan(self.source, self.req, draft)
        draft = copy.deepcopy(self.draft)
        draft["criteria"]["AC-01"] = []
        with self.assertRaisesRegex(AuditError, "cannot be empty"):
            freeze_plan(self.source, self.req, draft)

    def test_plan_identity_is_stable_across_candidate_heads_and_order(self):
        draft = copy.deepcopy(self.draft)
        for items in draft["criteria"].values():
            items.reverse()
        changed = copy.deepcopy(self.raw)
        changed["pull_request"]["head_sha"] = "c" * 40
        src = normalize_source(changed)
        req = extract_requirements(src, canonical_ids=True)
        self.assertEqual(self.plan, freeze_plan(src, req, draft))
        altered = copy.deepcopy(self.draft)
        altered["criteria"]["AC-01"][0]["subject"] = "different scope"
        with self.assertRaisesRegex(AuditError, "separately frozen"):
            self.evaluate(obligation_plan=freeze_plan(self.source, self.req, altered))
        with self.assertRaisesRegex(AuditError, "separate frozen"):
            self.evaluate(obligation_plan=None)

    def test_history_inventory_is_frozen_and_required(self):
        with self.assertRaises(AuditError):
            self.evaluate(audit_history=None)
        history = copy.deepcopy(self.history)
        history["search"] += " Changed after initialization."
        with self.assertRaisesRegex(AuditError, "inventory changed"):
            self.evaluate(audit_history=history)

    def test_prior_same_head_disagreement_is_not_a_final_grade(self):
        for ident in self.texts:
            self.adjudicate(ident, unrelated=True)
        previous = self.evaluate()
        self.history["reports"] = [{"format": "json", "content": previous}]
        self.review = init_review(self.source, self.req, obligation_plan=self.plan, audit_history=self.history)
        self.adjudicate("AC-01", "PARTIAL")
        self.adjudicate("AC-02", unrelated=True)
        current = self.evaluate()
        self.assertEqual(current["review_closure"]["state"], "UNRECONCILED")
        leads = current["reconciliation"]["leads"]
        self.assertEqual({lead["criterion"] for lead in leads}, {"AC-01", "AC-03"})
        self.assertEqual(current["summary"]["numeric_delivery_grade_pct"], "50.00")
        with self.assertRaisesRegex(AuditError, "incomplete or unreconciled"):
            compare_grades(previous, current)
        # A resolution needs a real current row anchor. It never changes scores.
        lead = next(x for x in leads if x["criterion"] == "AC-01")
        self.history["resolutions"][lead["id"]] = {"anchor": self.anchor, "rationale": "The earlier verdict omitted a source quota counterexample; the current boundary witness is independently reconsidered."}
        resolved = self.evaluate()
        self.assertEqual(resolved["summary"], current["summary"])
        self.assertEqual(len(resolved["reconciliation"]["unresolved"]), 1)

    def test_shared_counterexample_lead_does_not_automatically_penalize(self):
        self.adjudicate("AC-01", "PARTIAL")
        self.adjudicate("AC-02")
        self.adjudicate("AC-03", unrelated=True)
        report = self.evaluate()
        self.assertEqual(report["review_closure"]["state"], "UNRECONCILED")
        leads = report["reconciliation"]["leads"]
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["kind"], "shared_counterexample")
        self.assertEqual(leads[0]["criterion"], "AC-02")
        self.assertEqual(report["summary"]["counts"]["COMPLETE"], 2)
        self.history["resolutions"][leads[0]["id"]] = {"anchor": "source.py:L4-L5", "rationale": "This deliberately wrong anchor should never be accepted for the affected criterion or evidence."}
        with self.assertRaisesRegex(AuditError, "resolution needs"):
            self.evaluate()
        self.history["resolutions"][leads[0]["id"]]["anchor"] = self.anchor
        self.history["resolutions"][leads[0]["id"]]["rationale"] = "The overlapping guard applies to a different configured source; this synthetic rationale records why the counterexample is not applicable."
        self.assertEqual(self.evaluate()["review_closure"]["state"], "PROVISIONAL")

    def test_legacy_markdown_report_is_only_a_provisional_prior_lead(self):
        self.adjudicate("AC-01")
        old = markdown_grade(self.evaluate())
        inv = markdown_inventory(old)
        self.assertEqual(len(inv["rows"]), 3)
        self.history["reports"] = [{"format": "markdown", "content": old}]
        self.review = init_review(self.source, self.req, obligation_plan=self.plan, audit_history=self.history)
        self.adjudicate("AC-01", "PARTIAL")
        rec = self.evaluate()["reconciliation"]
        self.assertEqual(rec["prior_reports"][0]["scope_identity"], "provisional_markdown_text")
        self.assertEqual(rec["leads"][0]["identity"], "same_head_and_criterion_text_only")

    def test_partial_with_unknown_parts_is_not_complete_audit(self):
        self.adjudicate("AC-01", "PARTIAL")
        # Add a mandatory third obligation to the original plan BEFORE adjudication.
        draft = copy.deepcopy(self.draft)
        draft["criteria"]["AC-01"].append({"kind": "behavior", "quote": self.texts["AC-01"], "subject": "third part", "polarity": "none"})
        self.plan = freeze_plan(self.source, self.req, draft)
        self.review = init_review(self.source, self.req, obligation_plan=self.plan, audit_history=self.history)
        self.adjudicate("AC-01", "PARTIAL")
        self.review["criteria"]["AC-01"]["coverage"][-1]["verdict"] = "UNKNOWN"
        self.adjudicate("AC-02", unrelated=True)
        self.adjudicate("AC-03", unrelated=True)
        result = self.evaluate()
        self.assertEqual(result["summary"]["assessed"], 3)
        self.assertEqual(result["review_closure"]["unknown_obligation_count"], 1)
        self.assertEqual(result["review_closure"]["state"], "INCOMPLETE")

    def test_same_status_different_obligation_is_a_reconciliation_lead(self):
        self.adjudicate("AC-01", "PARTIAL")
        self.adjudicate("AC-02", unrelated=True)
        self.adjudicate("AC-03", unrelated=True)
        previous = self.evaluate()
        self.history["reports"] = [{"format": "json", "content": previous}]
        self.review = init_review(self.source, self.req, obligation_plan=self.plan, audit_history=self.history)
        self.adjudicate("AC-01", "PARTIAL")
        self.adjudicate("AC-02", unrelated=True)
        self.adjudicate("AC-03", unrelated=True)
        coverage = self.review["criteria"]["AC-01"]["coverage"]
        coverage[0]["verdict"], coverage[1]["verdict"] = coverage[1]["verdict"], coverage[0]["verdict"]
        current = self.evaluate()
        self.assertEqual(current["summary"], previous["summary"])
        self.assertEqual([l["kind"] for l in current["reconciliation"]["leads"]], ["prior_obligation", "prior_obligation"])
        self.assertEqual(current["review_closure"]["state"], "UNRECONCILED")

    def test_prior_resolution_is_invalidated_when_current_evidence_changes(self):
        self.adjudicate("AC-01", "PARTIAL")
        self.adjudicate("AC-02")
        self.adjudicate("AC-03", unrelated=True)
        lead = self.evaluate()["reconciliation"]["leads"][0]
        self.history["resolutions"][lead["id"]] = {"anchor": self.anchor, "rationale": "The overlapping source guard is not applicable to the second configured path, as demonstrated by the cited branch."}
        self.assertEqual(self.evaluate()["review_closure"]["state"], "PROVISIONAL")
        self.review["criteria"]["AC-02"]["trace"] += " New material trace detail."
        with self.assertRaisesRegex(AuditError, "Stale or unknown"):
            self.evaluate()

    def test_missing_named_polarity_is_rejected_even_before_code(self):
        raw = copy.deepcopy(self.raw)
        raw["issue"]["body"] += "AC-04: Missing/null and quantifiers have positive and negative tests.\n"
        source = normalize_source(raw)
        req = extract_requirements(source, canonical_ids=True)
        draft = copy.deepcopy(self.draft)
        quote = "Missing/null and quantifiers have positive and negative tests."
        draft["criteria"]["AC-04"] = [{"kind": "mandatory_test", "quote": quote, "subject": subject, "polarity": polarity}
                                        for subject in ("missing/null", "quantifiers") for polarity in ("positive", "negative")]
        self.assertEqual(len(freeze_plan(source, req, draft)["criteria"]["AC-04"]), 4)
        draft["criteria"]["AC-04"].pop()
        with self.assertRaisesRegex(AuditError, "lacks explicit test polarity"):
            freeze_plan(source, req, draft)

    def test_cli_roundtrip_and_bundle_members(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def put(name, value):
                p = root / name
                p.write_bytes(canonical(value))
                return p
            def run(script, *args):
                proc = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / script), *map(str, args)], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            raw = put("source-input.json", self.raw)
            capture = root / "capture"
            run("pr_audit.py", "capture", "--from-json", raw, "--require-coverage", "--out", capture)
            src, req = capture / "source.json", capture / "requirements.json"
            plan, history = root / "obligation-plan.json", root / "audit-history.json"
            run("pr_audit.py", "freeze-obligations", "--source", src, "--requirements", req, "--draft", put("draft.json", self.draft), "--out", plan)
            run("pr_audit.py", "prepare-audit-history", "--search", self.history["search"], "--out", history)
            common = ["--source", src, "--requirements", req, "--obligation-plan", plan, "--audit-history", history]
            run("pr_audit.py", "init-code-review", *common, "--out", root / "scaffold.json")
            self.assertEqual(json.loads((root / "scaffold.json").read_text()), self.review)
            self.adjudicate("AC-01")
            review = put("review.json", self.review)
            out = root / "bundle"
            run("audit_bundle.py", "--from-json", raw, "--review", review, "--obligation-plan", plan, "--audit-history", history,
                "--require-review", "--require-coverage", "--allow-provisional", "--out", out)
            report = json.loads((out / "implementation-grade.json").read_text())
            self.assertEqual(report["adjudication_policy"], FROZEN_POLICY)
            self.assertEqual(report["review_closure"]["state"], "INCOMPLETE")
            with ZipFile(out / "audit-bundle.zip") as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(z.read("obligation-plan.json"), plan.read_bytes())
                self.assertEqual(z.read("audit-history.json"), history.read_bytes())
            run("pr_audit.py", "verify-code-grade", *common, "--review", review, "--allow-provisional", "--require-coverage",
                "--report-json", out / "implementation-grade.json", "--report-md", out / "implementation-grade.md")
