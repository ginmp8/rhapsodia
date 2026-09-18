#!/usr/bin/env python3
"""Validate MAGIA execution-state consistency across canonical planning and execution artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from board_contract import registry_for
from magia_utils import (
    BOARD_ROOT_TEMPLATE,
    dedupe_preserve_order,
    load_yaml,
    parse_spec_id,
    print_errors,
    read_lines,
    spec_package_path,
    spec_package_path_error,
)

TASK_LINE_RE = re.compile(r"^(?P<prefix>\s*-\s*)\[(?P<mark>[ xX])\](?P<suffix>\s+(?P<task_id>task\d{3}):\s+.+)$")
NOTES_TASK_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})\s+-\s+.+$")
NOTES_STATUS_RE = re.compile(r"^-\s+Status:\s*(?P<status>not_started|in_progress|blocked|done)\s*$")
VALIDATION_RUN_RE = re.compile(r"^##\s+Execution Run -\s+(?P<task_id>task\d{3})(?:\s|$|\()")


def parse_tasks(tasks_path: Path) -> dict[str, bool]:
    tasks: dict[str, bool] = {}
    for line in read_lines(tasks_path):
        match = TASK_LINE_RE.match(line)
        if match:
            tasks[match.group("task_id")] = match.group("mark").lower() == "x"
    return tasks


def parse_notes(notes_path: Path) -> dict[str, str | None]:
    notes_status: dict[str, str | None] = {}
    lines = read_lines(notes_path)
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Execution Log")
    except StopIteration:
        return notes_status

    current_task: str | None = None
    for line in lines[start + 1 :]:
        if line.startswith("## ") and line.strip() != "## Execution Log":
            break
        task_match = NOTES_TASK_RE.match(line)
        if task_match:
            current_task = task_match.group("task_id")
            notes_status.setdefault(current_task, None)
            continue
        if current_task is None:
            continue
        status_match = NOTES_STATUS_RE.match(line)
        if status_match:
            notes_status[current_task] = status_match.group("status")
    return notes_status


def parse_validation(validation_path: Path) -> set[str]:
    return {
        match.group("task_id")
        for line in read_lines(validation_path)
        if (match := VALIDATION_RUN_RE.match(line))
    }


def parse_manifest(manifest_path: Path) -> tuple[dict, str | None]:
    manifest = load_yaml(manifest_path)
    last_execution = manifest.get("last_execution")
    last_task = last_execution.get("task_id") if isinstance(last_execution, dict) else None
    return manifest, str(last_task) if last_task else None


def collect_errors(spec_package: Path) -> list[str]:
    tasks_path = spec_package / "tasks.md"
    notes_path = spec_package / "implementation-notes.md"
    validation_path = spec_package / "validation-evidence.md"
    legacy_notes = spec_package / "notes.md"
    legacy_validation = spec_package / "validation.md"
    manifest_path = spec_package / "manifest.yaml"

    required = (tasks_path, notes_path, validation_path, manifest_path)
    missing = [path for path in required if not path.exists()]
    if missing:
        legacy_markers: list[str] = []
        if legacy_notes.exists() and "## Execution Log" in legacy_notes.read_text(encoding="utf-8-sig"):
            legacy_markers.append(str(legacy_notes))
        if legacy_validation.exists() and "Execution" in legacy_validation.read_text(encoding="utf-8-sig"):
            legacy_markers.append(str(legacy_validation))
        errors = [f"Missing required execution-state file: {path}" for path in missing]
        if legacy_markers:
            errors.append(
                "Legacy execution content detected in planning-owned files; run "
                "scripts/adapt_legacy_execution_records.py before validation."
            )
        return errors

    tasks = parse_tasks(tasks_path)
    notes_status = parse_notes(notes_path)
    validation_runs = parse_validation(validation_path)
    manifest, last_execution_task_id = parse_manifest(manifest_path)
    board_root = spec_package.parent.parent
    spec_id = spec_package.name
    registry = registry_for(board_root, spec_id)

    errors: list[str] = []
    executed_statuses = {"in_progress", "blocked", "done"}

    if not tasks:
        errors.append("No task ids were found in tasks.md.")

    for key in ("spec_id", "cycle_id", "feature_key"):
        if manifest.get(key) != registry.get(key):
            errors.append(f"manifest.yaml `{key}` must match registry/<spec_id>.yaml.")
    if manifest.get("spec_id") != spec_id:
        errors.append("manifest.yaml spec_id must match the package directory name.")
    if manifest.get("status") != registry.get("status"):
        errors.append("manifest.yaml status must match registry/<spec_id>.yaml status.")

    for task_id in notes_status:
        if task_id not in tasks:
            errors.append(f"execution log references missing task id `{task_id}`.")

    if last_execution_task_id and last_execution_task_id not in tasks:
        errors.append(f"manifest.yaml last_execution references missing task id `{last_execution_task_id}`.")

    if last_execution_task_id:
        if last_execution_task_id not in notes_status:
            errors.append(
                f"manifest.yaml last_execution points to `{last_execution_task_id}` but implementation-notes.md "
                "has no Execution Log subsection for that task."
            )
        elif notes_status[last_execution_task_id] not in executed_statuses:
            errors.append(
                f"manifest.yaml last_execution points to `{last_execution_task_id}` but implementation-notes.md "
                f"records status `{notes_status[last_execution_task_id]}`."
            )
        if last_execution_task_id not in validation_runs:
            errors.append(
                f"manifest.yaml last_execution points to `{last_execution_task_id}` but validation-evidence.md "
                f"has no `Execution Run - {last_execution_task_id}` section."
            )

    executed_tasks = [task_id for task_id, status in notes_status.items() if status in executed_statuses]
    if executed_tasks and not last_execution_task_id:
        errors.append("implementation-notes.md records executed tasks but manifest.yaml omits last_execution.")

    for task_id, is_checked in tasks.items():
        status = notes_status.get(task_id)
        if is_checked and status != "done":
            errors.append(
                f"tasks.md marks `{task_id}` done but implementation-notes.md status is "
                f"`{status or 'missing'}` instead of done."
            )
        if not is_checked and status == "done":
            errors.append(f"implementation-notes.md marks `{task_id}` done but tasks.md leaves the checkbox unchecked.")
        if is_checked and task_id not in validation_runs:
            errors.append(
                f"tasks.md marks `{task_id}` done but validation-evidence.md has no "
                f"`Execution Run - {task_id}` section."
            )

    for task_id, status in notes_status.items():
        if status in executed_statuses and task_id not in validation_runs:
            errors.append(
                f"implementation-notes.md records `{task_id}` as `{status}` but validation-evidence.md has no "
                f"`Execution Run - {task_id}` section."
            )

    open_tasks = [task_id for task_id, is_checked in tasks.items() if not is_checked]
    manifest_status = manifest.get("status")
    manifest_phase = manifest.get("phase")
    registry_status = registry.get("status")

    if manifest_status == "done" and open_tasks:
        errors.append(f"manifest.yaml is done but tasks remain open: {', '.join(open_tasks)}")
    if manifest_phase == "done" and open_tasks:
        errors.append(f"manifest.yaml phase is done but tasks remain open: {', '.join(open_tasks)}")
    if registry_status == "done" and open_tasks:
        errors.append(f"registry/<spec_id>.yaml marks `{spec_id}` done but tasks remain open: {', '.join(open_tasks)}")
    if manifest_status == "done" and manifest_phase != "done":
        errors.append("manifest.yaml status done requires phase done.")
    if manifest_status in {"in_progress", "blocked"} and manifest_phase != "execute":
        errors.append(f"manifest.yaml status `{manifest_status}` requires phase execute.")

    return dedupe_preserve_order(errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate MAGIA execution-state consistency across tasks.md, implementation-notes.md, "
            "validation-evidence.md, manifest.yaml, and registry/<spec_id>.yaml."
        )
    )
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected canonical spec id.")
    args = parser.parse_args(argv)

    errors: list[str] = []
    try:
        parse_spec_id(args.spec_id)
    except ValueError as exc:
        errors.append(str(exc))
    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        errors.append(canonical_error)
    if not errors:
        try:
            errors.extend(collect_errors(spec_package))
        except (FileNotFoundError, ValueError) as exc:
            errors.append(str(exc))
    errors = dedupe_preserve_order(errors)
    if errors:
        print_errors(errors)
        return 1

    print("OK: execution-state records are aligned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
