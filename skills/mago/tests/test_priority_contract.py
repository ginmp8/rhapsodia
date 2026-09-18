from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrent_model import RegistryRecord, topological_order, validate_record
from mago_utils import CANONICAL_CYCLE_KIND, CANONICAL_SPEC_KIND, make_cycle_id, make_spec_id


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class PriorityContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.cycle_id = make_cycle_id("priority-contract", "2026-07-21")
        self.board = self.repo / "docs/boards/demo/2026/cycles" / self.cycle_id
        (self.board / "registry").mkdir(parents=True)
        yaml.safe_dump
        (self.board / "cycle.yaml").write_text(yaml.safe_dump({
            "kind": CANONICAL_CYCLE_KIND, "cycle_id": self.cycle_id, "cycle_key": "priority-contract",
            "board_id": "demo", "year": 2026, "created_at": "2026-07-21T10:00:00Z",
            "created_by": "test", "status": "planned", "proposed_version": None,
            "accepted_version": None, "planning_revision": 1, "imported_from": None,
        }, sort_keys=False), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *extra: str) -> list[str]:
        return [sys.executable, "-B", str(SCRIPTS / "create_planning_identity.py"), "spec",
                "--board-root", str(self.board), "--feature-key", "demo-feature", "--title", "Demo Feature",
                "--created-at", "2026-07-21T11:00:00Z", *extra]

    def test_new_writer_emits_only_explicit_priority_concepts(self):
        result = subprocess.run(self.command(), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = yaml.safe_load(next((self.board / "registry").glob("*.yaml")).read_text(encoding="utf-8"))
        self.assertIn("business_priority", payload)
        self.assertIn("technical_criticality", payload)
        self.assertIn("execution_sequence", payload)
        self.assertNotIn("priority", payload)
        self.assertNotIn("order_hint", payload)

    def test_non_unknown_business_priority_requires_nomia_provenance(self):
        result = subprocess.run(self.command("--business-priority", "urgent"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires --business-priority-source", result.stdout)

    def test_generic_priority_field_is_rejected(self):
        spec_id = make_spec_id("demo-feature", "2026-07-21")
        data = {
            "kind": CANONICAL_SPEC_KIND, "spec_id": spec_id, "cycle_id": self.cycle_id,
            "feature_key": "demo-feature", "feature_version": "0.1.0", "title": "Demo",
            "type": "feature", "classification": "internal", "profile": "standard",
            "created_at": "2026-07-21T11:00:00Z", "status": "planned", "priority": "normal",
            "business_priority": {"level": "unknown", "owner": "nomia", "source": None, "observed_at": None},
            "technical_criticality": {"level": "normal", "owner": "mago", "rationale": None},
            "execution_sequence": {"rank": None, "lane": "standard", "owner": "mago", "rationale": []},
            "depends_on_features": [], "depends_on_specs": [], "supersedes": [], "superseded_by": None,
            "handoff": {"status": "needs_discovery", "downstream_mode": "define", "package_shape": "full",
                        "source_candidates": [], "seed_artifacts": ["manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"], "blockers": []},
        }
        path = self.board / "registry" / f"{spec_id}.yaml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        errors = validate_record(self.board, yaml.safe_load((self.board / "cycle.yaml").read_text()), RegistryRecord(path, data))
        self.assertTrue(any("unsupported generic field" in error for error in errors))

    def test_generic_priority_only_registry_is_rejected(self):
        spec_id = make_spec_id("legacy-feature", "2026-07-21")
        data = {
            "kind": CANONICAL_SPEC_KIND, "spec_id": spec_id, "cycle_id": self.cycle_id,
            "feature_key": "legacy-feature", "feature_version": "0.1.0", "title": "Legacy",
            "type": "feature", "classification": "internal", "profile": "standard",
            "created_at": "2026-07-21T11:00:00Z", "status": "planned", "priority": "normal", "order_hint": None,
            "depends_on_features": [], "depends_on_specs": [], "supersedes": [], "superseded_by": None,
            "handoff": {"status": "needs_discovery", "downstream_mode": "define", "package_shape": "full",
                        "source_candidates": [], "seed_artifacts": ["manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"], "blockers": []},
        }
        path = self.board / "registry" / f"{spec_id}.yaml"
        errors = validate_record(self.board, yaml.safe_load((self.board / "cycle.yaml").read_text()), RegistryRecord(path, data))
        self.assertTrue(any("unsupported generic field" in error for error in errors))

    def test_execution_sequence_orders_without_using_business_priority(self):
        def record(feature: str, business: str, rank: int) -> RegistryRecord:
            sid = make_spec_id(feature, "2026-07-21")
            data = {"spec_id": sid, "feature_key": feature, "depends_on_specs": [], "created_at": "2026-07-21T11:00:00Z",
                    "business_priority": {"level": business, "owner": "nomia", "source": "nomia/ops", "observed_at": "2026-07-21T10:00:00Z"},
                    "technical_criticality": {"level": "normal", "owner": "mago", "rationale": None},
                    "execution_sequence": {"rank": rank, "lane": "standard", "owner": "mago", "rationale": ["explicit technical sequence"]}}
            return RegistryRecord(self.board / "registry" / f"{sid}.yaml", data)
        urgent_later = record("urgent-later", "urgent", 20)
        low_first = record("low-first", "low", 10)
        ordered = topological_order([urgent_later, low_first])
        self.assertEqual([item.feature_key for item in ordered], ["low-first", "urgent-later"])

    def test_local_priority_contract_validator_passes(self):
        module = load_script("validate_priority_contract.py")
        self.assertEqual(module.collect_errors(ROOT), [])


if __name__ == "__main__":
    unittest.main()
