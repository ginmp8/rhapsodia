from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ORIGINAL_RESOURCES = {
    "SKILL.md",
    "agents/openai.yaml",
    "requirements-test.txt",
    "assets/templates/complexity-reduction-evidence.md.template",
    "assets/templates/contract-change-note.md.template",
    "assets/templates/implementation-adr.md.template",
    "assets/templates/implementation-notes.md.template",
    "assets/templates/migration-execution-note.md.template",
    "assets/templates/observability-note.md.template",
    "assets/templates/runbook.md.template",
    "assets/templates/security-risk-note.md.template",
    "assets/templates/technical-gap-note.md.template",
    "assets/templates/troubleshooting.md.template",
    "assets/templates/validation-evidence.md.template",
    "evals/activation-scenarios.json",
    "examples/activation-scenarios.json",
    "references/artifacts/execution-evidence.md",
    "references/artifacts/execution-records.md",
    "references/canonical-paths.md",
    "references/common-execution.md",
    "references/complexity-reduction-execution.md",
    "references/developer-artifact-standards.md",
    "references/markdown-writing.md",
    "references/modes/adapt.md",
    "references/modes/adhoc.md",
    "references/modes/ralph.md",
    "references/package-delivery.md",
    "references/planning-handoff.md",
    "references/resource-map.md",
    "references/senior-engineering-discipline.md",
    "references/shared-artifact-ownership.md",
    "references/technical-documentation.md",
    "references/validation-and-closure.md",
    "scripts/adapt_legacy_execution_records.py",
    "scripts/close_execution_state.py",
    "scripts/heal_execution_state.py",
    "scripts/magia_utils.py",
    "scripts/package_skill.py",
    "scripts/sync_execution_state.py",
    "scripts/update_template_lists.py",
    "scripts/validate_artifact.py",
    "scripts/validate_boundary.py",
    "scripts/validate_execution_state.py",
    "scripts/validate_planning_handoff_contract.py",
    "scripts/validate_repo_board.py",
    "scripts/validate_skill_package.py",
    "scripts/validate_contract_semantics.py",
    "scripts/run_test_suite.py",
    "scripts/write_artifact_scaffold.py",
    "scripts/write_execution_log.py",
}

REQUIRED_FUNCTIONS = {
    "scripts/adapt_legacy_execution_records.py": {"main"},
    "scripts/close_execution_state.py": {"_run_module_main", "main"},
    "scripts/heal_execution_state.py": {
        "parse_notes_records", "parse_validation_runs", "build_last_execution_block",
        "update_manifest_file", "collect_unhealable_errors", "main",
    },
    "scripts/sync_execution_state.py": {
        "update_tasks_file", "build_last_execution_block", "remove_last_execution",
        "update_manifest_file", "update_registry_file", "main",
    },
    "scripts/validate_execution_state.py": {
        "parse_tasks", "parse_notes", "parse_validation", "parse_manifest", "collect_errors", "main",
    },
    "scripts/validate_repo_board.py": {
        "iter_files", "validate_canonical_segments", "collect_artifact_placement_errors",
        "collect_package_shape_errors", "collect_placeholder_errors", "collect_errors", "main",
    },
    "scripts/validate_boundary.py": {"iter_skill_files", "collect_errors", "main"},
    "scripts/validate_skill_package.py": {
        "validate_shared_artifact_boundaries", "validate_eval_scenarios", "load_test_report",
        "validate_test_report", "validate_test_dependency", "validate_target", "validate_zip", "main",
    },
    "scripts/validate_contract_semantics.py": {"collect_errors", "main"},
    "scripts/run_test_suite.py": {"suite_manifest", "run_suite", "main"},
    "scripts/write_execution_log.py": {
        "load_task_title", "split_execution_log", "parse_execution_log", "build_entry", "write_execution_log", "main",
    },
}


def test_all_original_resources_remain_present():
    missing = sorted(path for path in ORIGINAL_RESOURCES if not (ROOT / path).is_file())
    assert missing == []


def test_core_script_capabilities_remain_addressable():
    for rel, expected in REQUIRED_FUNCTIONS.items():
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8-sig"), filename=rel)
        functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert expected <= functions, f"{rel} lost functions: {sorted(expected - functions)}"
