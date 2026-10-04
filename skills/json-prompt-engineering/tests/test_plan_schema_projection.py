from __future__ import annotations
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "plan_schema_projection.py"


class ProjectionPlanTests(unittest.TestCase):
    def test_reports_application_side_constraint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schema = root / "schema.json"
            profile = root / "profile.json"
            schema.write_text(json.dumps({"type": "string", "minLength": 3}), encoding="utf-8")
            profile.write_text(json.dumps({"profile_version": 1, "id": "test", "verified_at": "2026-10-04", "unsupported_keywords": ["minLength"], "requirements": {}}), encoding="utf-8")
            result = subprocess.run(["python3", str(SCRIPT), "--schema", str(schema), "--profile", str(profile)], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["compatibility"], "projection-required")
            self.assertTrue(report["lossy"])
            self.assertEqual(report["application_side_constraints"][0]["keyword"], "minLength")


if __name__ == "__main__":
    unittest.main()
