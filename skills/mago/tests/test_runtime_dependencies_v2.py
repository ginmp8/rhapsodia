from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / "scripts"))
from validate_runtime_dependencies import validate  # noqa: E402


class RuntimeDependencyTests(unittest.TestCase):
    def test_current_package_dependency_contract_passes(self) -> None:
        result = validate(ROOT)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["dependencies"][0]["import_status"], "pass")

    def test_missing_requirement_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-deps-") as tmp:
            target = Path(tmp)
            shutil.copy2(ROOT / "release.json", target / "release.json")
            (target / "requirements.txt").write_text("", encoding="utf-8")
            result = validate(target, check_installed=False)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("must equal" in error for error in result["errors"]), result)

    def test_undeclared_requirement_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-deps-") as tmp:
            target = Path(tmp)
            shutil.copy2(ROOT / "release.json", target / "release.json")
            (target / "requirements.txt").write_text("PyYAML>=6.0,<7\nrequests>=2,<3\n", encoding="utf-8")
            result = validate(target, check_installed=False)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("undeclared" in error for error in result["errors"]), result)


if __name__ == "__main__":
    unittest.main()
