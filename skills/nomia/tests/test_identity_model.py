from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nomia_utils import (
    infer_year_from_cycle_id,
    is_legacy_cycle_id,
    is_legacy_spec_id,
    parse_cycle_id,
    parse_canonical_board_root,
    parse_spec_id,
    resolve_board_root,
    validate_cycle_id_format,
    validate_id_provenance,
    validate_spec_id_format,
)
from validate_board_paths import validate_path
from validate_contracts import validate_actor
from validate_ops import validate as validate_ops
from validate_roadmap import validate_feature_map, validate_roadmap
from write_ops_scaffold import render

CYCLE_ID = "cycle-2026-04-20-workspace-admin"
SPEC_ID = "spec-2026-04-20-saved-query-sharing-controls"
LEGACY_CYCLE_ID = "2026-04-20-workspace-admin--01jt1a2b3c4d5e6f7g8h9jkmnp"
LEGACY_PREFIXED_CYCLE_ID = "cycle-2026-04-20-q2-delivery--01jt1b2c3d4e5f6g7h8j9kmnpq"
LEGACY_SPEC_ID = "spec-2026-04-20-csv-export--01jt1b2c3d4e5f6g7h8j9kmnpq"


class IdentityModelTests(unittest.TestCase):

    def test_exact_canonical_examples_are_accepted(self) -> None:
        self.assertIsNone(validate_cycle_id_format("cycle-2026-04-20-q2-delivery"))
        self.assertIsNone(validate_spec_id_format("spec-2026-04-20-csv-export-filtered-columns"))

    def test_former_ulid_ids_are_read_only_legacy_and_rejected_operationally(self) -> None:
        self.assertTrue(is_legacy_cycle_id(LEGACY_CYCLE_ID))
        self.assertTrue(is_legacy_cycle_id(LEGACY_PREFIXED_CYCLE_ID))
        self.assertTrue(is_legacy_spec_id(LEGACY_SPEC_ID))
        self.assertIsNotNone(validate_cycle_id_format(LEGACY_CYCLE_ID))
        self.assertIsNotNone(validate_cycle_id_format(LEGACY_PREFIXED_CYCLE_ID))
        self.assertIsNotNone(validate_spec_id_format(LEGACY_SPEC_ID))
        with self.assertRaises(ValueError):
            parse_cycle_id(LEGACY_CYCLE_ID)
        with self.assertRaises(ValueError):
            parse_cycle_id(LEGACY_PREFIXED_CYCLE_ID)
        with self.assertRaises(ValueError):
            parse_spec_id(LEGACY_SPEC_ID)

    def test_candidate_spec_id_absent_or_null_is_allowed(self) -> None:
        roadmap_text = """schema_version: 1
roadmap_id: sample-roadmap
title: Sample roadmap
owner: product
horizon: now
features:
  - feature_key: sample-feature
    name: Sample feature
    problem: Sample problem
    outcome: Sample outcome
    horizon: now
    commitment: targeted
    confidence: medium
    dependencies: []
    ready_for_spec: true
"""
        feature_map_text = """schema_version: 1
roadmap_id: sample-roadmap
features:
  - feature_key: sample-feature
    ready_for_spec: true
    candidate_spec_id: null
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            roadmap_path = root / "roadmap.yaml"
            feature_map_path = root / "feature-map.yaml"
            roadmap_path.write_text(roadmap_text, encoding="utf-8")
            feature_map_path.write_text(feature_map_text, encoding="utf-8")
            errors, _, features, roadmap_id = validate_roadmap(roadmap_path)
            self.assertEqual(errors, [])
            map_errors, _ = validate_feature_map(feature_map_path, features, roadmap_id)
            self.assertEqual(map_errors, [])

    def test_external_id_requires_provenance(self) -> None:
        self.assertIsNone(
            validate_id_provenance("user-supplied", id_value=SPEC_ID, field_name="spec_id_provenance")
        )
        self.assertIsNotNone(validate_id_provenance(None, id_value=SPEC_ID, field_name="spec_id_provenance"))
        with tempfile.TemporaryDirectory() as tmp:
            valid_path = Path(tmp) / "valid-ops.yaml"
            valid_path.write_text(render(SPEC_ID, "user-supplied"), encoding="utf-8")
            valid_errors, _ = validate_ops(valid_path)
            self.assertEqual(valid_errors, [])

            invalid_path = Path(tmp) / "invalid-ops.yaml"
            invalid_path.write_text(render(SPEC_ID), encoding="utf-8")
            invalid_errors, _ = validate_ops(invalid_path)
            self.assertTrue(any("spec_id_provenance" in error for error in invalid_errors))

    def test_unknown_null_and_empty_lists_are_preserved(self) -> None:
        scaffold = render(None)
        self.assertIn("spec_id: null", scaffold)
        self.assertIn("spec_id_provenance: null", scaffold)
        self.assertIn("state: unknown", scaffold)
        self.assertIn("stakeholders: []", scaffold)
        self.assertIn("blockers: []", scaffold)

    def test_cycle_id_is_date_readable_and_year_is_inferred(self) -> None:
        parsed = parse_cycle_id(CYCLE_ID)
        self.assertEqual(parsed["cycle_key"], "workspace-admin")
        self.assertEqual(infer_year_from_cycle_id(CYCLE_ID), "2026")

    def test_spec_id_is_date_readable_and_feature_bound(self) -> None:
        parsed = parse_spec_id(SPEC_ID)
        self.assertEqual(parsed["feature_key"], "saved-query-sharing-controls")

    def test_impossible_dates_are_rejected(self) -> None:
        for cycle_id in (
            "cycle-2026-02-30-invalid-date",
            "cycle-2026-13-01-invalid-month",
            "cycle-0000-01-01-invalid-year",
        ):
            with self.subTest(cycle_id=cycle_id), self.assertRaises(ValueError):
                parse_cycle_id(cycle_id)
        for spec_id in (
            "spec-2026-02-30-invalid-date",
            "spec-2026-13-01-invalid-month",
            "spec-0000-01-01-invalid-year",
        ):
            with self.subTest(spec_id=spec_id), self.assertRaises(ValueError):
                parse_spec_id(spec_id)

    def test_valid_leap_day_is_accepted(self) -> None:
        self.assertEqual(parse_cycle_id("cycle-2028-02-29-leap-cycle")["date"], "2028-02-29")
        self.assertEqual(parse_spec_id("spec-2028-02-29-leap-feature")["date"], "2028-02-29")

    def test_board_root_uses_year_cycles_and_cycle_id(self) -> None:
        root = resolve_board_root(Path("/repo"), board_id="workspace-admin", year="2026", cycle_id=CYCLE_ID)
        self.assertEqual(
            root.as_posix(),
            f"/repo/docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}",
        )

    def test_year_conflict_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_board_root(Path("/repo"), board_id="workspace-admin", year="2025", cycle_id=CYCLE_ID)

    def test_board_root_override_is_confined_and_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            canonical = repo_root / "docs" / "boards" / "workspace-admin" / "2026" / "cycles" / CYCLE_ID
            resolved = resolve_board_root(
                repo_root,
                board_root_override=canonical,
                board_id="workspace-admin",
                year="2026",
                cycle_id=CYCLE_ID,
            )
            self.assertEqual(resolved, canonical.resolve())

            with self.assertRaisesRegex(ValueError, "inside the repository root"):
                resolve_board_root(repo_root, board_root_override=Path(tmp) / "outside")

            with self.assertRaisesRegex(ValueError, "must match"):
                resolve_board_root(repo_root, board_root_override=canonical / "specs")

            with self.assertRaisesRegex(ValueError, "board_id.*conflicts"):
                resolve_board_root(
                    repo_root,
                    board_root_override=canonical,
                    board_id="different-board",
                )

    def test_canonical_board_root_parser_rejects_nested_paths(self) -> None:
        canonical = f"/repo/docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}"
        self.assertEqual(parse_canonical_board_root(canonical)["cycle_id"], CYCLE_ID)
        with self.assertRaises(ValueError):
            parse_canonical_board_root(f"{canonical}/specs")

    def test_canonical_nomia_paths_are_accepted(self) -> None:
        paths = [
            f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/roadmap.yaml",
            f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/specs/{SPEC_ID}/ops.yaml",
        ]
        for path in paths:
            self.assertEqual(validate_path(path, "workspace-admin", CYCLE_ID, "2026"), [])

    def test_legacy_sequence_spec_id_is_rejected(self) -> None:
        for legacy_id in ("spec001", "spec022"):
            errors = validate_path(
                f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/specs/{legacy_id}/ops.yaml",
                "workspace-admin",
                CYCLE_ID,
                "2026",
            )
            self.assertTrue(any("spec-YYYY-MM-DD-feature-key" in error for error in errors))

    def test_impossible_spec_date_in_path_is_rejected(self) -> None:
        invalid_spec_id = "spec-2026-02-30-impossible-date"
        errors = validate_path(
            f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/specs/{invalid_spec_id}/ops.yaml",
            "workspace-admin",
            CYCLE_ID,
            "2026",
        )
        self.assertTrue(any("real calendar date" in error for error in errors))

    def test_nomia_cannot_write_planning_registry(self) -> None:
        errors = validate_actor(
            "nomia",
            [f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/registry/{SPEC_ID}.yaml"],
        )
        self.assertTrue(any("must not write Mago planning or registry artifact" in error for error in errors))

    def test_magias_narrow_registry_sync_is_not_rejected(self) -> None:
        errors = validate_actor(
            "magia",
            [f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/registry/{SPEC_ID}.yaml"],
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
