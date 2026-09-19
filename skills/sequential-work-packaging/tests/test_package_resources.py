from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageResourceTests(unittest.TestCase):
    def test_all_json_resources_parse(self):
        for folder in (ROOT / "schemas", ROOT / "evals"):
            for path in folder.glob("*.json"):
                with self.subTest(path=path.name):
                    json.loads(path.read_text(encoding="utf-8"))

    def test_frozen_scenarios_cover_required_cases(self):
        data = json.loads((ROOT / "evals/scenarios.json").read_text(encoding="utf-8"))
        ids = {x["id"] for x in data["scenarios"]}
        required = {
            "new-spec", "refine-no-material-change", "refine-repeat", "decompose-repeat",
            "normalize-legacy", "conflicting-ids", "inconsistent-manifest", "tasks-out-of-order",
            "dependency-cycle", "protected-file", "partial-write-failure", "rerun-after-success",
            "rerun-after-failure", "output-aliases-input", "duplicate-canonical-identity"
        }
        self.assertEqual(required, ids)

    def test_current_mago_compatibility_is_adapter_only(self):
        text = (ROOT / "references/mago-adaptation.md").read_text(encoding="utf-8")
        self.assertIn("external compatibility adapter/projection", text)
        self.assertIn("Never rewrite a current MAGO", text)
        self.assertIn("MAGO remains authoritative", text)
        self.assertIn("`reshape-tasks` | `decompose`", text)


if __name__ == "__main__":
    unittest.main()
