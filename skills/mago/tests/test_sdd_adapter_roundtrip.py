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


class SddAdapterRoundTripTests(unittest.TestCase):
    def run_cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
        return completed

    def run_round_trip(self, format_name: str, target_version: str) -> dict:
        with tempfile.TemporaryDirectory(prefix=f"mago-{format_name}-adapter-") as tmp:
            root = Path(tmp)
            output = root / "roundtrip"
            report = root / "report.json"
            self.run_cli(
                "round-trip",
                "--package",
                str(PACKAGE),
                "--format",
                format_name,
                "--source-version",
                "mago-2026.07",
                "--target-version",
                target_version,
                "--output",
                str(output),
                "--report",
                str(report),
            )
            validation = subprocess.run(
                [sys.executable, "-B", str(VALIDATOR), str(report)],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            data = json.loads(report.read_text(encoding="utf-8"))
            for name in ("prd.md", "technical-design.md", "tasks.md"):
                self.assertEqual((PACKAGE / name).read_bytes(), (output / "imported" / name).read_bytes())
            self.assertEqual(data["round_trip"]["differences"], [])
            self.assertEqual(data["validation"][-1]["status"], "pass")
            return data

    def test_spec_kit_round_trip_preserves_core_planning_files(self) -> None:
        data = self.run_round_trip("spec-kit", "spec-kit-file-contract-1")
        self.assertEqual(data["target"]["format"], "spec-kit")
        self.assertIn("exported/spec.md", data["generated_files"])
        self.assertIn("exported/plan.md", data["generated_files"])

    def test_openspec_round_trip_preserves_core_and_delta_files(self) -> None:
        data = self.run_round_trip("openspec", "openspec-file-contract-1")
        self.assertEqual(data["target"]["format"], "openspec")
        self.assertIn("change-delta.md", data["mapped_fields"])

    def test_unspecified_latest_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-adapter-version-") as tmp:
            root = Path(tmp)
            self.run_cli(
                "round-trip",
                "--package",
                str(PACKAGE),
                "--format",
                "spec-kit",
                "--source-version",
                "mago-2026.07",
                "--target-version",
                "latest",
                "--output",
                str(root / "out"),
                "--report",
                str(root / "report.json"),
                expected=2,
            )

    def test_external_edit_is_disclosed_on_import(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-adapter-edit-") as tmp:
            root = Path(tmp)
            exported = root / "exported"
            export_report = root / "export-report.json"
            self.run_cli(
                "export",
                "--package",
                str(PACKAGE),
                "--format",
                "spec-kit",
                "--source-version",
                "mago-2026.07",
                "--target-version",
                "spec-kit-file-contract-1",
                "--output",
                str(exported),
                "--report",
                str(export_report),
            )
            (exported / "spec.md").write_text((exported / "spec.md").read_text(encoding="utf-8") + "\nExternal edit.\n", encoding="utf-8")
            imported = root / "imported"
            import_report = root / "import-report.json"
            self.run_cli(
                "import",
                "--source",
                str(exported),
                "--format",
                "spec-kit",
                "--source-version",
                "spec-kit-file-contract-1",
                "--target-version",
                "mago-2026.07",
                "--output",
                str(imported),
                "--report",
                str(import_report),
                "--require-metadata",
            )
            data = json.loads(import_report.read_text(encoding="utf-8"))
            self.assertIn("external file changed since export: spec.md", data["round_trip"]["differences"])


if __name__ == "__main__":
    unittest.main()
