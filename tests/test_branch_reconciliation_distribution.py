"""RhapsodIA 0.16.0 distribution guard for the Branch Reconciliation skill."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "branch-reconciliation"
VERSION = "0.1.0"


class BranchReconciliationDistributionTests(unittest.TestCase):
    def test_complete_independent_package(self):
        paths = (
            "SKILL.md", "VERSION", "CHANGELOG.md", "SOURCE.md",
            "agents/openai.yaml", "evals/activation-scenarios.json",
            "references/manual-resolution.md",
            "references/validation-and-remote.md",
            "scripts/reconcile.py", "tests/test_reconcile.py",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((SKILL / path).is_file(), path)
        self.assertEqual((SKILL / "VERSION").read_text(encoding="utf-8").strip(), VERSION)
        self.assertIn(f"## [{VERSION}]", (SKILL / "CHANGELOG.md").read_text(encoding="utf-8"))
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: branch-reconciliation\n"))
        self.assertLessEqual(len(next(line.split(": ", 1)[1] for line in text.splitlines() if line.startswith("description: "))), 500)
        self.assertIn("single-parent", text)
        self.assertIn("references/manual-resolution.md", text)
        self.assertIn("references/validation-and-remote.md", text)
        self.assertIn("source-only", text)
        self.assertIn("destination-only", text)
        self.assertIn("explicit authorization", text)

    def test_eval_fixtures_have_positive_and_negative_activation(self):
        fixture = json.loads((SKILL / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
        self.assertEqual(fixture["skill"], "branch-reconciliation")
        self.assertEqual(fixture["evidence_status"], "planned-not-executed")
        kinds = {case["kind"] for case in fixture["scenarios"]}
        self.assertTrue({"activate", "do-not-activate", "clarify-authority"}.issubset(kinds))

    def test_helper_is_portable_stdlib_cli(self):
        for args in (("--help",), ("plan", "--help"), ("apply", "--help")):
            with self.subTest(args=args):
                run = subprocess.run(
                    [sys.executable, "-I", "-S", "-B", str(SKILL / "scripts/reconcile.py"), *args],
                    capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertIn("usage:", run.stdout)

    def test_distribution_metadata_and_ci_are_wired(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        release = (ROOT / "docs/releases/0.16.0.md").read_text(encoding="utf-8")
        history = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("69 independently versioned Agent Skills", readme)
        self.assertIn("Branch Reconciliation", release)
        self.assertIn("62 to 69 Skills", release)
        self.assertIn("Branch Reconciliation v0.1.0", history)
        for workflow in ("helix-release.yml", "runtime-portability.yml"):
            text = (ROOT / ".github/workflows" / workflow).read_text(encoding="utf-8")
            self.assertIn("skills/branch-reconciliation/tests", text)
            self.assertIn("test_branch_reconciliation_distribution.py", text)


if __name__ == "__main__":
    unittest.main()
