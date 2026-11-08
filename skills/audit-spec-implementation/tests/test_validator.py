import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_report.py"


def valid_report():
    return {
        "schema_version": "spec-audit/v1",
        "scope": {
            "repository": "acme/widgets", "target": "PR #7", "base_sha": "aaa",
            "head_sha": "bbb", "snapshot_time_utc": "2026-10-27T08:00:00Z",
            "partial": False,
        },
        "sources": [{"locator": "issue #8", "available": True, "revision": "2026-10-27"}],
        "requirements": [{
            "id": "REQ-001", "criterion": "Reject unauthorized writes",
            "source_locator": "issue #8 AC1", "status": "PASS",
            "implementation_evidence": [{"locator": "acme/widgets@bbb:src/a.py#L1-L12", "claim": "Permission checked"}],
            "proof": [{"kind": "executed_test", "locator": "pytest 2026-10-27 bbb", "result": "passed"}],
            "explanation": "An unauthorized attempt was denied.", "finding_ids": [],
        }],
        "findings": [], "verdict": "COMPLIANT", "limitations": [],
    }


def run_report(report):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "report.json"
        path.write_text(json.dumps(report), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(path)], text=True, capture_output=True)


class ValidatorTests(unittest.TestCase):
    def test_valid_pass(self):
        result = run_report(valid_report())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"pass": 1', result.stdout)

    def test_rejects_pass_without_actual_proof(self):
        report = valid_report()
        report["requirements"][0]["proof"] = [{"kind": "test_defined", "locator": "test file", "result": "passed"}]
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent passing proof", result.stderr)

    def test_rejects_duplicate_requirement_id(self):
        report = valid_report()
        report["requirements"].append(copy.deepcopy(report["requirements"][0]))
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Duplicate requirement", result.stderr)

    def test_rejects_compliant_with_unverified(self):
        report = valid_report()
        report["requirements"][0]["status"] = "UNVERIFIED"
        report["requirements"][0]["proof"] = []
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMPLIANT", result.stderr)

    def test_rejects_compliant_when_scope_is_partial(self):
        report = valid_report()
        report["scope"]["partial"] = True
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("partial scope", result.stderr)

    def test_rejects_compliant_with_missing_spec(self):
        report = valid_report()
        report["sources"][0]["available"] = False
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unavailable source", result.stderr)

    def test_not_applicable_requires_reason(self):
        report = valid_report()
        report["requirements"][0].update({"status": "NOT_APPLICABLE", "explanation": "", "proof": [], "implementation_evidence": []})
        report["verdict"] = "INCONCLUSIVE"
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explanation", result.stderr)

    def test_rejects_unknown_finding_ref(self):
        report = valid_report()
        report["requirements"][0]["finding_ids"] = ["F-001"]
        result = run_report(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown finding", result.stderr)


if __name__ == "__main__":
    unittest.main()
