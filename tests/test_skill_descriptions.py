"""Regression tests for 500-character skill descriptions."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_skill_descriptions", ROOT / "scripts/validate_skill_descriptions.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class SkillDescriptionTests(unittest.TestCase):
    def test_boundary_500_succeeds(self):
        self.assertEqual(mod.parse_description("---\nname: demo\ndescription: " + "x" * 500 + "\n---\n"), "x" * 500)

    def test_boundary_501_fails(self):
        with self.assertRaisesRegex(ValueError, "501 characters"):
            mod.parse_description("---\ndescription: " + "x" * 501 + "\n---\n")

    def test_folded_multiline_overflow_fails(self):
        with self.assertRaisesRegex(ValueError, "maximum is 500"):
            mod.parse_description("---\ndescription: >-\n  " + "x" * 260 + "\n  " + "x" * 260 + "\n---\n")

    def test_missing_and_duplicate_descriptions_fail(self):
        for content in ("---\nname: demo\n---\n", "---\ndescription: one\ndescription: two\n---\n"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                mod.parse_description(content)

    def test_unicode_counts_characters(self):
        self.assertEqual(len(mod.parse_description("---\ndescription: " + "é" * 500 + "\n---")), 500)

    def test_quoted_and_folded_scalars(self):
        self.assertEqual(mod.parse_description('---\ndescription: "quoted content"\n---'), "quoted content")
        self.assertEqual(mod.parse_description("---\ndescription: >\n  first\n  second\n---"), "first second")

    def test_repository_all_descriptions(self):
        self.assertEqual(mod.check(ROOT), [])

    def test_reports_correct_path(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "skills" / "bad"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\ndescription: " + "x" * 501 + "\n---\n", encoding="utf-8")
            errors = mod.check(Path(td))
            self.assertEqual(len(errors), 1)
            self.assertIn("skills/bad/SKILL.md", errors[0])

if __name__ == "__main__":
    unittest.main()
