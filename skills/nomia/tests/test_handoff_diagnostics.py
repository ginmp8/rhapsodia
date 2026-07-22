import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ecosystem_handoff as handoff
spec = importlib.util.spec_from_file_location("evaluate_governance_diagnostics", ROOT / "scripts" / "evaluate_governance.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
AS_OF = datetime(2026, 7, 20, tzinfo=timezone.utc)


class HandoffDiagnosticTests(unittest.TestCase):
    def envelope(self):
        payload = {
            "feature_key": "demo-feature",
            "outcome": "Outcome",
            "scope_summary": "Scope",
            "owner": "Owner",
            "business_priority": {"level": "high", "owner": "nomia", "source": "roadmap.yaml", "observed_at": AS_OF.isoformat()},
            "dependencies": [],
            "governance_readiness": "ready",
            "candidate_spec_id": "spec-2026-07-20-demo-feature",
            "candidate_spec_id_provenance": "registry/spec-2026-07-20-demo-feature.yaml",
        }
        return handoff.build_envelope(
            direction="nomia_to_mago", payload=payload, source="roadmap.yaml",
            authority="nomia", evidence_refs=["decision-1"],
            observed_at=AS_OF.isoformat(), freshness_days=30, root=ROOT,
        )

    @staticmethod
    def refresh_id(env):
        env["handoff_id"] = handoff.handoff_id_for(env)
        return env

    def test_missing_field_has_actionable_remediation(self):
        env = self.envelope()
        del env["payload"]["outcome"]
        self.refresh_id(env)
        result = mod.validate_handoff(env, AS_OF)
        self.assertEqual(result["status"], "rejected")
        self.assertIn("payload.outcome", result["missing_fields"])
        self.assertTrue(any("authoritative source" in item for item in result["remediation"]))

    def test_technical_content_routes_to_correct_authority(self):
        env = self.envelope()
        env["payload"]["tasks"] = ["Implement migration"]
        self.refresh_id(env)
        result = mod.validate_handoff(env, AS_OF)
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(any("Mago or Magia" in item for item in result["remediation"]))
        self.assertIn("Mago owns planning", result["authority_note"])

    def test_accepted_handoff_does_not_certify_completion(self):
        result = mod.validate_handoff(self.envelope(), AS_OF)
        self.assertEqual(result["status"], "accepted")
        self.assertIn("does not certify technical completion", result["next_action"])

    def test_json_output_is_written_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "handoff.json"
            output = Path(tmp) / "result.json"
            source.write_text(json.dumps(self.envelope()), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "evaluate_governance.py"), "--handoff", str(source), "--as-of", AS_OF.isoformat(), "--json-output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
