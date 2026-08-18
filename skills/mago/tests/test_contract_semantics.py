from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_contract_semantics.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_contract_semantics", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContractSemanticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.temp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def copy_package(self) -> Path:
        target = Path(self.temp.name) / "mago"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        return target

    def test_current_contract_semantics_pass(self) -> None:
        self.assertEqual(self.module.collect_errors(ROOT), [])

    def test_legacy_handoff_acceptance_in_prose_is_rejected(self) -> None:
        target = self.copy_package()
        path = target / "references" / "ecosystem-handoff-contract.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nLegacy envelopes are accepted through a compatibility mode and normalized before validation.\n",
            encoding="utf-8",
        )
        errors = self.module.collect_errors(target)
        self.assertTrue(any("legacy compatibility as accepted" in error for error in errors), errors)

    def test_machine_contract_cannot_enable_legacy_read_support(self) -> None:
        target = self.copy_package()
        path = target / "references" / "ecosystem-handoff-contract.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["compatibility"]["legacy_read_support"] = True
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        errors = self.module.collect_errors(target)
        self.assertTrue(any("legacy_read_support false" in error for error in errors), errors)

    def test_generic_priority_alias_preservation_is_rejected(self) -> None:
        target = self.copy_package()
        path = target / "references" / "shared-artifact-ownership.md"
        text = path.read_text(encoding="utf-8")
        text += "\nPreserve priority and order hint as registry fields.\n"
        path.write_text(text, encoding="utf-8")
        errors = self.module.collect_errors(target)
        self.assertTrue(any("unsupported generic priority alias" in error for error in errors), errors)

    def test_mixed_version_policy_cannot_be_relaxed(self) -> None:
        target = self.copy_package()
        path = target / "references" / "ecosystem-compatibility.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["policy"]["mixed_versions_allowed"] = True
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        errors = self.module.collect_errors(target)
        self.assertTrue(any("reject mixed versions" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
