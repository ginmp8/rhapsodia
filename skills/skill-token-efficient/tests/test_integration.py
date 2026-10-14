"""Standalone deterministic integration/format-policy tests; Python stdlib only."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def request(role="skill-instructions"):
    return {
        "contract_id": "skill-opt.token-efficiency",
        "contract_version": 1,
        "consumer": "skill-creator-juiced",
        "operation": "format-advice",
        "mode": "plan",
        "target_skill": "./example-staged-skill",
        "mutation_authorized": False,
        "tokenization": {"primary_method": "estimator-v1", "scope": "instructions"},
        "format_context": {
            "role": role,
            "supported_formats": ["markdown", "json-compact", "yaml", "csv", "tsv", "toon", "jton", "ndjson", "html", "xml", "toml"],
            "requires_machine_parse": False,
            "requires_type_fidelity": False,
            "schema_available": False,
            "has_typed_decoder": False,
            "allow_nonstandard_codec": False,
            "human_editable": True,
        },
    }


def invoke(tool: str, req: dict):
    proc = subprocess.run([sys.executable, "-S", str(ROOT / "scripts" / tool), "--json-input", "-"],
                          input=json.dumps(req), text=True, capture_output=True)
    return proc.returncode, json.loads(proc.stdout)


class IntegrationTests(unittest.TestCase):
    def test_advice_role_defaults(self):
        expected = {
            "skill-instructions": "markdown", "tool-schema": "json-compact",
            "human-config": "yaml", "flat-records": "json-compact",
            "nested-data": "json-compact", "event-stream": "ndjson",
            "html-dom": "html", "workflow": "markdown",
        }
        for role, selected in expected.items():
            with self.subTest(role=role):
                rc, result = invoke("recommend_format.py", request(role))
                self.assertEqual(rc, 0)
                self.assertEqual(result["recommended_format"], selected)
                self.assertEqual(result["evidence"]["token_count_status"], "not-run")
                self.assertFalse(result["mutation_performed"])

    def test_flat_schema_eligibility(self):
        r = request("flat-records")
        r["format_context"]["schema_available"] = True
        self.assertEqual(invoke("recommend_format.py", r)[1]["recommended_format"], "csv")
        r["format_context"]["requires_type_fidelity"] = True
        self.assertEqual(invoke("recommend_format.py", r)[1]["recommended_format"], "json-compact")
        r["format_context"]["has_typed_decoder"] = True
        self.assertEqual(invoke("recommend_format.py", r)[1]["recommended_format"], "csv")

    def test_nonstandard_never_auto_promoted(self):
        r = request("nested-data")
        r["format_context"].update(schema_available=True, has_typed_decoder=True, allow_nonstandard_codec=True,
                                    supported_formats=["toon", "jton"])
        rc, result = invoke("recommend_format.py", r)
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "blocked")
        self.assertIsNone(result["recommended_format"])
        self.assertEqual(result["conditional_formats"], ["toon", "jton"])

    def test_native_tool_contract_cannot_be_overridden(self):
        r = request("tool-schema")
        r["format_context"]["supported_formats"] = ["toon", "yaml"]
        rc, result = invoke("recommend_format.py", r)
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "blocked")

    def test_nested_typed_machine_without_json_is_blocked(self):
        r = request("nested-data")
        r["format_context"].update(requires_type_fidelity=True, requires_machine_parse=True,
                                    supported_formats=["yaml", "xml"])
        self.assertEqual(invoke("recommend_format.py", r)[1]["status"], "blocked")

    def test_invalid_request_never_mutates(self):
        r = request()
        r["mutation_authorized"] = True
        rc, result = invoke("validate_integration.py", r)
        self.assertNotEqual(rc, 0)
        self.assertEqual(result["status"], "fail")
        for bad in [[], {}, False]:
            r = request()
            r["mode"] = bad
            self.assertNotEqual(invoke("validate_integration.py", r)[0], 0)

    def test_booster_authorized_only_on_staged_copy(self):
        r = request()
        r.update(consumer="skill-booster", operation="optimize-existing", mode="apply",
                 format_context=None, mutation_authorized=True, staged_candidate="./staged")
        self.assertEqual(invoke("validate_integration.py", r)[0], 0)
        r["staged_candidate"] = ""
        self.assertNotEqual(invoke("validate_integration.py", r)[0], 0)
        r["staged_candidate"] = "./staged"
        r["consumer"] = "skill-benchmark"
        self.assertNotEqual(invoke("validate_integration.py", r)[0], 0)

    def test_read_only_benchmark_compares_two_arms(self):
        r = request()
        r.update(consumer="skill-benchmark", operation="compare-existing", mode="validate",
                 format_context=None, baseline_path="./before", candidate_path="./after")
        self.assertEqual(invoke("validate_integration.py", r)[0], 0)
        r["candidate_path"] = ""
        self.assertNotEqual(invoke("validate_integration.py", r)[0], 0)

    def test_invalid_version_format_rejected(self):
        r = request()
        r["contract_version"] = 2
        self.assertNotEqual(invoke("validate_integration.py", r)[0], 0)
        r = request()
        r["format_context"]["supported_formats"] = ["secret-unknown-format"]
        self.assertNotEqual(invoke("validate_integration.py", r)[0], 0)

    def test_provider_package_boundaries(self):
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(content.splitlines()), 100)
        self.assertTrue((ROOT / "contracts/integration-manifest.json").exists())
        self.assertTrue((ROOT / "release.json").exists())
        self.assertIn("references/format-selection.md", content)
        self.assertIn("references/integration-protocol.md", content)


if __name__ == "__main__":
    unittest.main()
