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

from mago_utils import (
    CANONICAL_CYCLE_KIND,
    CANONICAL_SPEC_KIND,
    make_cycle_id,
    make_spec_id,
    parse_cycle_id,
    parse_legacy_cycle_id,
    parse_legacy_spec_id,
    parse_spec_id,
)
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
        self.cycle_id = make_cycle_id("sprint-15", "2026-07-19")
        self.board = self.repo / "docs" / "boards" / "firstaccess" / "2026" / "cycles" / self.cycle_id
        (self.board / "registry").mkdir(parents=True)
        (self.board / "specs").mkdir()
        self.write_yaml(self.board / "cycle.yaml", {
            "kind": CANONICAL_CYCLE_KIND,
            "cycle_id": self.cycle_id,
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

    def add_spec(
        self,
        feature: str,
        dependencies: list[str] | None = None,
        status: str = "planned",
        created_date: str = "2026-07-19",
    ) -> str:
        spec_id = make_spec_id(feature, created_date)
        self.write_yaml(self.board / "registry" / f"{spec_id}.yaml", {
            "kind": CANONICAL_SPEC_KIND,
            "spec_id": spec_id,
            "cycle_id": self.cycle_id,
            "feature_key": feature,
            "feature_version": "0.1.0",
            "title": feature.replace("-", " ").title(),
            "type": "feature",
            "classification": "internal",
            "profile": "standard",
            "created_at": f"{created_date}T13:00:00Z",
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

    def spec_command(self, feature: str, title: str) -> list[str]:
        return [
            sys.executable,
            "-B",
            str(SCRIPTS / "create_planning_identity.py"),
            "spec",
            "--board-root",
            str(self.board),
            "--feature-key",
            feature,
            "--title",
            title,
            "--created-at",
            "2026-07-19T14:00:00Z",
        ]

    def test_identity_round_trip(self) -> None:
        cycle_id = make_cycle_id("q2-delivery", "2026-04-20")
        spec_id = make_spec_id("csv-export-filtered-columns", "2026-04-20")
        cycle = parse_cycle_id(cycle_id)
        spec = parse_spec_id(spec_id)
        self.assertEqual(cycle_id, "cycle-2026-04-20-q2-delivery")
        self.assertEqual(spec_id, "spec-2026-04-20-csv-export-filtered-columns")
        self.assertEqual(cycle, {"date": "2026-04-20", "key": "q2-delivery"})
        self.assertEqual(spec, {"date": "2026-04-20", "feature": "csv-export-filtered-columns"})

    def test_cycle_identity_script_creates_and_reuses_canonical_path(self) -> None:
        command = [
            sys.executable,
            "-B",
            str(SCRIPTS / "create_planning_identity.py"),
            "cycle",
            "--repo-root",
            str(self.repo),
            "--board-id",
            "delivery",
            "--cycle-key",
            "q2-delivery",
            "--created-at",
            "2026-04-20T10:00:00Z",
        ]
        first = subprocess.run(command, capture_output=True, text=True)
        second = subprocess.run(command, capture_output=True, text=True)
        expected = self.repo / "docs" / "boards" / "delivery" / "2026" / "cycles" / "cycle-2026-04-20-q2-delivery"
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("REUSED: identical identity already exists", second.stderr)
        self.assertTrue((expected / "cycle.yaml").is_file())
        cycle_payload = yaml.safe_load((expected / "cycle.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("cycle_uid", cycle_payload)
        self.assertTrue((expected / "registry").is_dir())
        self.assertTrue((expected / "specs").is_dir())
        self.assertTrue((expected / "candidates").is_dir())

    def test_legacy_ulid_ids_are_read_only_adapt_inputs_not_canonical(self) -> None:
        legacy_cycle = f"cycle-2026-04-20-q2-delivery--{ULID_A}"
        legacy_spec = f"spec-2026-04-20-csv-export--{ULID_B}"
        self.assertEqual(parse_legacy_cycle_id(legacy_cycle)["ulid"], ULID_A)
        self.assertEqual(parse_legacy_spec_id(legacy_spec)["ulid"], ULID_B)
        for value, parser in (
            (legacy_cycle, parse_cycle_id),
            (legacy_spec, parse_spec_id),
            ("cycle001", parse_cycle_id),
            ("spec001", parse_spec_id),
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parser(value)

    def test_invalid_dates_and_non_kebab_ids_are_rejected(self) -> None:
        invalid = (
            ("cycle-2026-02-30-q2-delivery", parse_cycle_id),
            ("spec-2026-02-30-csv-export", parse_spec_id),
            ("cycle-2026-04-20-Q2-Delivery", parse_cycle_id),
            ("spec-2026-04-20-csv_export", parse_spec_id),
            ("cycle-2026-04-20-q2--delivery", parse_cycle_id),
            ("spec-2026-04-20-csv--export", parse_spec_id),
        )
        for value, parser in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parser(value)

    def test_independent_specs_validate_and_render_deterministically(self) -> None:
        first = self.add_spec("audit-trail")
        second = self.add_spec("compliance-events", [first])
        report = validate(self.board)
        self.assertEqual(report.status, "pass", report.errors)
        catalog_a, queue_a = build_views(self.board)
        catalog_b, queue_b = build_views(self.board)
        self.assertEqual(catalog_a, catalog_b)
        self.assertEqual(queue_a, queue_b)
        self.assertEqual([item["spec_id"] for item in catalog_a["specs"]], [first, second])

    def test_duplicate_active_feature_is_semantic_conflict(self) -> None:
        self.add_spec("audit-trail", created_date="2026-07-19")
        self.add_spec("audit-trail", created_date="2026-07-20")
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("duplicate feature_key" in error for error in report.errors))

    def test_distinct_specs_require_distinct_feature_keys_regardless_of_status(self) -> None:
        self.add_spec("audit-trail", status="done", created_date="2026-07-19")
        self.add_spec("audit-trail", status="cancelled", created_date="2026-07-20")
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("duplicate feature_key" in error for error in report.errors))

    def test_missing_dependency_is_rejected(self) -> None:
        missing = make_spec_id("missing-feature", "2026-07-19")
        self.add_spec("audit-trail", [missing])
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("missing dependency" in error for error in report.errors))

    def test_dependency_cycle_is_rejected(self) -> None:
        first = make_spec_id("audit-trail", "2026-07-19")
        second = make_spec_id("compliance-events", "2026-07-19")
        self.add_spec("audit-trail", [second])
        self.add_spec("compliance-events", [first])
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("dependency cycle" in error for error in report.errors))

    def test_shared_aggregate_files_are_rejected(self) -> None:
        self.add_spec("audit-trail")
        (self.board / "spec-catalog.yaml").write_text("kind: mago-spec-catalog\n", encoding="utf-8")
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("noncanonical" in error for error in report.errors))

    def test_identity_script_creates_two_specs_without_counter_coordination(self) -> None:
        first = subprocess.run(self.spec_command("audit-trail", "Audit Trail"), capture_output=True, text=True)
        second = subprocess.run(self.spec_command("compliance-events", "Compliance Events"), capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        paths = sorted((self.board / "registry").glob("*.yaml"))
        self.assertEqual([path.name for path in paths], [
            "spec-2026-07-19-audit-trail.yaml",
            "spec-2026-07-19-compliance-events.yaml",
        ])
        for path in paths:
            self.assertNotIn("spec_uid", yaml.safe_load(path.read_text(encoding="utf-8")))

    def test_identical_identity_is_reused_without_overwrite(self) -> None:
        command = self.spec_command("audit-trail", "Audit Trail")
        first = subprocess.run(command, capture_output=True, text=True)
        path = self.board / "registry" / "spec-2026-07-19-audit-trail.yaml"
        original = path.read_bytes()
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("REUSED: identical identity already exists", second.stderr)
        self.assertEqual(path.read_bytes(), original)

    def test_legacy_ulid_argument_is_rejected_without_overwrite(self) -> None:
        completed = subprocess.run(
            self.spec_command("audit-trail", "Audit Trail") + ["--ulid", ULID_B],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("unrecognized arguments: --ulid", completed.stderr)
        self.assertFalse(any((self.board / "registry").glob("*.yaml")))

    def test_identity_collision_is_rejected_without_suffix_or_overwrite(self) -> None:
        first = subprocess.run(self.spec_command("audit-trail", "Audit Trail"), capture_output=True, text=True)
        path = self.board / "registry" / "spec-2026-07-19-audit-trail.yaml"
        original = path.read_bytes()
        second = subprocess.run(self.spec_command("audit-trail", "Different Title"), capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 2, second.stdout + second.stderr)
        self.assertIn("identity collision; no suffix or counter was generated", second.stdout)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(len(list((self.board / "registry").glob("*.yaml"))), 1)

    def test_atomic_exclusive_creation_under_collision(self) -> None:
        first = subprocess.Popen(self.spec_command("audit-trail", "Audit Trail"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(self.spec_command("audit-trail", "Different Title"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_out, first_err = first.communicate()
        second_out, second_err = second.communicate()
        self.assertEqual(sorted([first.returncode, second.returncode]), [0, 2], first_out + first_err + second_out + second_err)
        path = self.board / "registry" / "spec-2026-07-19-audit-trail.yaml"
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertIn(payload["title"], {"Audit Trail", "Different Title"})
        self.assertEqual(len(list((self.board / "registry").glob("*.yaml"))), 1)
        self.assertFalse(any((self.board / "registry").glob(".*.tmp")))

    def test_invalid_semver_is_rejected_before_write(self) -> None:
        command = self.spec_command("audit-trail", "Audit Trail") + ["--feature-version", "latest"]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(any((self.board / "registry").glob("*.yaml")))

    def test_invalid_timestamp_is_rejected_before_write(self) -> None:
        command = self.spec_command("audit-trail", "Audit Trail")
        timestamp_index = command.index("--created-at") + 1
        command[timestamp_index] = "2026-07-19-no-timezone"
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(any((self.board / "registry").glob("*.yaml")))

    def test_offset_timestamp_is_normalized_to_utc(self) -> None:
        command = self.spec_command("audit-trail", "Audit Trail")
        timestamp_index = command.index("--created-at") + 1
        command[timestamp_index] = "2026-07-19T17:00:00+03:00"
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        path = next((self.board / "registry").glob("*.yaml"))
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["created_at"], "2026-07-19T14:00:00Z")

    def test_repo_validator_rejects_parallel_duplicate_active_cycle_key(self) -> None:
        from validate_repo_board import validate as validate_repo_board

        sibling_id = make_cycle_id("sprint-15", "2026-07-20")
        sibling = self.board.parent / sibling_id
        self.write_yaml(sibling / "cycle.yaml", {
            "kind": CANONICAL_CYCLE_KIND,
            "cycle_id": sibling_id,
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
        spec_id = self.add_spec("audit-trail")
        package = self.board / "specs" / spec_id
        package.mkdir()
        self.write_yaml(package / "manifest.yaml", {
            "kind": "mago-spec-manifest",
            "spec_id": spec_id,
            "cycle_id": self.cycle_id,
            "feature_key": "different-feature",
        })
        report = validate(self.board)
        self.assertEqual(report.status, "fail")
        self.assertTrue(any("feature_key" in error and "match registry" in error for error in report.errors))

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
