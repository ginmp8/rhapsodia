from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class PriorityContractTests(unittest.TestCase):
    def test_new_scaffold_emits_business_priority_only(self):
        writer = load_script("write_ops_scaffold.py")
        payload = yaml.safe_load(writer.render(None))
        self.assertIn("business_priority", payload)
        self.assertNotIn("priority", payload)

    def test_canonical_business_priority_validates(self):
        writer = load_script("write_ops_scaffold.py")
        validator = load_script("validate_ops.py")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(writer.render(None), encoding="utf-8")
            errors, _ = validator.validate(path)
        self.assertEqual(errors, [])

    def test_generic_priority_alias_is_rejected(self):
        writer = load_script("write_ops_scaffold.py")
        validator = load_script("validate_ops.py")
        payload = yaml.safe_load(writer.render(None))
        payload["priority"] = payload.pop("business_priority")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            errors, _ = validator.validate(path)
        self.assertTrue(any("unsupported generic key `priority`" in error for error in errors))

    def test_mixed_priority_forms_are_rejected(self):
        writer = load_script("write_ops_scaffold.py")
        validator = load_script("validate_ops.py")
        payload = yaml.safe_load(writer.render(None))
        payload["priority"] = dict(payload["business_priority"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            errors, _ = validator.validate(path)
        self.assertTrue(any("unsupported generic key `priority`" in error for error in errors))

    def test_local_priority_contract_validator_passes(self):
        module = load_script("validate_priority_contract.py")
        self.assertEqual(module.collect_errors(ROOT), [])


if __name__ == "__main__":
    unittest.main()
