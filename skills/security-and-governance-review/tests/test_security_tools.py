from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _security_common import contains_secret_like, protected_status, redact_text  # noqa: E402


def minimal_report() -> dict:
    return {
        "report_version": "security-review-report-1",
        "rubric_version": "SGR-2.0",
        "target": {"name": "fixture", "identity": "sha256:fixture"},
        "mode": "security-report",
        "review_status": "complete",
        "evidence_snapshot": {"tree_sha256": "sha256:fixture"},
        "critical_evidence_gaps": [],
        "findings": [],
        "commands": [],
        "evidence_layers": {
            "structural": [],
            "behavioral": [],
            "runtime": [],
            "external_current": [],
        },
        "limitations": [],
    }


class ProtectedSourceTests(unittest.TestCase):
    def test_secret_bearing_config_paths_are_protected_unread(self) -> None:
        paths = [
            ".npmrc",
            ".pypirc",
            ".netrc",
            ".git-credentials",
            ".docker/config.json",
            "kubeconfig",
            "service-account.json",
            "service_account_prod.json",
            "application_default_credentials.json",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual("protected-unread", protected_status(path))

    def test_windows_style_secret_paths_are_normalized(self) -> None:
        paths = [
            r"repo\.npmrc",
            r"repo\.docker\config.json",
            r"repo\service-account.json",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual("protected-unread", protected_status(path))

    def test_encrypted_private_key_marker_is_detected_and_redacted(self) -> None:
        text = "-----BEGIN " + "ENCRYPTED PRIVATE KEY-----"
        self.assertTrue(contains_secret_like(text))
        self.assertEqual("[masked private key block]", redact_text(text))


class ReadOnlyOutputTests(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_evidence_snapshot_rejects_output_inside_directory_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "a.txt").write_text("alpha\n", encoding="utf-8")
            output = target / "receipt.json"
            result = self.run_script(
                "evidence_snapshot.py",
                "--target",
                str(target),
                "--output",
                str(output),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_static_review_rejects_output_inside_directory_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "a.txt").write_text("alpha\n", encoding="utf-8")
            output = target / "triage.json"
            result = self.run_script(
                "security_static_review.py",
                "--target",
                str(target),
                "--format",
                "json",
                "--output",
                str(output),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_report_validator_rejects_output_alias_without_overwriting_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            original = json.dumps(minimal_report(), indent=2) + "\n"
            report.write_text(original, encoding="utf-8")
            result = self.run_script(
                "validate_security_report.py",
                str(report),
                "--json",
                str(report),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(original, report.read_text(encoding="utf-8"))

    def test_report_validator_returns_structured_failure_for_non_object_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            report.write_text("[]\n", encoding="utf-8")
            result = self.run_script("validate_security_report.py", str(report))
            self.assertEqual(1, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("fail", payload["status"])
            self.assertTrue(any("object" in error for error in payload["errors"]))
            self.assertNotIn("Traceback", result.stderr)

    def test_report_validator_preserves_json_output_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            output = Path(tmp) / "validation.json"
            report.write_text(json.dumps(minimal_report()) + "\n", encoding="utf-8")
            result = self.run_script(
                "validate_security_report.py",
                str(report),
                "--json",
                str(output),
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("pass", json.loads(output.read_text(encoding="utf-8"))["status"])


if __name__ == "__main__":
    unittest.main()
