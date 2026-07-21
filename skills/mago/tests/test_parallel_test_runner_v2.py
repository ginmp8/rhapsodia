from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_test_suite import run_suite  # noqa: E402


class ParallelTestRunnerV2Tests(unittest.TestCase):
    def make_test(self, directory: Path, name: str, body: str) -> None:
        (directory / name).write_text(body, encoding="utf-8")

    def test_parallel_runner_counts_isolated_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-runner-") as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            content = "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\nif __name__ == '__main__': unittest.main()\n"
            self.make_test(tests, "test_a.py", content)
            self.make_test(tests, "test_b.py", content)
            result = run_suite(root, tests, jobs=2, timeout=10)
            self.assertEqual(result["status"], "pass", result)
            self.assertEqual(result["test_count"], 2)
            self.assertEqual(result["file_count"], 2)

    def test_timeout_is_reported_as_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-runner-timeout-") as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            self.make_test(tests, "test_slow.py", "import time\ntime.sleep(5)\n")
            result = run_suite(root, tests, jobs=1, timeout=1)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(result["results"][0]["timed_out"])
            self.assertEqual(result["results"][0]["termination_reason"], "per-file-timeout")

    def test_total_timeout_emits_partial_result_and_reaps_child(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-runner-total-timeout-") as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            pid_path = root / "child.pid"
            self.make_test(
                tests,
                "test_slow.py",
                "import os, pathlib, time\n"
                f"pathlib.Path({str(pid_path)!r}).write_text(str(os.getpid()))\n"
                "time.sleep(30)\n",
            )
            checkpoints: list[dict] = []
            result = run_suite(
                root,
                tests,
                jobs=1,
                timeout=20,
                total_timeout=2,
                checkpoint=lambda payload: checkpoints.append(payload),
            )
            self.assertEqual(result["status"], "fail")
            self.assertTrue(result["total_timed_out"])
            self.assertEqual(result["stop_reason"], "total-timeout")
            self.assertTrue(checkpoints)
            self.assertIn("running", {item["status"] for item in checkpoints})
            pid = int(pid_path.read_text(encoding="utf-8"))
            for _ in range(20):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            else:
                self.fail(f"timed-out child process still exists: {pid}")


if __name__ == "__main__":
    unittest.main()
