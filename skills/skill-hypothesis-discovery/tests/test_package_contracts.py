from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageContractTests(unittest.TestCase):
    def test_hypothesis_pool_v2_surface_is_preserved(self) -> None:
        manifest = json.loads((ROOT / "contracts/integration-manifest.json").read_text(encoding="utf-8"))
        exports = {item["contract_id"]: item for item in manifest["exports"]}
        contract = exports["skill-opt.hypothesis-pool"]
        self.assertEqual(2, contract["version"])
        self.assertEqual("owner-producer", contract["role"])
        for rel in contract["surface_paths"]:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_activation_suite_matches_current_portable_validator_shapes(self) -> None:
        data = json.loads((ROOT / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
        scenarios = data["scenarios"]
        ids = [item["id"] for item in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"should_activate", "should_not_activate", "ambiguous", "edge_case"}.issubset({item["type"] for item in scenarios}))
        self.assertTrue({"activation", "non-activation", "ambiguous", "boundary", "adversarial"}.issubset({item["group"] for item in scenarios}))
        allowed_routes = {"activate", "do-not-activate", "conditional", "activate-constrained", "split-handoff", "reject-scope-weakening", "reject-fabricated-evidence", "reject-ownership-expansion"}
        for item in scenarios:
            self.assertIn(item["expected_route"], allowed_routes)
            self.assertTrue(item["acceptance_criteria"])
            self.assertTrue(all(re.fullmatch(r"[A-Z]{2,5}-\d{3}", value) for value in item["contract_ids"]))

    def test_regression_fixture_references_real_deterministic_tests(self) -> None:
        fixture = ROOT / "tests/fixtures/discovery-regression-scenarios.json"
        self.assertTrue(fixture.is_file())
        self.assertFalse((ROOT / "evals/discovery-regression-scenarios.json").exists())
        data = json.loads(fixture.read_text(encoding="utf-8"))
        test_sources = [
            (ROOT / "tests/test_validate_hypothesis_backlog.py").read_text(encoding="utf-8"),
            (ROOT / "tests/test_validate_research_discovery.py").read_text(encoding="utf-8"),
        ]
        declared = set()
        for test_source in test_sources:
            declared.update(re.findall(r"^\s*def\s+(test_[A-Za-z0-9_]+)\s*\(", test_source, flags=re.MULTILINE))
        for scenario in data["scenarios"]:
            self.assertIn(scenario["deterministic_test"], declared, scenario["id"])


    def test_top100_control_plane_keeps_critical_rules_and_direct_resources(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        top100 = "\n".join(skill.splitlines()[:100])
        required = [
            "Mission and activation boundary",
            "Required inputs and mode router",
            "Eligibility and decision contract",
            "Quick-start workflow",
            "Critical invariants",
            "Direct resource map",
            "Output contract",
            "Stop conditions",
            "testable-hypothesis",
            "evidence-gap",
            "unsupported-speculation",
            "no-mutation-recommended",
            "research_policy",
            "impact + confidence + testability - risk - ceil(cost / 2)",
            "next_hypothesis_id",
            "Never relabel candidate-aware validation evidence as discovery evidence",
        ]
        for token in required:
            self.assertIn(token, top100, token)

        for rel in [
            "references/discovery-method.md",
            "references/hypothesis-schema.md",
            "references/research-grounding.md",
            "references/integration-workflows.md",
            "examples/hypothesis-discovery-examples.md",
        ]:
            self.assertIn(rel, top100, rel)

    def test_long_markdown_has_semantic_preview_and_synced_contents(self) -> None:
        long_markdown = [
            p for p in ROOT.rglob("*.md")
            if p.name != "SKILL.md" and len(p.read_text(encoding="utf-8").splitlines()) > 100
        ]
        self.assertTrue(long_markdown)
        for path in long_markdown:
            lines = path.read_text(encoding="utf-8").splitlines()
            early = "\n".join(lines[:40])
            for token in ["**Purpose:**", "**Load when:**", "**Decision impact:**", "## Contents"]:
                self.assertIn(token, early, f"{path.relative_to(ROOT)} missing {token}")

            material = [line[3:].strip() for line in lines if line.startswith("## ")]
            material = [h for h in material if h not in {"At a Glance", "Contents"}]
            contents_start = lines.index("## Contents") + 1
            contents = []
            for line in lines[contents_start:]:
                if line.startswith("## "):
                    break
                if line.startswith("- "):
                    contents.append(line[2:].strip())
            self.assertEqual(material, contents, path.relative_to(ROOT))


if __name__ == "__main__":
    unittest.main()
