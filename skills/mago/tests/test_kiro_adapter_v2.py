from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sdd_adapter.py"
VALIDATOR = ROOT / "scripts" / "validate_sdd_adapter_report.py"
PACKAGE = ROOT / "examples" / "golden" / "interoperability" / "package"


class KiroAdapterV2Tests(unittest.TestCase):
    def test_kiro_round_trip_preserves_core_planning_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-kiro-") as tmp:
            root = Path(tmp)
            output = root / "roundtrip"
            report = root / "report.json"
            completed = subprocess.run(
                [
                    sys.executable, "-B", str(SCRIPT), "round-trip",
                    "--package", str(PACKAGE),
                    "--format", "kiro",
                    "--source-version", "mago-2026.07",
                    "--target-version", "kiro-file-contract-1",
                    "--output", str(output),
                    "--report", str(report),
                ],
                cwd=str(ROOT), text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["round_trip"]["status"], "lossless")
            self.assertEqual(payload["round_trip"]["differences"], [])
            self.assertEqual(set(payload["mapped_fields"]), {"prd.md", "tasks.md", "technical-design.md"})
            self.assertTrue((output / "exported" / "requirements.md").is_file())
            validation = subprocess.run(
                [sys.executable, "-B", str(VALIDATOR), str(report)],
                cwd=str(ROOT), text=True, capture_output=True, check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_kiro_external_edit_is_disclosed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-kiro-edit-") as tmp:
            root = Path(tmp)
            exported = root / "exported"
            export_report = root / "export-report.json"
            imported = root / "imported"
            import_report = root / "import-report.json"
            export = subprocess.run([
                sys.executable, "-B", str(SCRIPT), "export",
                "--package", str(PACKAGE), "--format", "kiro",
                "--source-version", "mago-2026.07", "--target-version", "kiro-file-contract-1",
                "--output", str(exported), "--report", str(export_report),
            ], cwd=str(ROOT), text=True, capture_output=True, check=False)
            self.assertEqual(export.returncode, 0, export.stdout + export.stderr)
            (exported / "requirements.md").write_text("external edit\n", encoding="utf-8")
            imported_run = subprocess.run([
                sys.executable, "-B", str(SCRIPT), "import",
                "--source", str(exported), "--format", "kiro",
                "--source-version", "kiro-file-contract-1", "--target-version", "mago-2026.07",
                "--output", str(imported), "--report", str(import_report), "--require-metadata",
            ], cwd=str(ROOT), text=True, capture_output=True, check=False)
            self.assertEqual(imported_run.returncode, 0, imported_run.stdout + imported_run.stderr)
            payload = json.loads(import_report.read_text(encoding="utf-8"))
            self.assertTrue(any("requirements.md" in item for item in payload["round_trip"]["differences"]))


if __name__ == "__main__":
    unittest.main()
