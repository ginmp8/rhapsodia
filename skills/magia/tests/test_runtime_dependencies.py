from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_runtime_dependencies import satisfies, validate  # noqa: E402
from magia_utils import load_yaml  # noqa: E402
from update_template_lists import load_payload  # noqa: E402


class RuntimeDependencyTests(unittest.TestCase):
    def test_current_package_dependency_contract_passes(self) -> None:
        result = validate(ROOT)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["dependencies"][0]["import_status"], "pass")

    def test_missing_requirements_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="magia-deps-") as tmp:
            target = Path(tmp)
            shutil.copy2(ROOT / "release.json", target / "release.json")
            result = validate(target, check_installed=False)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("missing regular dependency manifest" in error for error in result["errors"]), result)

    def test_missing_release_declaration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="magia-deps-") as tmp:
            target = Path(tmp)
            release = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
            release["runtime_dependencies"] = []
            (target / "release.json").write_text(json.dumps(release), encoding="utf-8")
            (target / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
            result = validate(target, check_installed=False)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("non-empty list" in error for error in result["errors"]), result)

    def test_wrong_import_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="magia-deps-") as tmp:
            target = Path(tmp)
            release = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
            release["runtime_dependencies"][0]["import"] = "missing_yaml_module"
            (target / "release.json").write_text(json.dumps(release), encoding="utf-8")
            (target / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
            result = validate(target, check_installed=True)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("cannot load runtime dependency" in error for error in result["errors"]), result)

    def test_incompatible_version_is_rejected_by_specifier(self) -> None:
        self.assertFalse(satisfies("6.0.2", "==6.0.3"))
        self.assertTrue(satisfies("6.0.3", "==6.0.3"))

    def test_yaml_helpers_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="magia-yaml-") as tmp:
            path = Path(tmp) / "sample.yaml"
            path.write_text("value: 7\n", encoding="utf-8")
            self.assertEqual(load_yaml(path), {"value": 7})
            self.assertEqual(load_payload(path), {"value": 7})

    def test_runtime_validator_cli(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/validate_runtime_dependencies.py"), str(ROOT)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
