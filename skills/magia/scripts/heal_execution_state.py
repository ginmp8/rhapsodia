#!/usr/bin/env python3
"""Repair narrowly-scoped MAGIA execution-state drift from existing evidence only."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, load_local_module, print_errors, read_lines, spec_package_path, spec_package_path_error


NOTES_TASK_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})\s+-\s+.+$")
NOTES_STATUS_RE = re.compile(r"^-\s+Status:\s*(?P<status>not_started|in_progress|blocked|done)\s*$")
NOTES_SUMMARY_RE = re.compile(r"^-\s+Summary:\s*(?P<summary>.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+(?P<field>Changes|Context Docs|Decisions|Follow-Ups|Blockers):\s*(?P<value>.*)$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(?P<value>.+?)\s*$")
VALIDATION_RUN_RE = re.compile(r"^##\s+Execution Run -\s+(?P<task_id>task\d{3})(?:\s+\((?P<date>\d{4}-\d{2}-\d{2})\))?")
HEALABLE_ERROR_PATTERNS = (
    re.compile(r"^notes\.md marks `task\d{3}` done but tasks\.md leaves the checkbox unchecked\.$"),
    re.compile(r"^notes\.md records executed tasks but manifest\.yaml omits last_execution\.$"),
)



def parse_notes_records(notes_path: Path) -> dict[str, dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    in_execution_log = False
    current_task: str | None = None
    current_field: str | None = None

    for line in read_lines(notes_path):
        if line.strip() == "## Execution Log":
            in_execution_log = True
            current_task = None
            current_field = None
            continue

        if in_execution_log and line.startswith("## ") and line.strip() != "## Execution Log":
            break

        if not in_execution_log:
            continue

        task_match = NOTES_TASK_RE.match(line)
        if task_match:
            current_task = task_match.group("task_id")
            current_field = None
            records.setdefault(current_task, {"status": None, "summary": None, "changes": []})
            continue

        if current_task is None:
            continue

        status_match = NOTES_STATUS_RE.match(line)
        if status_match:
            records[current_task]["status"] = status_match.group("status")
            current_field = None
            continue

        summary_match = NOTES_SUMMARY_RE.match(line)
        if summary_match:
            summary = summary_match.group("summary").strip()
            records[current_task]["summary"] = None if summary == "none" else summary
            current_field = None
            continue

        field_match = FIELD_RE.match(line)
        if field_match:
            current_field = field_match.group("field").lower().replace("-", "_").replace(" ", "_")
            if current_field == "changes":
                inline_value = field_match.group("value").strip()
                if inline_value and inline_value != "none":
                    records[current_task]["changes"] = [inline_value]
                else:
                    records[current_task]["changes"] = []
            continue

        if current_field == "changes":
            item_match = LIST_ITEM_RE.match(line)
            if item_match:
                value = item_match.group("value").strip()
                if value != "none":
                    changes = records[current_task].setdefault("changes", [])
                    assert isinstance(changes, list)
                    changes.append(value)
                continue

            if line.strip():
                current_field = None

    return records


def parse_validation_runs(validation_path: Path) -> tuple[dict[str, str | None], list[str]]:
    run_dates: dict[str, str | None] = {}
    run_order: list[str] = []

    for line in read_lines(validation_path):
        match = VALIDATION_RUN_RE.match(line)
        if not match:
            continue
        task_id = match.group("task_id")
        run_dates[task_id] = match.group("date")
        run_order.append(task_id)

    return run_dates, run_order


def build_last_execution_block(sync_module, task_id: str, execution_date: str | None, summary: str | None, files_changed: list[str]) -> list[str]:
    lines = [
        "last_execution:",
        f"  task_id: {sync_module.yaml_quote(task_id)}",
    ]
    if execution_date:
        lines.append(f"  date: {sync_module.yaml_quote(execution_date)}")
    if summary:
        lines.append(f"  summary: {sync_module.yaml_quote(summary)}")
    if files_changed:
        lines.append("  files_changed:")
        for file_path in files_changed:
            lines.append(f"    - {sync_module.yaml_quote(file_path)}")
    return lines


def update_manifest_file(sync_module, manifest_path: Path, task_id: str, execution_date: str | None, summary: str | None, files_changed: list[str]) -> None:
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    skipping = False

    for line in lines:
        if not skipping and line.startswith("last_execution:"):
            skipping = True
            continue

        if skipping:
            if line.startswith(" ") or line.startswith("\t") or not line:
                continue
            if sync_module.TOP_LEVEL_KEY_RE.match(line):
                skipping = False
            else:
                continue

        output.append(line)

    while output and not output[-1].strip():
        output.pop()

    output.append("")
    output.extend(build_last_execution_block(sync_module, task_id, execution_date, summary, files_changed))
    manifest_path.write_text("\n".join(output) + "\n", encoding="utf-8")


def collect_unhealable_errors(errors: list[str]) -> list[str]:
    return [e for e in errors if not any(p.match(e) for p in HEALABLE_ERROR_PATTERNS)]


def print_failed(errors: list[str]) -> None:
    unique_errors = list(dict.fromkeys(errors))
    for error in unique_errors:
        print(f"ERROR: {error}")
    print(f"FAILED: {len(unique_errors)} errors, 0 warnings")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Repair narrow MAGIA execution-state drift using only existing notes.md and validation.md evidence."
    )
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected spec id in the form `specNNN`.")
    args = parser.parse_args(argv)

    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        print_errors([canonical_error])
        return 1

    tasks_path = spec_package / "tasks.md"
    notes_path = spec_package / "notes.md"
    validation_path = spec_package / "validation.md"
    manifest_path = spec_package / "manifest.yaml"

    sync_module = _load_local_module("sync_execution_state.py")
    validate_module = _load_local_module("validate_execution_state.py")

    errors = validate_module.collect_errors(spec_package)
    unhealable_errors = collect_unhealable_errors(errors)
    if unhealable_errors:
        print_failed(unhealable_errors)
        return 1

    tasks = validate_module.parse_tasks(tasks_path)
    task_order = list(tasks.keys())
    notes_records = parse_notes_records(notes_path)
    validation_dates, validation_order = parse_validation_runs(validation_path)
    _, _, _, last_execution_task_id = validate_module.parse_manifest(manifest_path)

    if any(task_id not in tasks for task_id in notes_records):
        print_failed(["notes.md references a task missing from tasks.md"])
        return 1

    done_without_validation = [
        task_id
        for task_id, record in notes_records.items()
        if record.get("status") == "done" and task_id not in validation_dates
    ]
    if done_without_validation:
        print_failed(
            [
                f"{task_id} is marked done in notes.md but has no validation evidence"
                for task_id in done_without_validation
            ]
        )
        return 1

    done_candidates = [task_id for task_id in validation_order if notes_records.get(task_id, {}).get("status") == "done"]
    if not done_candidates:
        print("OK: no healable drift")
        return 0

    updated_tasks: list[str] = []
    for task_id in task_order:
        if task_id in done_candidates and not tasks[task_id]:
            sync_module.update_tasks_file(tasks_path, task_id, "done")
            updated_tasks.append(task_id)

    latest_task_id = done_candidates[-1]
    latest_record = notes_records[latest_task_id]
    summary = latest_record.get("summary")
    assert summary is None or isinstance(summary, str)
    changes = latest_record.get("changes", [])
    assert isinstance(changes, list)
    execution_date = validation_dates.get(latest_task_id)

    if last_execution_task_id != latest_task_id or updated_tasks:
        update_manifest_file(sync_module, manifest_path, latest_task_id, execution_date, summary, [str(change) for change in changes])

    remaining_errors = validate_module.collect_errors(spec_package)
    if remaining_errors:
        print_failed(remaining_errors)
        return 1

    checked = f"; checked {len(updated_tasks)} tasks" if updated_tasks else ""
    print(f"OK: healed execution state{checked}; last_execution {latest_task_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
