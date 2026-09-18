import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("guide_intake", ROOT / "scripts" / "guide_intake.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class GuidedIntakeTests(unittest.TestCase):
    def test_minimal_intake_preserves_unknowns_and_prioritizes_questions(self):
        result = mod.build_guidance({"low_risk": True})
        self.assertEqual(result["profile"], "quick")
        self.assertEqual(result["lifecycle"], "intake")
        self.assertEqual(result["mode"], "delivery-intake")
        self.assertEqual(len(result["blocking_questions"]), 3)
        self.assertIn("owner", result["unknown_fields"])
        self.assertEqual(result["authority"], "non_authoritative_guidance")

    def test_governed_trigger_overrides_quick_request(self):
        result = mod.build_guidance(
            {
                "profile": "quick",
                "problem": "Policy change",
                "outcome": "Compliant onboarding",
                "evidence": "policy-2026-07",
                "risk_triggers": ["regulatory"],
            }
        )
        self.assertEqual(result["profile"], "governed")
        self.assertEqual(result["escalation_reasons"], ["regulatory"])

    def test_ready_handoff_is_guidance_not_certification(self):
        result = mod.build_guidance(
            {
                "problem": "Manual triage",
                "outcome": "Reduce decision latency",
                "evidence": "intake-42",
                "scope": "governance workflow",
                "requester": "Ops",
                "owner": "Delivery",
                "decision_needed": False,
            }
        )
        self.assertTrue(result["mago_handoff_candidate"]["ready_for_validation"])
        self.assertEqual(result["next_responsible_skill"], "mago")
        self.assertIn("guidance only", result["mago_handoff_candidate"]["note"])

    def test_repository_write_requires_runtime_identity_and_provenance(self):
        result = mod.build_guidance(
            {
                "problem": "Create status",
                "outcome": "Visible ownership",
                "evidence": "issue-12",
                "repository_write": True,
                "spec_id": "spec-2026-07-21-visible-ownership",
            }
        )
        self.assertFalse(result["repository_write"]["ready"])
        self.assertIn("spec_id_provenance", result["repository_write"]["missing_fields"])
        self.assertTrue(result["identity_issues"])

    def test_cli_writes_same_json_it_prints(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "intake.yaml"
            output = Path(tmp) / "guidance.json"
            source.write_text("problem: Demo\noutcome: Decide\nevidence: issue-1\n", encoding="utf-8")
            self.assertEqual(mod.main([str(source), "--output", str(output)]), 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "pass")


if __name__ == "__main__":
    unittest.main()
