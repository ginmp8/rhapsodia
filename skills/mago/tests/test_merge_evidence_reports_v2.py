from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "merge_evidence_reports.py"


class MergeEvidenceReportsV2Tests(unittest.TestCase):
    def test_incomplete_shards_are_rejected(self) -> None:
        suite = json.loads((ROOT / "evals" / "sdd-evidence-scenarios.json").read_text())
        with tempfile.TemporaryDirectory(prefix="mago-evidence-merge-") as temp:
            report = Path(temp) / "part.json"
            report.write_text(json.dumps({
                "status": "pass",
                "suite_digest": "wrong",
                "results": [{"id": suite["scenarios"][0]["id"], "status": "pass", "area": suite["scenarios"][0]["area"]}],
            }))
            output = Path(temp) / "merged.json"
            result = subprocess.run([
                sys.executable, "-B", str(SCRIPT), "--target", str(ROOT),
                "--report", str(report), "--output", str(output),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(output.read_text())
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(payload["errors"])


if __name__ == "__main__":
    unittest.main()
