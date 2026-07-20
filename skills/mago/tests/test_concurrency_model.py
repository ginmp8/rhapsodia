from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mago_utils import CANONICAL_CYCLE_KIND, CANONICAL_SPEC_KIND, make_cycle_id, make_spec_id, parse_cycle_id, parse_spec_id
from render_registry_views import build_views
from validate_concurrent_board import validate

ULID_A = "01k0yq8e2dmm6f5qg3a7x9c4tb"
ULID_B = "01k0yr2k4q9tm8c6n7w5x3p1za"
ULID_C = "01k0yr4m5w2tx7b8q3j6n9c0vd"


class ConcurrencyModelTests(unittest.TestCase):
    def setUp(self) -> None:
        if yaml is None:
            self.skipTest("PyYAML required")
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.cycle_id = make_cycle_id("sprint-15", "2026-07-19", ULID_A)
        self.board = self.repo / "docs" / "boards" / "firstaccess" / "2026" / "cycles" / self.cycle_id
        (self.board / "registry").mkdir(parents=True)
        (self.board / "specs").mkdir()
        self.write_yaml(self.board / "cycle.yaml", {
            "kind": CANONICAL_CYCLE_KIND,
            "cycle_id": self.cycle_id,
            "cycle_uid": ULID_A,
            "cycle_key": "sprint-15",
            "board_id": "firstaccess",
            "year": 2026,
            "created_at": "2026-07-19T12:00:00Z",
            "created_by": "test",
            "status": "planned",
            "proposed_version": "0.3.0",
            "accepted_version": None,
            "planning_revision": 1,
            "imported_from": None,
        })

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_yaml(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def add_spec(self, feature: str, ulid: str, dependencies: list[str] | None = None, status: str = "planned") -> str:
        spec_id = make_spec_id(feature, "2026-07-19", ulid)
        self.write_yaml(self.board / "registry" / f"{spec_id}.yaml", {
            "kind": CANONICAL_SPEC_KIND,
            "spec_id": spec_id,
            "spec_uid": ulid,
            "cycle_id": self.cycle_id,
            "feature_key": feature,
            "feature_version": "0.1.0",
            "title": feature.replace("-", " ").title(),
            "type": "feature",
            "classification": "internal",
            "created_at": "2026-07-19T13:00:00Z",
            "status": status,
            "priority": "normal",
            "order_hint": None,
            "depends_on_features": [],
            "depends_on_specs": dependencies or [],
            "supersedes": [],
            "superseded_by": None,
            "handoff": {
                "status": "needs_discovery",
                "downstream_mode": "define",
                "package_shape": "full",
                "source_candidates": [],
                "seed_artifacts": ["manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"],
                "blockers": [],
            },
            "imported_from": None,
        })
        return spec_id

    def test_identity_round_trip(self) -> None:
        cycle = parse_cycle_id(self.cycle_id)
        spec_id = make_spec_id("audit-trail", "2026-07-19", ULID_B)
        spec = parse_spec_id(spec_id)
        self.assertEqual(cycle["key"], "sprint-15")
        self.assertEqual(spec["feature"], "audit-trail")
        self.assertEqual(spec["ulid"], ULID_B)

    def test_independent_specs_validate_and_render_deterministically(self) -> None:
        first = self.add_spec("audit-trail", ULID_B)
        second = self.add_spec("compliance-events", ULID_C, [first])
        report = validate(self.board)
        self.assertEqual(report.status, "pass", report.errors)
        catalog_a, queue_a = build_views(self.board)
        catalog_b, queue_b = build_views(self.board)
        self.assertEqual(catalog_a, catalog_b)
        self.assertEqual(queue_a, queue_b)
        self.assertEqual([item["spec_id"] for item in catalog_a["specs"]], [first, second])

    def test_duplicate_active_feature_is_semantic_conflict(self) -> None:
        self.add_spec("audit-trail", ULID_B)
        self.add_spec("audit-trail", ULID_C)
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("duplicate active feature_key" in error for error in report.errors))

    def test_dependency_cycle_is_rejected(self) -> None:
        first = make_spec_id("audit-trail", "2026-07-19", ULID_B)
        second = make_spec_id("compliance-events", "2026-07-19", ULID_C)
        self.add_spec("audit-trail", ULID_B, [second])
        self.add_spec("compliance-events", ULID_C, [first])
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("dependency cycle" in error for error in report.errors))

    def test_shared_aggregate_files_are_rejected(self) -> None:
        self.add_spec("audit-trail", ULID_B)
        (self.board / "spec-catalog.yaml").write_text("kind: mago-spec-catalog\n", encoding="utf-8")
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("noncanonical" in error for error in report.errors))

    def test_identity_script_creates_two_specs_without_counter_coordination(self) -> None:
        command = [sys.executable, "-B", str(SCRIPTS / "create_planning_identity.py"), "spec", "--board-root", str(self.board)]
        first = subprocess.run(command + ["--feature-key", "audit-trail", "--title", "Audit Trail", "--created-at", "2026-07-19T14:00:00Z", "--ulid", ULID_B], capture_output=True, text=True)
        second = subprocess.run(command + ["--feature-key", "compliance-events", "--title", "Compliance Events", "--created-at", "2026-07-19T14:00:00Z", "--ulid", ULID_C], capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(len(list((self.board / "registry").glob("*.yaml"))), 2)

    def test_duplicate_ulid_is_rejected_without_overwrite(self) -> None:
        command = [sys.executable, "-B", str(SCRIPTS / "create_planning_identity.py"), "spec", "--board-root", str(self.board), "--feature-key", "audit-trail", "--title", "Audit Trail", "--created-at", "2026-07-19T14:00:00Z", "--ulid", ULID_B]
        first = subprocess.run(command, capture_output=True, text=True)
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 2, second.stdout + second.stderr)
        self.assertEqual(len(list((self.board / "registry").glob("*.yaml"))), 1)

    def test_invalid_semver_is_rejected_before_write(self) -> None:
        command = [sys.executable, "-B", str(SCRIPTS / "create_planning_identity.py"), "spec", "--board-root", str(self.board), "--feature-key", "audit-trail", "--title", "Audit Trail", "--feature-version", "latest", "--created-at", "2026-07-19T14:00:00Z", "--ulid", ULID_B]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(any((self.board / "registry").glob("*.yaml")))

    def test_invalid_timestamp_is_rejected_before_write(self) -> None:
        command = [sys.executable, "-B", str(SCRIPTS / "create_planning_identity.py"), "spec", "--board-root", str(self.board), "--feature-key", "audit-trail", "--title", "Audit Trail", "--created-at", "2026-07-19-no-timezone", "--ulid", ULID_B]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(any((self.board / "registry").glob("*.yaml")))

    def test_offset_timestamp_is_normalized_to_utc(self) -> None:
        command = [sys.executable, "-B", str(SCRIPTS / "create_planning_identity.py"), "spec", "--board-root", str(self.board), "--feature-key", "audit-trail", "--title", "Audit Trail", "--created-at", "2026-07-19T17:00:00+03:00", "--ulid", ULID_B]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        path = next((self.board / "registry").glob("*.yaml"))
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["created_at"], "2026-07-19T14:00:00Z")

    def test_repo_validator_rejects_parallel_duplicate_active_cycle_key(self) -> None:
        from validate_repo_board import validate as validate_repo_board

        sibling_id = make_cycle_id("sprint-15", "2026-07-20", ULID_C)
        sibling = self.board.parent / sibling_id
        self.write_yaml(sibling / "cycle.yaml", {
            "kind": CANONICAL_CYCLE_KIND,
            "cycle_id": sibling_id,
            "cycle_uid": ULID_C,
            "cycle_key": "sprint-15",
            "board_id": "firstaccess",
            "year": 2026,
            "created_at": "2026-07-20T12:00:00Z",
            "created_by": "test",
            "status": "planned",
            "proposed_version": None,
            "accepted_version": None,
            "planning_revision": 1,
            "imported_from": None,
        })
        (sibling / "registry").mkdir()
        (sibling / "specs").mkdir()
        errors, _ = validate_repo_board(self.repo, board_root_override=str(self.board))
        self.assertTrue(any("duplicate active cycle_key" in error for error in errors), errors)

    def test_manifest_identity_mismatch_is_rejected(self) -> None:
        spec_id = self.add_spec("audit-trail", ULID_B)
        package = self.board / "specs" / spec_id
        package.mkdir()
        self.write_yaml(package / "manifest.yaml", {
            "kind": "mago-spec-manifest",
            "spec_id": spec_id,
            "spec_uid": ULID_C,
            "cycle_id": self.cycle_id,
            "feature_key": "audit-trail",
        })
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("spec_uid" in error and "match registry" in error for error in report.errors))

    def test_old_layout_is_not_an_active_board_model(self) -> None:
        from validate_repo_board import validate as validate_repo_board

        old_root = self.repo / "docs" / "boards" / "old" / "01.00.00"
        package = old_root / "specs" / "spec001"
        package.mkdir(parents=True)
        (package / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        errors, _ = validate_repo_board(self.repo, board_root_override=str(old_root))
        self.assertTrue(any("missing canonical cycle.yaml" in error for error in errors), errors)



if __name__ == "__main__":
    unittest.main()
