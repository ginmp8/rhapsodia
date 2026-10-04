from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageContractTests(unittest.TestCase):
    def test_skill_has_portable_frontmatter(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: json-prompt-engineering", text)
        self.assertIn("description:", text)

    def test_all_markdown_resource_links_exist(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        import re
        for rel in re.findall(r"\]\(([^)]+)\)", text):
            if rel.startswith(("http://", "https://")):
                continue
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_activation_scenarios_have_unique_ids(self) -> None:
        data = json.loads((ROOT / "evals" / "activation-scenarios.json").read_text(encoding="utf-8"))
        ids = [item["id"] for item in data["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_activation_scenarios_have_executable_contract(self) -> None:
        data = json.loads((ROOT / "evals" / "activation-scenarios.json").read_text(encoding="utf-8"))
        allowed = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
        self.assertGreaterEqual(len(data["scenarios"]), 20)
        for scenario in data["scenarios"]:
            self.assertIn(scenario["type"], allowed)
            self.assertEqual(scenario["category"], scenario["type"])
            self.assertTrue(scenario["prompt"].strip())
            self.assertTrue(scenario["expected_behavior"].strip())
            self.assertTrue(scenario["acceptance_criteria"])
            self.assertTrue(all(isinstance(x, str) and x.strip() for x in scenario["acceptance_criteria"]))


if __name__ == "__main__":
    unittest.main()
