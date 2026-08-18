#!/usr/bin/env python3
"""Produce a read-only, non-authoritative MAGIA execution and recovery view."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from magia_utils import (
    board_root_path_error,
    load_yaml,
    parse_spec_id,
    spec_package_path,
    spec_package_path_error,
    spec_registry_path,
)
from sync_execution_state import (
    LOCK_FILE_NAME,
    TRANSACTION_DIR_NAME,
    _load_transaction_journal,
    _lock_owner_state,
)
from validate_execution_state import collect_errors, parse_notes, parse_tasks, parse_validation_details


def _safe_yaml(path: Path) -> tuple[dict[str, Any], str | None]:
    if path.is_symlink() or not path.is_file():
        return {}, f"missing or unsafe file: {path.name}"
    try:
        return load_yaml(path), None
    except (OSError, RuntimeError, ValueError) as exc:
        return {}, f"invalid {path.name}: {exc}"


def _task_rows(package: Path) -> list[dict[str, Any]]:
    tasks_path = package / "tasks.md"
    notes_path = package / "implementation-notes.md"
    evidence_path = package / "validation-evidence.md"
    tasks = parse_tasks(tasks_path) if tasks_path.is_file() and not tasks_path.is_symlink() else {}
    notes = parse_notes(notes_path) if notes_path.is_file() and not notes_path.is_symlink() else {}
    runs = (
        parse_validation_details(evidence_path)
        if evidence_path.is_file() and not evidence_path.is_symlink()
        else {}
    )
    rows: list[dict[str, Any]] = []
    for task_id in sorted(tasks):
        run = runs.get(task_id, {})
        rows.append(
            {
                "task_id": task_id,
                "checked": tasks[task_id],
                "execution_status": notes.get(task_id) or "not_started",
                "executed_check_count": len(run.get("executed_checks", [])),
                "failed_check_count": len(run.get("failed_checks", [])),
                "not_run_check_count": len(run.get("not_run_checks", [])),
                "has_traceability": bool(run.get("traceability")),
            }
        )
    return rows


def _recovery_view(package: Path) -> dict[str, Any]:
    lock_path = package / LOCK_FILE_NAME
    journal_dir = package / TRANSACTION_DIR_NAME
    result: dict[str, Any] = {
        "lock": "absent",
        "journal": "absent",
        "journal_targets": [],
        "recovery_action": "none",
        "safe_to_mutate": True,
    }

    if lock_path.exists():
        if lock_path.is_symlink() or not lock_path.is_file():
            result.update(lock="unsafe", recovery_action="manual_inspection", safe_to_mutate=False)
        else:
            owner = _lock_owner_state(lock_path)
            if owner is True:
                result.update(lock="live_owner", recovery_action="wait_for_owner", safe_to_mutate=False)
            elif owner is False:
                result.update(lock="dead_owner", recovery_action="run_recovery", safe_to_mutate=False)
            else:
                result.update(lock="invalid_metadata", recovery_action="manual_inspection", safe_to_mutate=False)

    if journal_dir.exists():
        result["safe_to_mutate"] = False
        if journal_dir.is_symlink() or not journal_dir.is_dir():
            result.update(journal="unsafe", recovery_action="manual_inspection")
        else:
            try:
                state, entries = _load_transaction_journal(package, journal_dir)
                board_root = package.parent.parent.resolve()
                result["journal"] = state
                result["journal_targets"] = [target.relative_to(board_root).as_posix() for target, _ in entries]
                if result["lock"] != "live_owner":
                    result["recovery_action"] = "run_recovery"
            except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
                result.update(journal="invalid", recovery_action="manual_inspection")
                result["journal_error"] = str(exc)

    if result["lock"] == "dead_owner" and result["journal"] == "absent":
        result["recovery_action"] = "run_recovery"
    return result


def summarize(board_root: Path, spec_id: str) -> dict[str, Any]:
    root = board_root.resolve()
    root_error = board_root_path_error(root)
    if root_error:
        raise ValueError(root_error)
    parse_spec_id(spec_id)
    package = spec_package_path(root, spec_id).resolve()
    package_error = spec_package_path_error(package)
    if package_error:
        raise ValueError(package_error)
    if not package.is_dir() or package.is_symlink():
        raise ValueError(f"spec package is missing or unsafe: {package}")

    manifest, manifest_error = _safe_yaml(package / "manifest.yaml")
    registry, registry_error = _safe_yaml(spec_registry_path(root, spec_id))
    state_errors = collect_errors(package)
    recovery = _recovery_view(package)
    tasks = _task_rows(package)
    blockers = [error for error in (manifest_error, registry_error) if error] + state_errors

    if recovery["recovery_action"] == "wait_for_owner":
        next_action = "Wait for the live lock owner; do not mutate execution state."
    elif recovery["recovery_action"] == "run_recovery":
        next_action = "Run the existing execution-state recovery path, then repeat validation."
    elif recovery["recovery_action"] == "manual_inspection":
        next_action = "Stop mutation and inspect unsafe lock or journal evidence manually."
    elif blockers:
        next_action = "Resolve execution-state validation errors before closure or state mutation."
    else:
        next_action = "Continue the selected bounded task and run its planned proving check."

    return {
        "projection": "non_authoritative",
        "board_root": str(root),
        "spec_id": spec_id,
        "state": {
            "manifest_status": manifest.get("status", "unknown"),
            "manifest_phase": manifest.get("phase", "unknown"),
            "registry_status": registry.get("status", "unknown"),
            "last_execution": manifest.get("last_execution"),
        },
        "tasks": tasks,
        "validation_error_count": len(state_errors),
        "validation_errors": state_errors,
        "recovery": recovery,
        "blockers": blockers,
        "next_safe_action": next_action,
    }


def _markdown(payload: dict[str, Any]) -> str:
    state = payload["state"]
    recovery = payload["recovery"]
    lines = [
        "# MAGIA Execution View",
        "",
        "> Non-authoritative read-only projection. Canonical artifacts and command evidence remain authoritative.",
        "",
        f"- Spec: `{payload['spec_id']}`",
        f"- Status: `{state['manifest_status']}`",
        f"- Phase: `{state['manifest_phase']}`",
        f"- Registry status: `{state['registry_status']}`",
        f"- Lock: `{recovery['lock']}`",
        f"- Journal: `{recovery['journal']}`",
        f"- Validation errors: `{payload['validation_error_count']}`",
        f"- Next safe action: {payload['next_safe_action']}",
        "",
        "## Tasks",
        "",
        "| Task | Checked | Execution | Passed/recorded checks | Failed | Not run | Traceability |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for task in payload["tasks"]:
        lines.append(
            f"| `{task['task_id']}` | {str(task['checked']).lower()} | `{task['execution_status']}` | "
            f"{task['executed_check_count']} | {task['failed_check_count']} | {task['not_run_check_count']} | "
            f"{str(task['has_traceability']).lower()} |"
        )
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {item}" for item in payload["blockers"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board_root", type=Path)
    parser.add_argument("--spec-id", required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = summarize(args.board_root, args.spec_id)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n" if args.format == "json" else _markdown(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8", newline="\n")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
