#!/usr/bin/env python3
"""Run each script-style structural suite under unittest discovery."""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT_SUITES = sorted(
    path.name for path in HERE.glob("test_*.py") if path.name != Path(__file__).name
)


class ScriptSuites(unittest.TestCase):
    def test_script_suites_discovered(self):
        self.assertTrue(SCRIPT_SUITES)

    def test_each_script_suite_passes(self):
        for name in SCRIPT_SUITES:
            with self.subTest(suite=name):
                result = subprocess.run(
                    [sys.executable, "-I", "-S", "-B", str(HERE / name)],
                    capture_output=True, text=True, timeout=120, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
