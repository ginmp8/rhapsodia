from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from magia_utils import load_yaml  # noqa: E402
from test_board_contract import CYCLE, build_board  # noqa: E402


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def write_execution_evidence(package: Path, task_id: str, status: str):
    (package / "implementation-notes.md").write_text(
        f"# Implementation Notes\n\n## Execution Log\n\n### {task_id} - Executed task\n\n- Status: {status}\n- Summary: test execution\n- Changes: none\n- Context Docs: none\n- Decisions: none\n- Follow-Ups: none\n- Blockers: none\n",
        encoding="utf-8",
    )
    (package / "validation-evidence.md").write_text(
        f"# Validation Evidence\n\n## Execution Run - {task_id}\n\n### Executed Checks\n\n- test: passed\n",
        encoding="utf-8",
    )


def test_first_done_task_keeps_spec_in_progress(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    sync = load_script("sync_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 0
    assert load_yaml(root / "registry" / f"{spec_id}.yaml")["status"] == "in_progress"
    manifest = load_yaml(package / "manifest.yaml")
    assert manifest["status"] == "in_progress"
    assert manifest["phase"] == "execute"


def test_blocked_execution_preserves_open_checkbox_and_syncs_blocked_state(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "blocked")
    sync = load_script("sync_execution_state.py")
    validate = load_script("validate_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "blocked"]) == 0
    assert "- [ ] task001:" in (package / "tasks.md").read_text(encoding="utf-8")
    assert load_yaml(root / "registry" / f"{spec_id}.yaml")["status"] == "blocked"
    manifest = load_yaml(package / "manifest.yaml")
    assert manifest["status"] == "blocked"
    assert manifest["phase"] == "execute"
    assert validate.main([str(root), "--spec-id", spec_id]) == 0


def test_all_done_tasks_close_spec(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "tasks.md").write_text("# Tasks\n\n- [x] task001: First task\n- [ ] task002: Second task\n", encoding="utf-8")
    write_execution_evidence(package, "task002", "done")
    sync = load_script("sync_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task002", "--status", "done"]) == 0
    assert load_yaml(root / "registry" / f"{spec_id}.yaml")["status"] == "done"
    manifest = load_yaml(package / "manifest.yaml")
    assert manifest["status"] == "done"
    assert manifest["phase"] == "done"


def test_state_validator_requires_matching_evidence(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    sync = load_script("sync_execution_state.py")
    validate = load_script("validate_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 0
    assert validate.main([str(root), "--spec-id", spec_id]) == 0


def test_readiness_blocks_unfinished_spec_dependency(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    dependency = "spec-2026-04-19-foundation"
    registry = root / "registry"
    (registry / f"{dependency}.yaml").write_text(
        f"kind: mago-spec\nspec_id: {dependency}\ncycle_id: {CYCLE}\nfeature_key: foundation\nfeature_version: 0.1.0\ntitle: Foundation\ntype: feature\nclassification: internal\ncreated_at: 2026-04-19T00:00:00Z\nstatus: in_progress\npriority: normal\norder_hint: null\ndepends_on_features: []\ndepends_on_specs: []\nsupersedes: []\nsuperseded_by: null\nhandoff:\n  status: ready_for_prepare_define\n  downstream_mode: define\n  package_shape: full\n  source_candidates: []\n  seed_artifacts: []\n  blockers: []\nimported_from: null\n",
        encoding="utf-8",
    )
    selected = registry / f"{spec_id}.yaml"
    selected.write_text(selected.read_text().replace("depends_on_specs: []", f"depends_on_specs:\n  - {dependency}"), encoding="utf-8")
    readiness = load_script("validate_execution_readiness.py")
    assert readiness.main([str(root), "--spec-id", spec_id, "--task-id", "task001"]) == 1


def test_adapt_legacy_records_inside_canonical_package(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "notes.md").write_text(
        "# Notes\n\nLegacy source identity: spec-2026-04-20-csv-export--01jt1b2c3d4e5f6g7h8j9kmnpq\n\n## Execution Log\n\n### task001 - legacy\n- Status: done\n- Summary: legacy completion\n",
        encoding="utf-8",
    )
    (package / "validation.md").write_text("# Validation\n\n## Legacy task001 result\n", encoding="utf-8")
    adapt = load_script("adapt_legacy_execution_records.py")
    assert adapt.main([str(root), "--spec-id", spec_id]) == 0
    assert (package / "implementation-notes.md").is_file()
    assert (package / "validation-evidence.md").is_file()
    assert "--01jt1b2c3d4e5f6g7h8j9kmnpq" in (package / "notes.md").read_text(encoding="utf-8")


def test_adapt_rejects_legacy_ulid_as_active_spec_id(tmp_path: Path):
    root, _ = build_board(tmp_path)
    adapt = load_script("adapt_legacy_execution_records.py")
    assert adapt.main([
        str(root),
        "--spec-id",
        "spec-2026-04-20-csv-export--01jt1b2c3d4e5f6g7h8j9kmnpq",
    ]) == 1


def test_heal_repairs_checkbox_last_execution_and_registry(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    heal = load_script("heal_execution_state.py")
    validate = load_script("validate_execution_state.py")
    assert heal.main([str(root), "--spec-id", spec_id]) == 0
    tasks = (package / "tasks.md").read_text(encoding="utf-8")
    assert "- [x] task001:" in tasks
    assert load_yaml(root / "registry" / f"{spec_id}.yaml")["status"] == "in_progress"
    manifest = load_yaml(package / "manifest.yaml")
    assert manifest["status"] == "in_progress"
    assert manifest["phase"] == "execute"
    assert manifest["last_execution"]["task_id"] == "task001"
    assert validate.main([str(root), "--spec-id", spec_id]) == 0


def test_close_wrapper_preserves_full_closure_flow(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    close = load_script("close_execution_state.py")
    assert close.main([
        str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done",
        "--summary", "completed first task", "--files-changed", "src/example.py",
    ]) == 0
    manifest = load_yaml(package / "manifest.yaml")
    assert manifest["last_execution"]["summary"] == "completed first task"
    assert manifest["last_execution"]["files_changed"] == ["src/example.py"]


def test_write_execution_log_uses_canonical_spec_id(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    writer = load_script("write_execution_log.py")
    assert writer.main([
        str(root), "--spec-id", spec_id, "--task-id", "task001",
        "--status", "in_progress", "--summary", "started implementation",
        "--change", "src/example.py",
    ]) == 0
    notes = (root / "specs" / spec_id / "implementation-notes.md").read_text(encoding="utf-8")
    assert "### task001 - First task" in notes
    assert "- Status: in_progress" in notes


def test_repo_board_validator_preserves_placement_and_placeholder_checks(tmp_path: Path):
    root, _ = build_board(tmp_path)
    validator = load_script("validate_repo_board.py")
    repo_root = tmp_path
    assert validator.main([str(repo_root), "--board-root", str(root)]) == 0
    (root / "specs" / next((root / "specs").iterdir()).name / "prd.md").write_text("# PRD\n\n<unresolved>\n", encoding="utf-8")
    assert validator.main([str(repo_root), "--board-root", str(root)]) == 1
