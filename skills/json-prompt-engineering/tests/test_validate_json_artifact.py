from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_json_artifact.py"
SPEC = importlib.util.spec_from_file_location("validate_json_artifact", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ValidateJsonArtifactTests(unittest.TestCase):
    def write_text(self, content: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "artifact.json"
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, value: object) -> Path:
        return self.write_text(json.dumps(value))

    def test_valid_prompt_passes(self) -> None:
        report = MODULE.run(self.write_json({"task": "classify", "input": {"text": "hello"}}), "prompt")
        self.assertNotEqual(report["status"], "fail")

    def test_duplicate_key_fails(self) -> None:
        report = MODULE.run(self.write_text('{"task":"a","task":"b"}'), "prompt")
        self.assertEqual(report["status"], "fail")
        self.assertIn("duplicate key", report["errors"][0])

    def test_secret_value_fails(self) -> None:
        report = MODULE.run(self.write_json({"task": "call", "api_key": "real-looking-value"}), "prompt")
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("possible secret value" in item for item in report["errors"]))

    def test_unknown_required_property_fails(self) -> None:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"name": {"type": "string"}},
            "required": ["missing"],
        }
        report = MODULE.run(self.write_json(schema), "schema")
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("unknown properties" in item for item in report["errors"]))

    def test_unknown_dependency_fails(self) -> None:
        workflow = {
            "workflow_version": "1.0.0",
            "workflow_id": "test",
            "steps": [
                {
                    "id": "a",
                    "skill": "one",
                    "action": "run",
                    "instruction": "Run.",
                    "depends_on": ["missing"],
                }
            ],
        }
        report = MODULE.run(self.write_json(workflow), "workflow")
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("unknown dependencies" in item for item in report["errors"]))

    def test_dependency_cycle_fails(self) -> None:
        workflow = {
            "workflow_version": "1.0.0",
            "workflow_id": "test",
            "steps": [
                {
                    "id": "a",
                    "skill": "one",
                    "action": "run",
                    "instruction": "Run A.",
                    "depends_on": ["b"],
                },
                {
                    "id": "b",
                    "skill": "two",
                    "action": "run",
                    "instruction": "Run B.",
                    "depends_on": ["a"],
                },
            ],
        }
        report = MODULE.run(self.write_json(workflow), "workflow")
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("dependency cycle" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
