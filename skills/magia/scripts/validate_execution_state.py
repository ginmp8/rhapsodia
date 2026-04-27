#!/usr/bin/env python3
"""Validate cross-artifact execution-state consistency for a MAGIA spec package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, dedupe_preserve_order, print_errors, read_lines, spec_package_path, spec_package_path_error


TASK_LINE_RE = re.compile(r"^(?P<prefix>\s*-\s*)\[(?P<mark>[ xX])\](?P<suffix>\s+(?P<task_id>task\d{3}):\s+.+)$")
NOTES_TASK_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})\s+-\s+.+$")
NOTES_STATUS_RE = re.compile(r"^-\s+Status:\s*(?P<status>not_started|in_progress|blocked|done)\s*$")
VALIDATION_RUN_RE = re.compile(r"^##\s+Execution Run -\s+(?P<task_id>task\d{3})(?:\s|$|\()")
MANIFEST_TASK_ID_RE = re.compile(r'^\s*task_id:\s*["\']?(?P<task_id>task\d{3})["\']?\s*$')
MANIFEST_STATUS_RE = re.compile(r'^status:\s*["\']?(?P<value>[a-z_]+)["\']?\s*$')
MANIFEST_PHASE_RE = re.compile(r'^phase:\s*["\']?(?P<value>[a-z_]+)["\']?\s*$')
MANIFEST_SPEC_ID_RE = re.compile(r'^spec_id:\s*["\']?(?P<value>spec\d{3})["\']?\s*$')
CATALOG_ENTRY_START_RE = re.compile(r"^\s*-\s+order:\s+.+$")
CATALOG_SPEC_ID_RE = re.compile(r'^\s*spec_id:\s*["\']?(?P<value>spec\d{3})["\']?\s*$')
CATALOG_STATUS_RE = re.compile(r'^\s*status:\s*["\']?(?P<value>[a-z_]+)["\']?\s*$')



def parse_tasks(tasks_path: Path) -> dict[str, bool]:
    tasks: dict[str, bool] = {}
    for line in read_lines(tasks_path):
        match = TASK_LINE_RE.match(line)
        if not match:
            continue
        task_id = match.group("task_id")
        tasks[task_id] = match.group("mark").lower() == "x"
    return tasks


def parse_notes(notes_path: Path) -> dict[str, str | None]:
    notes_status: dict[str, str | None] = {}
    lines = read_lines(notes_path)
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Execution Log")
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
    task_ids: set[str] = set()
    for line in read_lines(validation_path):
        match = VALIDATION_RUN_RE.match(line)
        if match:
            task_ids.add(match.group("task_id"))
    return task_ids


def parse_manifest(manifest_path: Path) -> tuple[str | None, str | None, str | None, str | None]:
    lines = read_lines(manifest_path)
    spec_id: str | None = None
    status: str | None = None
    phase: str | None = None
    last_execution_task_id: str | None = None

    for line in lines:
        if spec_id is None:
            spec_match = MANIFEST_SPEC_ID_RE.match(line)
            if spec_match:
                spec_id = spec_match.group("value")
                continue

        if status is None:
            status_match = MANIFEST_STATUS_RE.match(line)
            if status_match:
                status = status_match.group("value")
                continue

        if phase is None:
            phase_match = MANIFEST_PHASE_RE.match(line)
            if phase_match:
                phase = phase_match.group("value")
                continue

    # parse last_execution block if present
    for i, line in enumerate(lines):
        if line.strip() == "last_execution:":
            for sub in lines[i + 1 :]:
                if not sub.startswith(" ") and sub.strip():
                    break
                task_match = MANIFEST_TASK_ID_RE.match(sub.strip())
                if task_match:
                    last_execution_task_id = task_match.group("task_id")
            break

    return spec_id, status, phase, last_execution_task_id


def parse_catalog_status(catalog_path: Path, spec_id: str | None) -> str | None:
    if spec_id is None or not catalog_path.exists():
        return None

    current_spec_id: str | None = None
    current_status: str | None = None

    for line in read_lines(catalog_path):
        if CATALOG_ENTRY_START_RE.match(line):
            if current_spec_id == spec_id:
                return current_status
            current_spec_id = None
            current_status = None
            continue

        spec_match = CATALOG_SPEC_ID_RE.match(line)
        if spec_match:
            current_spec_id = spec_match.group("value")
            continue

        status_match = CATALOG_STATUS_RE.match(line)
        if status_match:
            current_status = status_match.group("value")
            continue

    if current_spec_id == spec_id:
        return current_status
    return None


def collect_errors(spec_package: Path) -> list[str]:
    tasks_path = spec_package / "tasks.md"
    notes_path = spec_package / "notes.md"
    validation_path = spec_package / "validation.md"
    manifest_path = spec_package / "manifest.yaml"
    catalog_path = spec_package.parent.parent / "spec-catalog.yaml"

    for path in (tasks_path, notes_path, validation_path, manifest_path):
        if not path.exists():
            return [f"Missing required file: {path}"]

    tasks = parse_tasks(tasks_path)
    notes_status = parse_notes(notes_path)
    validation_runs = parse_validation(validation_path)
    spec_id, manifest_status, manifest_phase, last_execution_task_id = parse_manifest(manifest_path)
    catalog_status = parse_catalog_status(catalog_path, spec_id)

    errors: list[str] = []
    executed_statuses = {"in_progress", "blocked", "done"}

    if not tasks:
        errors.append("No task ids were found in tasks.md.")

    for task_id in notes_status:
        if task_id not in tasks:
            errors.append(f"notes.md references missing task id `{task_id}`.")

    if last_execution_task_id and last_execution_task_id not in tasks:
        errors.append(f"manifest.yaml last_execution references missing task id `{last_execution_task_id}`.")

    if last_execution_task_id:
        if last_execution_task_id not in notes_status:
            errors.append(
                f"manifest.yaml last_execution points to `{last_execution_task_id}` but notes.md has no Execution Log subsection for that task."
            )
        elif notes_status[last_execution_task_id] not in executed_statuses:
            errors.append(
                f"manifest.yaml last_execution points to `{last_execution_task_id}` but notes.md records status `{notes_status[last_execution_task_id]}`."
            )
        if last_execution_task_id not in validation_runs:
            errors.append(
                f"manifest.yaml last_execution points to `{last_execution_task_id}` but validation.md has no `Execution Run - {last_execution_task_id}` section."
            )

    executed_tasks = [task_id for task_id, status in notes_status.items() if status in executed_statuses]
    if executed_tasks and not last_execution_task_id:
        errors.append("notes.md records executed tasks but manifest.yaml omits last_execution.")

    for task_id, is_checked in tasks.items():
        status = notes_status.get(task_id)
        if is_checked and status != "done":
            errors.append(
                f"tasks.md marks `{task_id}` done but notes.md status is `{status or 'missing'}` instead of `done`."
            )
        if not is_checked and status == "done":
            errors.append(f"notes.md marks `{task_id}` done but tasks.md leaves the checkbox unchecked.")
        if is_checked and task_id not in validation_runs:
            errors.append(f"tasks.md marks `{task_id}` done but validation.md has no `Execution Run - {task_id}` section.")

    for task_id, status in notes_status.items():
        if status in executed_statuses and task_id not in validation_runs:
            errors.append(f"notes.md records `{task_id}` as `{status}` but validation.md has no `Execution Run - {task_id}` section.")

    open_tasks = [task_id for task_id, is_checked in tasks.items() if not is_checked]
    if manifest_status == "done" and open_tasks:
        errors.append(f"manifest.yaml is `done` but tasks remain open: {', '.join(open_tasks)}")
    if manifest_phase == "done" and open_tasks:
        errors.append(f"manifest.yaml phase is `done` but tasks remain open: {', '.join(open_tasks)}")
    if catalog_status == "done" and open_tasks:
        errors.append(f"spec-catalog.yaml marks `{spec_id}` done but tasks remain open: {', '.join(open_tasks)}")

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate MAGIA execution-state consistency across tasks.md, notes.md, validation.md, manifest.yaml, and spec-catalog.yaml."
    )
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected spec id in the form `specNNN`.")
    args = parser.parse_args(argv)

    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    errors = []
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        errors.append(canonical_error)
    errors.extend(collect_errors(spec_package))
    errors = dedupe_preserve_order(errors)
    if errors:
        print_errors(errors)
        return 1

    print("OK: execution-state records are aligned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
