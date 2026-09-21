from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate = load_module("validate_hardened_skill_test", ROOT / "scripts" / "validate_hardened_skill.py")
package = load_module("package_skill_test", ROOT / "scripts" / "package_skill.py")


class SkillHardeningTests(unittest.TestCase):
    def test_current_scenario_contract_is_valid(self):
        summary = validate.scenario_summary(ROOT)
        self.assertEqual([], summary["errors"])
        self.assertEqual([], summary["missing_required_types"])
        for required in ("should_activate", "should_not_activate", "ambiguous", "edge_case"):
            self.assertGreater(summary["types"].get(required, 0), 0)

    def test_output_aliases_are_rejected(self):
        errors = package.validate_output_paths(ROOT, ROOT / "skill.zip", ROOT / "receipt.json")
        self.assertTrue(any("outside the target skill tree" in item for item in errors))
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "skill.zip"
            self.assertEqual([], package.validate_output_paths(ROOT, out, Path(td) / "receipt.json"))
            alias_errors = package.validate_output_paths(ROOT, out, out)
            self.assertIn("package output and JSON output must be different paths", alias_errors)

    def test_packaging_is_deterministic_and_receipt_fields_are_additive(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            first = package.build_package(ROOT, td_path / "a.zip", validate=True)
            second = package.build_package(ROOT, td_path / "b.zip", validate=True)
            self.assertEqual(first["candidate_tree_sha256"], second["candidate_tree_sha256"])
            self.assertEqual(first["package_sha256"], second["package_sha256"])
            self.assertTrue(first["atomic_replace"])
            self.assertTrue(first["last_good_preserved_on_failure"])
            self.assertEqual([], first["recovery"])

    def test_cli_receipt_exposes_cross_skill_target_identity(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            receipt_path = td_path / "receipt.json"
            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = package.main([
                    "--target", str(ROOT),
                    "--output", str(td_path / "skill.zip"),
                    "--validate",
                    "--json-output", str(receipt_path),
                ])
            self.assertEqual(0, exit_code)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            expected = package.ecosystem_tree_sha256(ROOT)
            self.assertEqual(expected, receipt["target_tree_sha256"])
            self.assertEqual(expected, receipt["receipt"]["target_tree_sha256"])

    def test_old_zip_inside_target_is_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "demo"
            target.mkdir()
            (target / "SKILL.md").write_text("---\nname: demo\ndescription: use when hardening a demo package with enough detail to satisfy validation; do not use for unrelated work.\n---\n# Demo\n", encoding="utf-8")
            (target / "old.zip").write_bytes(b"old")
            files, excluded = package.iter_package_files(target)
            self.assertEqual(["SKILL.md"], [p.relative_to(target).as_posix() for p in files])
            self.assertTrue(any(item["path"] == "old.zip" for item in excluded))


if __name__ == "__main__":
    unittest.main()
