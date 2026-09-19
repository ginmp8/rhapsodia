from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from derive_identity import insertion_order, next_spec, next_task  # noqa: E402
from _fixtures import make_cycle  # noqa: E402


class IdentityTests(unittest.TestCase):
    def test_next_spec_is_max_plus_one_and_order_plus_ten(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            result = next_spec(root / "spec-catalog.yaml")
            self.assertEqual("spec002", result["next_spec_id"])
            self.assertEqual(20, result["append_order"])
            self.assertEqual(64, len(result["catalog_sha256"]))

    def test_insert_order_uses_deterministic_midpoint(self):
        with tempfile.TemporaryDirectory() as td:
            specs = [
                {"order":10,"spec_id":"spec001","feature_key":"alpha","title":"Alpha","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"},
                {"order":20,"spec_id":"spec002","feature_key":"beta","title":"Beta","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"}
            ]
            root = make_cycle(Path(td), specs, create_specs=False)
            result = insertion_order(root / "spec-catalog.yaml", "spec001", "spec002")
            self.assertEqual(15, result["order"])

    def test_insert_without_gap_requires_rebalance(self):
        with tempfile.TemporaryDirectory() as td:
            specs = [
                {"order":10,"spec_id":"spec001","feature_key":"alpha","title":"Alpha","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"},
                {"order":11,"spec_id":"spec002","feature_key":"beta","title":"Beta","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"}
            ]
            root = make_cycle(Path(td), specs, create_specs=False)
            result = insertion_order(root / "spec-catalog.yaml", "spec001", "spec002")
            self.assertEqual("ORDER_REBALANCE_REQUIRED", result["code"])

    def test_next_task_considers_existing_display_and_stable_ids(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            result = next_task(root / "specs/spec001/tasks.md")
            self.assertEqual("task003", result["next_task_id"])


if __name__ == "__main__":
    unittest.main()
