"""Offline behavioral tests with real Git objects (no GitHub/network dependency)."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pr_audit
from audit_core import (
    AuditError, canonical, compare_reports, digest, extract_requirements,
    init_checks, inspect, markdown_report, normalize_source, score, suggest_paths, validate_checks,
)

CLI = ROOT / "scripts" / "pr_audit.py"


def run(*cmd: str, cwd: Path | None = None) -> str:
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    if p.returncode:
        raise AssertionError(f"Command failed: {cmd}\n{p.stdout}\n{p.stderr}")
    return p.stdout.strip()


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run("git", "init", "-q", str(self.repo))
        run("git", "config", "user.email", "audit@example.invalid", cwd=self.repo)
        run("git", "config", "user.name", "Test", cwd=self.repo)
        (self.repo / "app.py").write_text("FEATURE_ENABLED = True\n", encoding="utf-8")
        (self.repo / "README.md").write_text("hello\n", encoding="utf-8")
        run("git", "add", ".", cwd=self.repo)
        run("git", "commit", "-qm", "init", cwd=self.repo)
        self.head = run("git", "rev-parse", "HEAD", cwd=self.repo)
        self.src = normalize_source({
            "repository": "example/example",
            "pull_request": {"number": 5, "title": "Feature", "head_sha": self.head,
                             "base_sha": "a" * 40, "files": ["app.py", "README.md"]},
            "issue": {"number": 7, "title": "Feature spec",
                      "body": "## Acceptance criteria\n- [ ] README exists\n- [x] feature works\n\nREQ-12: Feature flag is present\n",
                      "comments": [{"id": 12, "body": "AC-08: Unit tests pass"}]},
        })
        self.requirements = extract_requirements(self.src)
        self.plan = init_checks(self.requirements)
        self.ids = [c["id"] for c in self.requirements["criteria"]]
        self.assertEqual(len(self.ids), 4)

    def configure(self) -> None:
        # Two runtime tests and two structural criteria (test runner is deliberately separate)
        for ident, entry in self.plan["requirements"].items():
            if ident == "REQ-12":
                entry["proof_policy"] = "static"
                entry["checks"] = [{"id": "exists", "kind": "contains", "path": "app.py", "text": "FEATURE_ENABLED = True"}]
            elif ident == "AC-08":
                entry["checks"] = [{"id": "unit-test", "kind": "test", "argv": [sys.executable, "-c", "print('pass')"]}]
            elif ident.startswith("CHK-"):
                entry["checks"] = [{"id": "path", "kind": "path_exists", "path": "README.md"}]

    def test_replay_exact_bytes(self):
        self.configure()
        evidence = inspect(self.src, self.requirements, self.plan, self.repo)
        report1 = score(self.src, self.requirements, self.plan, evidence)
        report2 = score(self.src, self.requirements, self.plan, copy.deepcopy(evidence))
        self.assertEqual(canonical(report1), canonical(report2))
        self.assertEqual(markdown_report(report1), markdown_report(report2))
        self.assertEqual(report1["overall"]["counts"], {"PASS": 1, "PARTIAL": 2, "FAIL": 0, "UNVERIFIED": 1, "NOT_APPLICABLE": 0})
        self.assertEqual(report1["overall"]["completion_verified_pct"], "25.00")
        self.assertEqual(report1["overall"]["requirements_mapped_pct"], "100.00")
        self.assertEqual(report1["verdict"], "INCONCLUSIVE")

    def test_checked_boxes_do_not_count_as_done(self):
        other = copy.deepcopy(self.src)
        other["issue"]["body"] = other["issue"]["body"].replace("[x]", "[ ]")
        old = {x["id"]: x["text"] for x in self.requirements["criteria"]}
        new = {x["id"]: x["text"] for x in extract_requirements(other)["criteria"]}
        self.assertEqual(old, new)
        self.assertNotEqual(digest(self.requirements), digest(extract_requirements(other)))  # spec snapshot changed

    def test_git_content_always_from_pinned_sha(self):
        self.configure()
        (self.repo / "app.py").write_text("FEATURE_ENABLED = False\n", encoding="utf-8")
        evidence = inspect(self.src, self.requirements, self.plan, self.repo)
        self.assertEqual(evidence["results"]["REQ-12"]["exists"]["status"], "PASS")
        # The current working tree is not mistaken for frozen head content.

    def test_missing_probe_is_not_pass(self):
        self.configure()
        self.plan["requirements"]["REQ-12"]["checks"] = [{"id": "missing", "kind": "path_exists", "path": "never-created.txt"}]
        evidence = inspect(self.src, self.requirements, self.plan, self.repo)
        report = score(self.src, self.requirements, self.plan, evidence)
        self.assertEqual(next(c for c in report["criteria"] if c["id"] == "REQ-12")["status"], "FAIL")

    def test_unsupplied_static_repository_not_proof(self):
        self.configure()
        evidence = inspect(self.src, self.requirements, self.plan)
        report = score(self.src, self.requirements, self.plan, evidence)
        self.assertEqual(report["overall"]["completion_verified_pct"], "0.00")

    def test_changed_source_or_plan_invalidates_evidence(self):
        self.configure()
        evidence = inspect(self.src, self.requirements, self.plan, self.repo)
        different = copy.deepcopy(self.src)
        different["pull_request"]["body"] += "something"
        with self.assertRaisesRegex(AuditError, "Evidence does not match"):
            score(different, self.requirements, self.plan, evidence)
        altered = copy.deepcopy(self.plan)
        altered["requirements"]["REQ-12"]["weight"] = 2
        with self.assertRaisesRegex(AuditError, "Evidence does not match"):
            score(self.src, self.requirements, altered, evidence)

    def test_conflicting_comment_fails_capture(self):
        src = copy.deepcopy(self.src)
        src["issue"]["comments"].append({"id": "18", "body": "AC-08: A different requirement"})
        with self.assertRaisesRegex(AuditError, "Conflicting criterion"):
            extract_requirements(src)

    def test_path_traversal_and_unsafe_test_shape_rejected(self):
        self.configure()
        self.plan["requirements"]["REQ-12"]["checks"][0]["path"] = "../secret.txt"
        with self.assertRaisesRegex(AuditError, "Unsafe"):
            validate_checks(self.requirements, self.plan)
        self.plan["requirements"]["REQ-12"]["checks"][0]["path"] = "app.py"
        self.plan["requirements"]["AC-08"]["checks"][0]["argv"] = "python -m pytest"
        with self.assertRaisesRegex(AuditError, "argv"):
            validate_checks(self.requirements, self.plan)

    def test_not_applicable_needs_reason(self):
        self.plan["requirements"]["REQ-12"].update({"not_applicable": True, "reason": ""})
        with self.assertRaisesRegex(AuditError, "reason"):
            validate_checks(self.requirements, self.plan)
        self.plan["requirements"]["REQ-12"]["reason"] = "This criterion is inapplicable for Linux-only interface"
        evidence = inspect(self.src, self.requirements, self.plan)
        result = score(self.src, self.requirements, self.plan, evidence)
        self.assertEqual(result["overall"]["eligible_count"], 3)

    def test_comparison_requires_same_plan_and_spec(self):
        self.configure()
        evidence = inspect(self.src, self.requirements, self.plan, self.repo)
        left = score(self.src, self.requirements, self.plan, evidence)
        right = copy.deepcopy(left)
        right["criteria"][0]["status"] = "PASS"
        changes = compare_reports(left, right)
        self.assertEqual(len(changes["changed_requirements"]), 1)
        right["identity"]["checks_digest"] = "bad"
        with self.assertRaisesRegex(AuditError, "Not comparable"):
            compare_reports(left, right)

    def test_cli_end_to_end_offline_and_verify(self):
        source_path = self.root / "source-input.json"
        source_path.write_bytes(canonical(self.src))
        base = [sys.executable, str(CLI)]
        out = self.root / "case"
        run(*base, "capture", "--from-json", str(source_path), "--out", str(out))
        run(*base, "init-checks", "--requirements", str(out / "requirements.json"), "--out", str(out / "checks.json"))
        checks = json.loads((out / "checks.json").read_text())
        checks["requirements"]["REQ-12"]["proof_policy"] = "static"
        checks["requirements"]["REQ-12"]["checks"] = [{"id": "flag", "kind": "contains", "path": "app.py", "text": "FEATURE_ENABLED = True"}]
        (out / "checks.json").write_bytes(canonical(checks))
        common = ["--source", str(out / "source.json"), "--requirements", str(out / "requirements.json"), "--checks", str(out / "checks.json")]
        run(*base, "inspect", *common, "--repo-path", str(self.repo), "--out", str(out / "evidence.json"))
        run(*base, "score", *common, "--evidence", str(out / "evidence.json"), "--out", str(out / "report"))
        bytes_before = (out / "report" / "report.json").read_bytes()
        run(*base, "score", *common, "--evidence", str(out / "evidence.json"), "--out", str(out / "report"))
        self.assertEqual(bytes_before, (out / "report" / "report.json").read_bytes())
        verify = run(*base, "verify", *common, "--evidence", str(out / "evidence.json"),
                     "--report-json", str(out / "report" / "report.json"),
                     "--report-md", str(out / "report" / "report.md"))
        self.assertIn("VERIFIED: byte-identical", verify)
        with (out / "report" / "report.md").open("a") as f:
            f.write("tamper")
        tampered = subprocess.run([*base, "verify", *common, "--evidence", str(out / "evidence.json"),
                                  "--report-json", str(out / "report" / "report.json"),
                                  "--report-md", str(out / "report" / "report.md")], capture_output=True)
        self.assertEqual(tampered.returncode, 2)

    def test_runtime_receipts_and_immutability(self):
        self.configure()
        base = [sys.executable, str(CLI)]
        src, req, plan = self.root / "src.json", self.root / "req.json", self.root / "plan.json"
        src.write_bytes(canonical(self.src))
        req.write_bytes(canonical(self.requirements))
        plan.write_bytes(canonical(self.plan))
        common = ["--source", str(src), "--requirements", str(req), "--checks", str(plan)]
        output = self.root / "exec.json"
        forbidden = subprocess.run([*base, "run-tests", *common, "--repo-path", str(self.repo), "--out", str(output)], capture_output=True)
        self.assertEqual(forbidden.returncode, 2)
        run(*base, "run-tests", *common, "--repo-path", str(self.repo), "--out", str(output), "--execute")
        receipts = json.loads(output.read_text())
        self.assertEqual(receipts["results"]["AC-08/unit-test"]["status"], "PASS")
        evidence = inspect(self.src, self.requirements, self.plan, self.repo, receipts)
        report = score(self.src, self.requirements, self.plan, evidence)
        self.assertEqual(report["overall"]["counts"]["PASS"], 2)
        bad = copy.deepcopy(receipts)
        bad["head_sha"] = "f" * 40
        with self.assertRaisesRegex(AuditError, "Execution receipts do not belong"):
            inspect(self.src, self.requirements, self.plan, self.repo, bad)

    def test_suggestions_are_advisory_and_deterministic(self):
        hints1 = suggest_paths(self.src, self.requirements, self.repo)
        hints2 = suggest_paths(self.src, self.requirements, self.repo)
        self.assertEqual(canonical(hints1), canonical(hints2))
        self.assertIn("never used for completion", hints1["warning"])
        self.assertIn("REQ-12", hints1["candidates"])
        self.assertEqual(score(self.src, self.requirements, self.plan,
                               inspect(self.src, self.requirements, self.plan))["overall"]["completion_verified_pct"], "0.00")

    def test_cli_verify_evidence_against_git(self):
        self.configure()
        src, req, plan, ev = [self.root / n for n in ("source.json", "requirements.json", "checks.json", "evidence.json")]
        for file, data in ((src, self.src), (req, self.requirements), (plan, self.plan)):
            file.write_bytes(canonical(data))
        ev.write_bytes(canonical(inspect(self.src, self.requirements, self.plan, self.repo)))
        common = ["--source", str(src), "--requirements", str(req), "--checks", str(plan)]
        success = run(sys.executable, str(CLI), "verify-evidence", *common,
                      "--repo-path", str(self.repo), "--evidence", str(ev))
        self.assertIn("VERIFIED", success)
        altered = json.loads(ev.read_text())
        altered["results"]["REQ-12"]["exists"]["status"] = "FAIL"
        ev.write_bytes(canonical(altered))
        bad = subprocess.run([sys.executable, str(CLI), "verify-evidence", *common,
                              "--repo-path", str(self.repo), "--evidence", str(ev)], capture_output=True)
        self.assertEqual(bad.returncode, 2)

    def test_fake_gh_capture_includes_issue_comments_and_pr_files(self):
        # Exercise the real capture and subprocess argument construction without
        # launching a shell-dependent .cmd shim or calling the real GitHub API.
        raw_pr = {"number": 5, "title": "Feature", "body": "desc", "head": {"sha": self.head},
                  "base": {"sha": "a" * 40}, "changed_files": 2}
        raw_issue = {"number": 7, "title": "Feature spec", "body": self.src["issue"]["body"],
                     "comments": 1, "updated_at": "2026-11-14T00:00:00Z"}
        data = {"pr": raw_pr, "issue": raw_issue,
                "comments": [{"id": 12, "body": "AC-08: Unit tests pass"}],
                "files": [{"filename": "app.py"}, {"filename": "README.md"}]}
        endpoints = []

        def fake_run(argv, **kwargs):
            self.assertEqual(argv[:2], ["fake-gh", "api"])
            self.assertFalse(kwargs.get("shell", False))
            ep = argv[2]
            endpoints.append(ep)
            if ep == "repos/example/example/pulls/5":
                result = data["pr"]
            elif ep == "repos/example/example/issues/7":
                result = data["issue"]
            elif ep == "repos/example/example/issues/7/comments?per_page=100&page=1":
                result = data["comments"]
            elif ep == "repos/example/example/pulls/5/files?per_page=100&page=1":
                result = data["files"]
            else:
                self.fail(f"Unexpected GitHub request: {ep}")
            return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(result), stderr="")

        target = self.root / "captured"
        argv = ["pr_audit.py", "capture", "--repo", "example/example", "--pr", "5",
                "--issue", "7", "--out", str(target)]
        with patch.object(pr_audit.shutil, "which", return_value="fake-gh"), \
                patch.object(pr_audit.subprocess, "run", side_effect=fake_run), \
                patch.object(sys, "argv", argv):
            for _ in range(2):
                self.assertEqual(pr_audit.main(), 0)
        self.assertEqual(len(endpoints), 12)
        self.assertIn("repos/example/example/issues/7/comments?per_page=100&page=1", endpoints)
        self.assertIn("repos/example/example/pulls/5/files?per_page=100&page=1", endpoints)
        source = json.loads((target / "source.json").read_text())
        requirements = json.loads((target / "requirements.json").read_text())
        self.assertEqual(source["pull_request"]["head_sha"], self.head)
        self.assertEqual(len(source["issue"]["comments"]), 1)
        self.assertEqual(source["pull_request"]["files"], ["README.md", "app.py"])
        self.assertIn("AC-08", [r["id"] for r in requirements["criteria"]])


if __name__ == "__main__":
    unittest.main()
