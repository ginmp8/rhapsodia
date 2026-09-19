from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
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
                    {"id": "first", "area": "requirements-design-validation", "command": ["{python}", "-c", "print('first')"], "expected_exit": 0},
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
            self.assertEqual(report["execution_model"], "isolated_bounded_subprocesses")

    def test_total_timeout_writes_failure_report_and_reaps_scenario(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-harness-timeout-") as tmp:
            root = Path(tmp)
            suite = root / "suite.json"
            output = root / "report.json"
            pid_path = root / "scenario.pid"
            suite.write_text(json.dumps({
                "schema_version": 1,
                "measurement_kind": "deterministic_executable_evidence",
                "scenarios": [{
                    "id": "slow",
                    "area": "execution-resume",
                    "command": [
                        "{python}",
                        "-c",
                        f"import os,pathlib,time;pathlib.Path({str(pid_path)!r}).write_text(str(os.getpid()));time.sleep(30)",
                    ],
                    "expected_exit": 0,
                }],
            }), encoding="utf-8")
            run = subprocess.run([
                sys.executable, "-B", str(SCRIPT), "--target", str(ROOT),
                "--suite", str(suite), "--output", str(output),
                "--timeout", "20", "--total-timeout", "3",
            ], cwd=str(ROOT), text=True, capture_output=True, check=False, timeout=15)
            self.assertNotEqual(run.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "fail")
            self.assertTrue(report["total_timed_out"])
            self.assertEqual(report["stop_reason"], "total-timeout")
            pid = int(pid_path.read_text(encoding="utf-8"))
            for _ in range(20):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            else:
                self.fail(f"timed-out scenario process still exists: {pid}")


if __name__ == "__main__":
    unittest.main()
