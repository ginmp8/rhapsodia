from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nomia_utils import infer_year_from_cycle_id, parse_cycle_id, parse_spec_id, resolve_board_root
from validate_board_paths import validate_path
from validate_contracts import validate_actor

CYCLE_ID = "2026-04-20-workspace-admin--01jt1a2b3c4d5e6f7g8h9jkmnp"
SPEC_ID = "spec-2026-04-20-saved-query-sharing-controls--01jt1c2d3e4f5g6h7j8kmnpqrs"


class IdentityModelTests(unittest.TestCase):
    def test_cycle_id_is_date_readable_and_year_is_inferred(self) -> None:
        parsed = parse_cycle_id(CYCLE_ID)
        self.assertEqual(parsed["cycle_key"], "workspace-admin")
        self.assertEqual(infer_year_from_cycle_id(CYCLE_ID), "2026")

    def test_spec_id_is_date_readable_and_feature_bound(self) -> None:
        parsed = parse_spec_id(SPEC_ID)
        self.assertEqual(parsed["feature_key"], "saved-query-sharing-controls")

    def test_board_root_uses_year_cycles_and_cycle_id(self) -> None:
        root = resolve_board_root(Path("/repo"), board_id="workspace-admin", year="2026", cycle_id=CYCLE_ID)
        self.assertEqual(
            root.as_posix(),
            f"/repo/docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}",
        )

    def test_year_conflict_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_board_root(Path("/repo"), board_id="workspace-admin", year="2025", cycle_id=CYCLE_ID)

    def test_canonical_nomia_paths_are_accepted(self) -> None:
        paths = [
            f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/roadmap.yaml",
            f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/specs/{SPEC_ID}/ops.yaml",
        ]
        for path in paths:
            self.assertEqual(validate_path(path, "workspace-admin", CYCLE_ID, "2026"), [])

    def test_legacy_sequence_spec_id_is_rejected(self) -> None:
        errors = validate_path(
            f"docs/boards/workspace-admin/2026/cycles/{CYCLE_ID}/specs/spec022/ops.yaml",
            "workspace-admin",
            CYCLE_ID,
            "2026",
        )
        self.assertTrue(any("spec-YYYY-MM-DD-feature-key--ULID" in error for error in errors))

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
