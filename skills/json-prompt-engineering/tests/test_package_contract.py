from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


class PackageContractTests(unittest.TestCase):
    def test_skill_has_portable_frontmatter(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: json-prompt-engineering", text)
        self.assertIn("description:", text)
        frontmatter = text.split("---", 2)[1].lower()
        self.assertIn("use when", frontmatter)
        self.assertIn("do not use", frontmatter)

    def test_all_local_resource_links_exist(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        for rel in re.findall(r"\]\(([^)]+)\)", text):
            if rel.startswith(("http://", "https://")):
                continue
            path = rel.split("#", 1)[0]
            self.assertTrue((ROOT / path).exists(), rel)

    def test_top_100_exposes_complete_control_plane(self) -> None:
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 100)
        top = "\n".join(lines[:100])
        required_signals = [
            "## Purpose and activation boundary",
            "**Use when:**",
            "**Do not use when:**",
            "## Critical rules",
            "## Mode router",
            "## Quick-start workflow",
            "## Direct resource map",
            "## Block or return a bounded result when",
            "canonical contract",
            "application-side",
            "official provider",
            "conforming JSON Schema implementation",
            "executed vs review-only vs not-run",
        ]
        for signal in required_signals:
            self.assertIn(signal, top, signal)

    def test_all_required_markdown_is_one_hop_and_top_100_discoverable(self) -> None:
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        top = "\n".join(lines[:100])
        linked = set(re.findall(r"\]\((references/[^)#]+\.md)(?:#[^)]+)?\)", top))
        expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / "references").glob("*.md")}
        self.assertEqual(expected, linked)

    def test_long_supporting_markdown_has_decision_useful_preview(self) -> None:
        for path in sorted(ROOT.rglob("*.md")):
            if path == SKILL:
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            if len(lines) <= 100:
                continue
            top = "\n".join(lines[:40])
            exception = "context-preview-exception:" in top
            if exception:
                continue
            for signal in ("Purpose", "Load when", "Decision impact"):
                self.assertIn(signal, top, f"{path.relative_to(ROOT)} missing {signal}")
            self.assertRegex(top, r"(?m)^## (Contents|Table of Contents|Section Map)$")

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
