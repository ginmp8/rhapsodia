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
        f"# Validation Evidence\n\n## Execution Run - {task_id}\n\n"
        "### Executed Checks\n\n"
        "| Check | Command or method | Result | Evidence |\n"
        "|---|---|---|---|\n"
        "| targeted test | `python -m pytest tests/test_target.py` | passed | command exited 0 |\n\n"
        "### Traceability\n\n"
        "| Requirement or acceptance criterion | Check | Result | Evidence |\n"
        "|---|---|---|---|\n"
        f"| {task_id} objective | targeted test | passed | command exited 0 |\n\n"
        "### Failed Checks\n\n- `none`\n",
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
    (package / "tasks.md").write_text("# Tasks\n\n- [x] task001: Implement filtered export behavior\n- [ ] task002: Validate filtered export compatibility\n", encoding="utf-8")
    write_execution_evidence(package, "task001", "done")
    notes = (package / "implementation-notes.md").read_text(encoding="utf-8")
    validation = (package / "validation-evidence.md").read_text(encoding="utf-8")
    write_execution_evidence(package, "task002", "done")
    (package / "implementation-notes.md").write_text(
        notes.rstrip() + "\n\n" + (package / "implementation-notes.md").read_text(encoding="utf-8").split("## Execution Log\n", 1)[1].lstrip(),
        encoding="utf-8",
    )
    (package / "validation-evidence.md").write_text(
        validation.rstrip() + "\n\n" + (package / "validation-evidence.md").read_text(encoding="utf-8").split("# Validation Evidence\n", 1)[1].lstrip(),
        encoding="utf-8",
    )
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
        f"kind: mago-spec\nspec_id: {dependency}\ncycle_id: {CYCLE}\nfeature_key: foundation\nfeature_version: 0.1.0\ntitle: Foundation\ntype: feature\nclassification: internal\ncreated_at: 2026-04-19T00:00:00Z\nstatus: in_progress\nbusiness_priority:\n  level: unknown\n  owner: nomia\n  source: null\n  observed_at: null\ntechnical_criticality:\n  level: normal\n  owner: mago\n  rationale: null\nexecution_sequence:\n  rank: null\n  lane: standard\n  owner: mago\n  rationale: []\ndepends_on_features: []\ndepends_on_specs: []\nsupersedes: []\nsuperseded_by: null\nhandoff:\n  status: ready_for_prepare_define\n  downstream_mode: define\n  package_shape: full\n  source_candidates: []\n  seed_artifacts: []\n  blockers: []\nimported_from: null\n",
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
    assert "### task001 - Implement filtered export behavior" in notes
    assert "- Status: in_progress" in notes


def test_repo_board_validator_preserves_placement_and_placeholder_checks(tmp_path: Path):
    root, _ = build_board(tmp_path)
    validator = load_script("validate_repo_board.py")
    repo_root = tmp_path
    assert validator.main([str(repo_root), "--board-root", str(root)]) == 0
    (root / "specs" / next((root / "specs").iterdir()).name / "prd.md").write_text("# PRD\n\n<unresolved>\n", encoding="utf-8")
    assert validator.main([str(repo_root), "--board-root", str(root)]) == 1


def test_done_rejects_empty_validation_heading(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "implementation-notes.md").write_text(
        "# Implementation Notes\n\n## Execution Log\n\n### task001 - Implement filtered export behavior\n\n"
        "- Status: done\n- Summary: claimed done\n- Changes: none\n- Context Docs: none\n"
        "- Decisions: none\n- Follow-Ups: none\n- Blockers: none\n",
        encoding="utf-8",
    )
    (package / "validation-evidence.md").write_text(
        "# Validation Evidence\n\n## Execution Run - task001\n",
        encoding="utf-8",
    )
    sync = load_script("sync_execution_state.py")
    original_tasks = (package / "tasks.md").read_bytes()
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 1
    assert (package / "tasks.md").read_bytes() == original_tasks


def test_done_rejects_not_run_only_and_missing_traceability(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "implementation-notes.md").write_text(
        "# Implementation Notes\n\n## Execution Log\n\n### task001 - Implement filtered export behavior\n\n"
        "- Status: done\n- Summary: claimed done\n- Changes: none\n- Context Docs: none\n"
        "- Decisions: none\n- Follow-Ups: none\n- Blockers: none\n",
        encoding="utf-8",
    )
    (package / "validation-evidence.md").write_text(
        "# Validation Evidence\n\n## Execution Run - task001\n\n### Not-Run Checks\n\n"
        "| Check | Reason not run | Risk |\n|---|---|---|\n| tests | unavailable | unverified |\n",
        encoding="utf-8",
    )
    validate = load_script("validate_execution_state.py")
    errors = validate.validate_task_evidence(package, "task001", "done")
    assert any("passed executed check" in error for error in errors)
    assert any("Traceability" in error for error in errors)


def test_done_rejects_failed_validation(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    validation = package / "validation-evidence.md"
    validation.write_text(
        validation.read_text(encoding="utf-8").replace("### Failed Checks\n\n- `none`", "### Failed Checks\n\n- integration test failed"),
        encoding="utf-8",
    )
    validate = load_script("validate_execution_state.py")
    errors = validate.validate_task_evidence(package, "task001", "done")
    assert any("failed or blocked" in error for error in errors)


def test_done_rejects_meta_or_placeholder_validation_evidence(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    (package / "validation-evidence.md").write_text(
        "# Validation Evidence\n\n## Execution Run - task001\n\n"
        "### Executed Checks\n\n"
        "| Check | Command or method | Result | Evidence |\n"
        "|---|---|---|---|\n"
        "| placeholder test | manual placeholder | passed | no evidence |\n\n"
        "### Traceability\n\n"
        "| Requirement or acceptance criterion | Check | Result | Evidence |\n"
        "|---|---|---|---|\n"
        "| This is not an acceptance criterion | unrelated check | passed | no evidence |\n\n"
        "### Failed Checks\n\n- `none`\n",
        encoding="utf-8",
    )
    validate = load_script("validate_execution_state.py")
    errors = validate.validate_task_evidence(package, "task001", "done")
    assert any("passed executed check" in error for error in errors)
    assert any("passed Traceability row" in error for error in errors)


def test_done_requires_traceability_to_reference_an_executed_check(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    validation = package / "validation-evidence.md"
    validation.write_text(
        validation.read_text(encoding="utf-8").replace(
            "| task001 objective | targeted test | passed | command exited 0 |",
            "| task001 objective | different unexecuted check | passed | command exited 0 |",
        ),
        encoding="utf-8",
    )
    validate = load_script("validate_execution_state.py")
    errors = validate.validate_task_evidence(package, "task001", "done")
    assert any("passed Traceability row" in error for error in errors)


def test_sync_rolls_back_all_files_after_injected_failure(tmp_path: Path, monkeypatch):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    paths = [
        package / "tasks.md",
        package / "manifest.yaml",
        root / "registry" / f"{spec_id}.yaml",
    ]
    originals = {path: path.read_bytes() for path in paths}
    monkeypatch.setenv("MAGIA_TEST_FAIL_AFTER_REPLACE", "1")
    sync = load_script("sync_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 1
    assert {path: path.read_bytes() for path in paths} == originals
    assert not (package / ".magia-state-transaction").exists()
    assert not (package / ".magia-state.lock").exists()


def test_sync_rejects_impossible_execution_date(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    sync = load_script("sync_execution_state.py")
    assert sync.main([
        str(root),
        "--spec-id", spec_id,
        "--task-id", "task001",
        "--status", "done",
        "--date", "2026-02-31",
    ]) == 1


def test_sync_recovers_prepared_interrupted_transaction(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    tasks = package / "tasks.md"
    original = tasks.read_bytes()
    transaction = package / ".magia-state-transaction"
    transaction.mkdir()
    (transaction / "backup-0.bin").write_bytes(original)
    relative = tasks.relative_to(root).as_posix()
    (transaction / "transaction.json").write_text(
        '{"state":"prepared","entries":[{"target":"' + relative + '","backup":"backup-0.bin"}]}',
        encoding="utf-8",
    )
    tasks.write_text("corrupt partial state\n", encoding="utf-8")
    sync = load_script("sync_execution_state.py")
    assert sync.recover_interrupted_transaction(package) is True
    assert tasks.read_bytes() == original
    assert not transaction.exists()


def test_readiness_requires_concrete_prd_acceptance_and_validation(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    readiness = load_script("validate_execution_readiness.py")
    assert readiness.main([str(root), "--spec-id", spec_id, "--task-id", "task001"]) == 0
    (package / "prd.md").write_text("# PRD\n", encoding="utf-8")
    assert readiness.main([str(root), "--spec-id", spec_id, "--task-id", "task001"]) == 1


def test_readiness_rejects_generic_task_and_empty_validation_plan(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "tasks.md").write_text("# Tasks\n\n- [ ] task001: First task\n", encoding="utf-8")
    (package / "validation.md").write_text("# Validation Plan\n", encoding="utf-8")
    readiness = load_script("validate_execution_readiness.py")
    errors = readiness.collect_errors(root, spec_id, "task001")
    assert any("too generic" in error or "three descriptive words" in error for error in errors)
    assert any("concrete planned validation check" in error for error in errors)


def test_heal_uses_recoverable_transaction(tmp_path: Path, monkeypatch):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    paths = [
        package / "tasks.md",
        package / "manifest.yaml",
        root / "registry" / f"{spec_id}.yaml",
    ]
    originals = {path: path.read_bytes() for path in paths}
    monkeypatch.setenv("MAGIA_TEST_FAIL_AFTER_REPLACE", "1")
    heal = load_script("heal_execution_state.py")
    assert heal.main([str(root), "--spec-id", spec_id]) == 1
    assert {path: path.read_bytes() for path in paths} == originals


def test_done_rejects_traceability_source_absent_from_planning(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    evidence = (package / "validation-evidence.md").read_text(encoding="utf-8")
    evidence = evidence.replace("task001 objective", "invented requirement absent from PRD and tasks")
    (package / "validation-evidence.md").write_text(evidence, encoding="utf-8")

    validate = load_script("validate_execution_state.py")
    errors = validate.validate_task_evidence(package, "task001", "done")
    assert any("source resolves to a real PRD objective" in error for error in errors)

    sync = load_script("sync_execution_state.py")
    original_tasks = (package / "tasks.md").read_bytes()
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 1
    assert (package / "tasks.md").read_bytes() == original_tasks


def test_done_accepts_exact_acceptance_criterion_as_traceability_source(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    evidence = (package / "validation-evidence.md").read_text(encoding="utf-8")
    evidence = evidence.replace("task001 objective", "A filtered export contains only the selected columns.")
    (package / "validation-evidence.md").write_text(evidence, encoding="utf-8")

    validate = load_script("validate_execution_state.py")
    assert validate.validate_task_evidence(package, "task001", "done") == []


def test_sync_rejects_unrelated_task_even_with_apparently_valid_evidence(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "tasks.md").write_text(
        "# Tasks\n\n- [ ] task001: Rotate production credentials safely\n",
        encoding="utf-8",
    )
    write_execution_evidence(package, "task001", "done")

    sync = load_script("sync_execution_state.py")
    original_tasks = (package / "tasks.md").read_bytes()
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 1
    assert (package / "tasks.md").read_bytes() == original_tasks
