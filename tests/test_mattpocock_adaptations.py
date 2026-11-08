"""Deterministic distribution and relationship checks for 0.17.0 source-attributed skills."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "grilling", "grill-me", "grill-with-docs", "domain-modeling",
    "wayfinder", "retro", "code-review",
)
REVISION = "4ae2317ddb22b046e26455e4f9c9b3aaaf62212d"

class MattPocockAdaptationTests(unittest.TestCase):
    def test_seven_package_roots_have_release_and_source_identity(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                root = ROOT / "skills" / name
                self.assertTrue((root / "SKILL.md").is_file())
                self.assertEqual((root / "VERSION").read_text().strip(), "0.1.0")
                self.assertIn("## [0.1.0]", (root / "CHANGELOG.md").read_text())
                source = (root / "SOURCE.md").read_text()
                self.assertIn(REVISION, source)
                self.assertIn("mattpocock/skills", source)
                self.assertIn("Reference Git blob SHA", source)
                license_text = (root / "LICENSE-MIT").read_text()
                self.assertIn("MIT License", license_text)
                self.assertIn("Matt Pocock", license_text)
                self.assertTrue((root / "agents/openai.yaml").is_file())
                evals = json.loads((root / "evals/activation-scenarios.json").read_text())
                self.assertEqual(evals["skill"], name)
                self.assertTrue(evals["positive"])
                self.assertTrue(evals["negative"])

    def test_portable_frontmatter_and_short_descriptions(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                source = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertTrue(source.startswith("---\n"))
                self.assertIn(f"name: {name}\n", source)
                self.assertNotIn("disable-model-invocation:", source)
                match = re.search(r'^description: (.+)$', source, flags=re.MULTILINE)
                self.assertIsNotNone(match)
                description = json.loads(match.group(1))
                self.assertLessEqual(len(description), 500)
                self.assertIn("\n---\n\n#", source)
                self.assertLess(len(source.splitlines()), 101)

    def test_compositions_and_existing_contract_boundaries(self):
        main = lambda name: (ROOT / "skills" / name / "SKILL.md").read_text()
        self.assertIn("explicit alias", main("grill-me").lower())
        self.assertIn("grilling", main("grill-me"))
        self.assertIn("grilling", main("grill-with-docs"))
        self.assertIn("domain-modeling", main("grill-with-docs"))
        self.assertIn("Mago", main("domain-modeling"))
        self.assertIn("Nomia", main("wayfinder"))
        self.assertIn("Magia", main("wayfinder"))
        self.assertIn("Standards", main("code-review"))
        self.assertIn("Spec", main("code-review"))
        self.assertIn("Skill Booster", main("retro"))
        for relative in ("skills/domain-modeling/GLOSSARY-FORMAT.md",
                         "skills/domain-modeling/ADR-FORMAT.md",
                         "skills/code-review/references/smell-baseline.md",
                         "skills/wayfinder/references/map-contract.md"):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_release_documents_and_catalog(self):
        d = json.loads((ROOT / "marketplace/catalog.json").read_text())
        self.assertEqual(d["plugin"]["version"], "0.17.0")
        self.assertEqual(d["marketplace"]["version"], "0.17.0")
        readme = (ROOT / "README.md").read_text()
        self.assertIn("76 independently versioned Agent Skills", readme.split("## 0.16.0")[0])
        for path in ("docs/releases/0.17.0.md",
                     "docs/interview-and-decision-workflows.md",
                     "docs/public-source-attribution-audit.md"):
            self.assertTrue((ROOT / path).is_file())

if __name__ == "__main__":
    unittest.main()
