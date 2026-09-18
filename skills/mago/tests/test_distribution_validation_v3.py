from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_distribution.py"
SPEC = importlib.util.spec_from_file_location("validate_distribution", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DistributionValidationTests(unittest.TestCase):
    def test_output_must_be_external(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target"
            target.mkdir()
            with self.assertRaises(ValueError):
                MODULE.ensure_external_output(target, target / "reports")
            MODULE.ensure_external_output(target, Path(temp) / "external")

    def test_atomic_json_and_sha256_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "report.json"
            MODULE.atomic_write_json(path, {"status": "pass", "value": 1})
            self.assertEqual(json.loads(path.read_text()), {"status": "pass", "value": 1})
            first = MODULE.sha256_file(path)
            second = MODULE.sha256_file(path)
            self.assertEqual(first, second)

    def test_safe_extract_rejects_multiple_roots(self) -> None:
        import zipfile
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "bad.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("one/SKILL.md", "x")
                zf.writestr("two/file.txt", "x")
            with self.assertRaises(ValueError):
                MODULE.safe_extract(archive, Path(temp) / "out")

    def test_run_command_records_failure(self) -> None:
        import sys
        with tempfile.TemporaryDirectory() as temp:
            result = MODULE.run_command(
                "expected-failure",
                [sys.executable, "-c", "raise SystemExit(3)"],
                Path(temp),
                timeout=10,
            )
            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["exit_code"], 3)
            self.assertFalse(result["timed_out"])


if __name__ == "__main__":
    unittest.main()
