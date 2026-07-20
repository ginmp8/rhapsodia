from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from board_contract import validate_board  # noqa: E402
from magia_utils import (  # noqa: E402
    board_root_path_error,
    parse_cycle_id,
    parse_spec_id,
    resolve_board_root,
    spec_package_path_error,
    spec_registry_path,
)

CYCLE = "cycle-2026-04-20-q2-delivery"
SPEC = "spec-2026-04-20-csv-export-filtered-columns"


def build_board(tmp_path: Path, *, dependency_status: str = "done") -> tuple[Path, str]:
    root = tmp_path / "docs" / "boards" / "onboarding" / "2026" / "cycles" / CYCLE
    registry = root / "registry"
    package = root / "specs" / SPEC
    registry.mkdir(parents=True)
    package.mkdir(parents=True)
    (root / "cycle.yaml").write_text(
        f"kind: mago-cycle\ncycle_id: {CYCLE}\ncycle_key: q2-delivery\nboard_id: onboarding\nyear: 2026\ncreated_at: 2026-04-20T00:00:00Z\ncreated_by: test\nstatus: in_progress\n",
        encoding="utf-8",
    )
    (registry / f"{SPEC}.yaml").write_text(
        f"kind: mago-spec\nspec_id: {SPEC}\ncycle_id: {CYCLE}\nfeature_key: csv-export-filtered-columns\nfeature_version: 0.1.0\ntitle: CSV Export Filtered Columns\ntype: feature\nclassification: internal\ncreated_at: 2026-04-20T00:00:00Z\nstatus: planned\npriority: normal\norder_hint: null\ndepends_on_features: []\ndepends_on_specs: []\nsupersedes: []\nsuperseded_by: null\nhandoff:\n  status: ready_for_prepare_define\n  downstream_mode: define\n  package_shape: full\n  source_candidates: []\n  seed_artifacts: []\n  blockers: []\nimported_from: null\n",
        encoding="utf-8",
    )
    (package / "manifest.yaml").write_text(
        f"kind: mago-spec-manifest\nspec_id: {SPEC}\ncycle_id: {CYCLE}\nfeature_key: csv-export-filtered-columns\ntitle: CSV Export Filtered Columns\ntype: feature\nclassification: internal\nstatus: planned\nphase: define\nfeature_version: 0.1.0\ncreated_at: 2026-04-20T00:00:00Z\nsource_of_truth:\n  registry: ../../registry/{SPEC}.yaml\n  prd: prd.md\n  tasks: tasks.md\n  validation: validation.md\n  notes: notes.md\ntraceability:\n  primary_discovery_file: ''\n  supporting_discovery_files: []\n  discovery_frontier: ''\n",
        encoding="utf-8",
    )
    for name in ("prd.md", "notes.md", "validation.md"):
        (package / name).write_text(f"# {name}\n", encoding="utf-8")
    (package / "tasks.md").write_text(
        "# Tasks\n\n- [ ] task001: First task\n- [ ] task002: Second task\n",
        encoding="utf-8",
    )
    return root, SPEC


def test_suffix_free_identifiers_are_accepted_without_generated_components():
    assert parse_cycle_id("cycle-2026-04-20-q2-delivery") == {"date": "2026-04-20", "key": "q2-delivery"}
    assert parse_spec_id("spec-2026-04-20-csv-export-filtered-columns") == {
        "date": "2026-04-20",
        "feature": "csv-export-filtered-columns",
    }


@pytest.mark.parametrize(
    ("parser", "value"),
    [
        (parse_cycle_id, "cycle-2026-04-20-q2-delivery--01jt1b2c3d4e5f6g7h8j9kmnpq"),
        (parse_spec_id, "spec-2026-04-20-csv-export--01jt1b2c3d4e5f6g7h8j9kmnpq"),
        (parse_spec_id, "spec001"),
    ],
)
def test_legacy_or_shorthand_identifiers_are_rejected(parser, value: str):
    with pytest.raises(ValueError):
        parser(value)


def test_board_registry_and_package_paths_resolve_from_suffix_free_ids(tmp_path: Path):
    repo_root = tmp_path
    resolved = resolve_board_root(
        repo_root,
        board_id="onboarding",
        year="2026",
        cycle_id=CYCLE,
    )
    assert resolved == repo_root / "docs" / "boards" / "onboarding" / "2026" / "cycles" / CYCLE
    assert spec_registry_path(resolved, SPEC) == resolved / "registry" / f"{SPEC}.yaml"
    assert spec_package_path_error(resolved / "specs" / SPEC) is None


def test_canonical_path_shape(tmp_path: Path):
    root, spec = build_board(tmp_path)
    assert board_root_path_error(root) is None
    assert spec_package_path_error(root / "specs" / spec) is None
    old = tmp_path / "docs" / "boards" / "onboarding" / "v1"
    assert board_root_path_error(old) is not None


def test_board_contract_is_valid(tmp_path: Path):
    root, _ = build_board(tmp_path)
    assert validate_board(root) == []


def test_generated_aggregate_is_rejected(tmp_path: Path):
    root, _ = build_board(tmp_path)
    (root / "spec-catalog.yaml").write_text("specs: []\n", encoding="utf-8")
    assert any("generated projection" in error for error in validate_board(root))
