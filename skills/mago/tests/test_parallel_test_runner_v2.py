from __future__ import annotations

import tempfile
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


if __name__ == "__main__":
    unittest.main()
