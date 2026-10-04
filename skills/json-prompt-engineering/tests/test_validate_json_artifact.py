from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_json_artifact.py"
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
        self.assertEqual(report["syntax_status"], "fail")
        self.assertIn("duplicate key", report["errors"][0])

    def test_secret_value_fails(self) -> None:
        report = MODULE.run(self.write_json({"task": "call", "api_key": "real-looking-value"}), "prompt")
        self.assertEqual(report["security_authority_status"], "fail")
        self.assertEqual(report["status"], "fail")

    def test_boolean_schema_is_valid_lint_input(self) -> None:
        report = MODULE.run(self.write_json(True), "schema")
        self.assertEqual(report["syntax_status"], "pass")
        self.assertNotEqual(report["specialized_lint_status"], "fail")
        self.assertEqual(report["normative_schema_validation"], "not-run")

    def test_ref_only_schema_has_no_type_warning(self) -> None:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$defs": {"name": {"type": "string"}}, "$ref": "#/$defs/name"}
        report = MODULE.run(self.write_json(schema), "schema")
        self.assertFalse(any("explicit type" in item for item in report["warnings"]))

    def test_unknown_required_property_fails_lint(self) -> None:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "properties": {"name": {"type": "string"}}, "required": ["missing"]}
        report = MODULE.run(self.write_json(schema), "schema")
        self.assertEqual(report["specialized_lint_status"], "fail")

    def test_provider_profile_detects_unsupported_keyword(self) -> None:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "properties": {"name": {"type": "string", "minLength": 2}}, "required": ["name"], "additionalProperties": False}
        profile = {"profile_version": 1, "id": "test", "verified_at": "2026-10-04", "unsupported_keywords": ["minLength"], "requirements": {}}
        report = MODULE.run(self.write_json(schema), "schema", self.write_json(profile))
        self.assertEqual(report["provider_compatibility_status"], "fail")
        self.assertTrue(any(item.get("keyword") == "minLength" for item in report["provider_findings"]))

    def test_provider_profile_can_require_closed_objects(self) -> None:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
        profile = {"profile_version": 1, "id": "test", "verified_at": "2026-10-04", "unsupported_keywords": [], "requirements": {"require_additional_properties_false": True}}
        report = MODULE.run(self.write_json(schema), "schema", self.write_json(profile))
        self.assertEqual(report["provider_compatibility_status"], "fail")
        self.assertTrue(any(item.get("code") == "provider/object-closure" for item in report["provider_findings"]))

    def test_unknown_dependency_fails(self) -> None:
        workflow = {"workflow_version": "1.0.0", "workflow_id": "test", "steps": [{"id": "a", "skill": "one", "action": "run", "instruction": "Run.", "depends_on": ["missing"]}]}
        report = MODULE.run(self.write_json(workflow), "workflow")
        self.assertEqual(report["workflow_status"], "fail")

    def test_dependency_cycle_fails(self) -> None:
        workflow = {"workflow_version": "1.0.0", "workflow_id": "test", "steps": [{"id": "a", "skill": "one", "action": "run", "instruction": "Run A.", "depends_on": ["b"]}, {"id": "b", "skill": "two", "action": "run", "instruction": "Run B.", "depends_on": ["a"]}]}
        report = MODULE.run(self.write_json(workflow), "workflow")
        self.assertEqual(report["workflow_status"], "fail")


if __name__ == "__main__":
    unittest.main()
