from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_sdd_evidence_harness.py"


class ParallelEvidenceHarnessV2Tests(unittest.TestCase):
    def test_parallel_harness_preserves_declared_order_and_results(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-harness-") as tmp:
            root = Path(tmp)
            suite = root / "suite.json"
            output = root / "report.json"
            suite.write_text(json.dumps({
                "schema_version": 1,
                "measurement_kind": "deterministic_executable_evidence",
                "scenarios": [
                    {"id": "first", "area": "validation" if False else "requirements-design-validation", "command": ["{python}", "-c", "print('first')"], "expected_exit": 0},
                    {"id": "second", "area": "product-ecosystem", "command": ["{python}", "-c", "print('second')"], "expected_exit": 0},
                ],
            }), encoding="utf-8")
            run = subprocess.run([
                sys.executable, "-B", str(SCRIPT), "--target", str(ROOT),
                "--suite", str(suite), "--output", str(output), "--jobs", "2",
            ], cwd=str(ROOT), text=True, capture_output=True, check=False)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "pass")
            self.assertEqual([item["id"] for item in report["results"]], ["first", "second"])
            self.assertEqual(report["execution_model"], "isolated_parallel_subprocesses")


if __name__ == "__main__":
    unittest.main()
