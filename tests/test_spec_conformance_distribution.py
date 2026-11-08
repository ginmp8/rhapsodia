"""Portable distribution and routing regressions for spec-conformance auditing."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
COORD = ROOT / "skills" / "audit-spec-implementation"
PACKAGES = {
    "audit-spec-implementation": "0.3.0",
    "spec-criteria-extractor": "0.2.0",
    "implementation-reachability-auditor": "0.2.0",
    "causal-behavior-auditor": "0.2.0",
    "verification-oracle-auditor": "0.2.0",
    "regression-parity-auditor": "0.2.0",
}


class SpecConformanceDistributionTests(unittest.TestCase):
    def test_all_six_packages_preserve_source_and_metadata(self):
        for name, version in PACKAGES.items():
            with self.subTest(skill=name):
                base = ROOT / "skills" / name
                for relative in ("SKILL.md", "VERSION", "CHANGELOG.md", "SOURCE.md",
                                 "evals/activation-scenarios.json", "agents/openai.yaml"):
                    self.assertTrue((base / relative).is_file(), f"{name}: missing {relative}")
                self.assertEqual((base / "VERSION").read_text(encoding="utf-8").strip(), version)
                self.assertIn(f"## [{version}]", (base / "CHANGELOG.md").read_text(encoding="utf-8"))
                entry = (base / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(f"name: {name}", entry)
                self.assertIn("description:", entry)
                fixture = json.loads((base / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
                self.assertEqual(fixture["skill"], name)
                self.assertEqual(fixture["evidence_status"], "planned-not-executed")

    def test_coordinator_retains_dispatch_and_validation_resources(self):
        for relative in ("references/skill-dispatch.json",
                         "references/evidence-method.md",
                         "references/external-skill-integration.md",
                         "references/report-contract.md",
                         "references/specialist-handoffs.md",
                         "scripts/plan_audit.py",
                         "scripts/validate_report.py",
                         "scripts/validate_stage_receipt.py",
                         "tests/test_validator.py"):
            with self.subTest(path=relative):
                self.assertTrue((COORD / relative).is_file(), relative)
        registry = json.loads((COORD / "references/skill-dispatch.json").read_text(encoding="utf-8"))
        self.assertEqual([stage["id"] for stage in registry["stages"]],
                         ["criteria", "implementation", "causal", "verification", "parity"])
        for stage in registry["stages"]:
            self.assertIn(stage["adapter"], PACKAGES)
        self.assertTrue({"reverse-engineering", "causal-flow-comprehension", "test-oracle-engineering"}
                        .issubset({specialist for stage in registry["stages"]
                                   for specialist in stage["external"]}))

    def test_plan_never_claims_invocation_or_test_execution(self):
        path = COORD / "scripts/plan_audit.py"
        spec = importlib.util.spec_from_file_location("spec_conformance_plan", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        outcome = module.plan({
            "base_sha": "frozen-base", "head_sha": "frozen-head",
            "available_skills": ["reverse-engineering", "causal-flow-comprehension",
                                 "test-oracle-engineering"],
            "risk_factors": ["authorization"], "needs_parity": True,
        })
        self.assertEqual(outcome["status"], "planned")
        self.assertFalse(outcome["authorized_test_execution"])
        self.assertTrue(all(stage["actually_invoked"] is False for stage in outcome["stages"]))
        self.assertFalse(next(stage for stage in outcome["stages"] if stage["stage"] == "verification")
                         ["test_execution_observed"])
        self.assertEqual(module.plan({"base_sha": "one"})["status"], "blocked")

    def test_coordinator_scripts_use_portable_stdlib_cli(self):
        for filename in ("plan_audit.py", "validate_report.py", "validate_stage_receipt.py"):
            with self.subTest(script=filename):
                proc = subprocess.run(
                    [sys.executable, "-I", "-S", "-B", str(COORD / "scripts" / filename), "--help"],
                    capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
