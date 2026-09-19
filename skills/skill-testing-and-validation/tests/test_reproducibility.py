from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from classify_failure import classify  # noqa: E402
from discover_commands import discover  # noqa: E402
from environment_fingerprint import fingerprint  # noqa: E402
from run_gate import make_receipt  # noqa: E402
from validate_protected_paths import validate as validate_protected  # noqa: E402


class ReproducibilityTests(unittest.TestCase):
    def test_command_selection_has_fixed_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text(json.dumps({"scripts": {"compile": "x", "build": "y", "test:ci": "x", "test": "y"}}), encoding="utf-8")
            (root / "demo.csproj").write_text("<Project></Project>\n", encoding="utf-8")
            result = discover(root)
            self.assertEqual("npm run build", result["selected"]["build"]["command"])
            self.assertEqual("npm test", result["selected"]["test"]["command"])
            self.assertIn("npm run compile", [c["command"] for c in result["candidates"]])
            self.assertIn("dotnet build", [c["command"] for c in result["candidates"]])

    def test_discovery_is_repeatable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text(json.dumps({"scripts": {"build": "echo x"}}), encoding="utf-8")
            self.assertEqual(discover(root), discover(root))

    def test_unittest_discovery_targets_tests_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_demo.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n", encoding="utf-8")
            result = discover(root)
            self.assertEqual([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], result["selected"]["test"]["argv"])

    def test_environment_fingerprint_has_no_timestamp_and_repeats(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = fingerprint(root, ["make"])
            second = fingerprint(root, ["make"])
            self.assertEqual(first, second)
            self.assertNotIn("timestamp", first)

    def test_failure_classification_environment_overrides_gate(self) -> None:
        result = classify("command not found", gate="test", exit_code=1)
        self.assertEqual("environment", result["category"])
        self.assertEqual("environment/command-missing", result["code"])

    def test_failure_classification_uses_gate_for_opaque_failure(self) -> None:
        result = classify("opaque failure", gate="validator", exit_code=9)
        self.assertEqual("validator", result["category"])
        self.assertEqual(9, result["exit_code"])

    def test_runner_preserves_exit_code_and_rerun_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            script = root / "gate.py"
            script.write_text("import sys\nsys.exit(5)\n", encoding="utf-8")
            argv = [sys.executable, str(script)]
            first, _ = make_receipt(root, "test", argv, True, 30)
            script.write_text("print('ok')\n", encoding="utf-8")
            second, _ = make_receipt(root, "test", argv, True, 30)
            self.assertEqual(5, first["exit_code"])
            self.assertEqual(0, second["exit_code"])
            self.assertEqual(first["command"], second["command"])
            self.assertEqual("fail", first["status"])
            self.assertEqual("pass", second["status"])

    def test_runner_missing_tool_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            receipt, process_code = make_receipt(Path(td), "test", ["stval-missing-tool-91f6"], True, 30)
            self.assertEqual(2, process_code)
            self.assertEqual("blocked", receipt["status"])
            self.assertEqual("environment", receipt["classification"])
            self.assertIsNone(receipt["exit_code"])

    def test_protected_fixture_change_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            baseline = root / "baseline"
            candidate = root / "candidate"
            (baseline / "fixtures").mkdir(parents=True)
            (candidate / "fixtures").mkdir(parents=True)
            (baseline / "fixtures" / "expected.json").write_text("1\n", encoding="utf-8")
            (candidate / "fixtures" / "expected.json").write_text("2\n", encoding="utf-8")
            result = validate_protected(baseline, candidate, set())
            self.assertEqual("fail", result["status"])
            self.assertEqual("protected/modified", result["diagnostics"][0]["code"])


if __name__ == "__main__":
    unittest.main()
