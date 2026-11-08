"""Static regressions for independently attributed Archify Skill distribution."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {"archify": "3.2.0", "archify-review": "0.1.0", "archify-tuning": "0.1.0"}
SOURCE_REVISION = "a4065941f12be7967436261d9934784e381d423c"


class ArchifyDistributionTests(unittest.TestCase):
    def test_skill_packages_are_self_attributed_and_versioned(self):
        for name, version in SKILLS.items():
            with self.subTest(name=name):
                base = ROOT / "skills" / name
                for path in ("SKILL.md", "VERSION", "CHANGELOG.md", "SOURCE.md"):
                    self.assertTrue((base / path).is_file(), f"{name}: missing {path}")
                legal = json.loads((ROOT / "licenses/skill-assets.json").read_text(encoding="utf-8"))
                entry = next(entry for entry in legal["skills"] if entry["name"] == name)
                originals = {notice["path"]: notice for notice in entry["notices"]}
                for path in ("LICENSE", "LICENSE-MIT", "NOTICE"):
                    self.assertIn(path, originals, f"{name}: missing source license mapping: {path}")
                    self.assertFalse((base / path).exists(), f"{name}: source license must be centralized")
                    self.assertTrue((ROOT / originals[path]["canonical"]).is_file())
                self.assertEqual((base / "VERSION").read_text(encoding="utf-8").strip(), version)
                self.assertIn(f"## [{version}]", (base / "CHANGELOG.md").read_text(encoding="utf-8"))
                self.assertIn(SOURCE_REVISION, (base / "SOURCE.md").read_text(encoding="utf-8"))
                self.assertIn("tt-a1i", (ROOT / originals["NOTICE"]["canonical"]).read_text(encoding="utf-8"))
                self.assertIn("Apache License", (ROOT / originals["LICENSE"]["canonical"]).read_text(encoding="utf-8"))

    def test_archify_runtime_covers_all_ten_native_types_and_explainer(self):
        base = ROOT / "skills" / "archify"
        self.assertTrue((base / "bin" / "archify.mjs").is_file())
        self.assertTrue((base / "references" / "explainer-authoring.md").is_file())
        for name in ("architecture", "workflow", "sequence", "dataflow", "lifecycle", "erd", "class", "tree", "timeline", "waterfall", "explainer"):
            with self.subTest(type=name):
                self.assertTrue((base / "schemas" / f"{name}.schema.json").is_file())
                data = json.loads((base / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)
        self.assertTrue((base / "skill-release.json").is_file())
        legal = json.loads((ROOT / "licenses/skill-assets.json").read_text(encoding="utf-8"))
        archify = next(entry for entry in legal["skills"] if entry["name"] == "archify")
        mapped = {notice["path"]: notice for notice in archify["notices"]}
        for path in ("THIRD_PARTY_NOTICES.md", "assets/JetBrainsMono-OFL.txt", "explainer/vendor/pele/LICENSE"):
            self.assertIn(path, mapped)
            self.assertFalse((base / path).exists(), path)
            self.assertTrue((ROOT / mapped[path]["canonical"]).is_file())

    def test_tuning_is_open_about_external_script_dependency(self):
        base = ROOT / "skills" / "archify-tuning"
        body = (base / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("scripts are not bundled", body)
        self.assertFalse((base / "scripts").exists())

    def test_reviewer_uses_current_repo_branch_and_scoped_evidence(self):
        base = ROOT / "skills" / "archify-review"
        body = (base / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do not assume", body)
        self.assertIn("Value", body)
        self.assertIn("Cost", body)
        self.assertIn("Impact", body)


if __name__ == "__main__":
    unittest.main()
