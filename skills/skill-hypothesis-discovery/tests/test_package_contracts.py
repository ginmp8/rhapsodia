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
        test_source = (ROOT / "tests/test_validate_hypothesis_backlog.py").read_text(encoding="utf-8")
        declared = set(re.findall(r"^\s*def\s+(test_[A-Za-z0-9_]+)\s*\(", test_source, flags=re.MULTILINE))
        for scenario in data["scenarios"]:
            self.assertIn(scenario["deterministic_test"], declared, scenario["id"])


if __name__ == "__main__":
    unittest.main()
