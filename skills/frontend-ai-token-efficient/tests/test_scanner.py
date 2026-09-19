from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_frontend_ai_package.py"
SPEC = importlib.util.spec_from_file_location("frontend_ai_scanner", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ScannerTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        (root / "src/features/account/components").mkdir(parents=True)
        (root / "src/features/other").mkdir(parents=True)
        (root / "src/shared/lib").mkdir(parents=True)
        (root / "src/features/account/components/AccountForm.tsx").write_text(
            "localStorage.setItem('auth_token', 'x');\nfetch('/api/account');\nconsole.log('x');\n",
            encoding="utf-8",
        )
        (root / "src/shared/lib/bad.ts").write_text("import { x } from '@/features/other/x';\n", encoding="utf-8")
        (root / ".env").write_text("VITE_CLIENT_SECRET=example\n", encoding="utf-8")

    def test_repeated_scan_is_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            first = MODULE.scan(root)
            second = MODULE.scan(root)
            self.assertEqual(first, second)

    def test_report_has_versioned_machine_readable_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            report = MODULE.scan(root)
            self.assertEqual("2.0", report["schema_version"])
            self.assertEqual("2.1.0", report["scanner_version"])
            self.assertEqual("review_required", report["status"])
            self.assertEqual(len(report["findings"]), report["finding_count"])
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("public_env_secret_like_name", codes)
            self.assertIn("web_storage_token", codes)
            self.assertIn("direct_http_in_component", codes)
            for finding in report["findings"]:
                self.assertIn("subject", finding)
                self.assertIn("supported_fixes", finding)

    def test_missing_target_is_fail_with_stable_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            report = MODULE.scan(missing)
            self.assertEqual("fail", report["status"])
            self.assertEqual("target_missing", report["findings"][0]["code"])


    def test_input_identity_changes_with_scanned_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            first = MODULE.scan(root)["input_identity"]["sha256"]
            source = root / "src/features/account/components/AccountForm.tsx"
            source.write_text(source.read_text(encoding="utf-8") + "\nconst changed = true;\n", encoding="utf-8")
            second = MODULE.scan(root)["input_identity"]["sha256"]
            self.assertNotEqual(first, second)

    def test_report_inside_target_is_excluded_from_input_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            self.make_repo(root)
            output = root / "scan-report.json"
            command = [sys.executable, str(SCRIPT), "--target", str(root), "--format", "json", "--output", str(output)]
            first = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(0, first.returncode, first.stderr)
            first_report = json.loads(output.read_text(encoding="utf-8"))
            second = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(0, second.returncode, second.stderr)
            second_report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(first_report["input_identity"]["sha256"], second_report["input_identity"]["sha256"])
            self.assertIn("scan-report.json", second_report["input_identity"]["excluded_paths"])

    def test_cli_output_is_parseable_and_atomic_destination_is_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            self.make_repo(root)
            output = Path(tmp) / "reports" / "scan.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--target", str(root), "--format", "json", "--output", str(output)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            parsed = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("2.0", parsed["schema_version"])
            self.assertFalse(any(output.parent.glob(".*.tmp-*")))


if __name__ == "__main__":
    unittest.main()
