#!/usr/bin/env python3
"""Synchronize canonical MAGIA task, manifest, and registry execution state."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from board_contract import registry_for
from magia_utils import (
    BOARD_ROOT_TEMPLATE,
    load_yaml,
    parse_spec_id,
    print_errors,
    read_lines,
    replace_top_level_scalar,
    spec_package_path,
    spec_package_path_error,
    spec_registry_path,
    write_text,
    yaml_quote,
)

TASK_LINE_RE = re.compile(r"^(?P<prefix>\s*-\s*)\[(?P<mark>[ xX])\](?P<suffix>\s+(?P<task_id>task\d{3}):\s+.+)$")
VALID_SYNC_STATUSES = {"in_progress", "blocked", "done"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def update_tasks_file(tasks_path: Path, task_id: str, status: str) -> dict[str, bool]:
    original = tasks_path.read_text(encoding="utf-8-sig")
    lines = original.splitlines()
    mark = "x" if status == "done" else " "
    found = False
    task_states: dict[str, bool] = {}
    for index, line in enumerate(lines):
        match = TASK_LINE_RE.match(line)
        if not match:
            continue
        current_id = match.group("task_id")
        if current_id == task_id:
            lines[index] = f"{match.group('prefix')}[{mark}]{match.group('suffix')}"
            found = True
            task_states[current_id] = status == "done"
        else:
            task_states[current_id] = match.group("mark").lower() == "x"
    if not found:
        raise ValueError(f"`{task_id}` not found in {tasks_path}")
    content = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
    write_text(tasks_path, content)
    return task_states


def build_last_execution_block(task_id: str, execution_date: str, summary: str | None, files_changed: list[str]) -> list[str]:
    lines = [
        "last_execution:",
        f"  task_id: {yaml_quote(task_id)}",
        f"  date: {yaml_quote(execution_date)}",
    ]
    if summary:
        lines.append(f"  summary: {yaml_quote(summary)}")
    if files_changed:
        lines.append("  files_changed:")
        lines.extend(f"    - {yaml_quote(item)}" for item in files_changed)
    return lines


def remove_last_execution(lines: list[str]) -> list[str]:
    output: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].startswith("last_execution:"):
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                index += 1
            continue
        output.append(lines[index])
        index += 1
    while output and not output[-1].strip():
        output.pop()
    return output


def update_manifest_file(
    manifest_path: Path,
    *,
    spec_status: str,
    phase: str,
    task_id: str,
    execution_date: str,
    summary: str | None,
    files_changed: list[str],
) -> None:
    original = manifest_path.read_text(encoding="utf-8-sig")
    lines = original.splitlines()
    replace_top_level_scalar(lines, "status", spec_status)
    replace_top_level_scalar(lines, "phase", phase)
    lines = remove_last_execution(lines)
    lines.extend(["", *build_last_execution_block(task_id, execution_date, summary, files_changed)])
    write_text(manifest_path, "\n".join(lines) + "\n")


def update_registry_file(registry_path: Path, spec_status: str) -> None:
    original = registry_path.read_text(encoding="utf-8-sig")
    lines = original.splitlines()
    replace_top_level_scalar(lines, "status", spec_status)
    write_text(registry_path, "\n".join(lines) + ("\n" if original.endswith("\n") else ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize canonical MAGIA execution state from truthful task evidence.")
    parser.add_argument("board_root", help=f"Canonical board root under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Canonical spec ID: spec-YYYY-MM-DD-feature-key--ULID.")
    parser.add_argument("--task-id", required=True, help="Executed task ID in taskNNN form.")
    parser.add_argument("--status", required=True, choices=sorted(VALID_SYNC_STATUSES))
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--summary")
    parser.add_argument("--files-changed", nargs="*", default=[])
    args = parser.parse_args(argv)

    errors: list[str] = []
    if not DATE_RE.fullmatch(args.date):
        errors.append(f"date must use YYYY-MM-DD, got `{args.date}`")
    try:
        parse_spec_id(args.spec_id)
    except ValueError as exc:
        errors.append(str(exc))

    board_root = Path(args.board_root).resolve()
    package = spec_package_path(board_root, args.spec_id)
    path_error = spec_package_path_error(package)
    if path_error:
        errors.append(path_error)
    if errors:
        print_errors(errors)
        return 1

    tasks_path = package / "tasks.md"
    manifest_path = package / "manifest.yaml"
    registry_path = spec_registry_path(board_root, args.spec_id)
    try:
        for path in (tasks_path, manifest_path, registry_path):
            if not path.is_file():
                raise FileNotFoundError(f"missing required execution-state input: {path}")
        manifest = load_yaml(manifest_path)
        registry = registry_for(board_root, args.spec_id)
        for key in ("spec_id", "spec_uid", "cycle_id", "feature_key"):
            if manifest.get(key) != registry.get(key):
                raise ValueError(f"manifest `{key}` must match registry before execution-state sync")
        task_states = update_tasks_file(tasks_path, args.task_id, args.status)
        all_done = bool(task_states) and all(task_states.values())
        if args.status == "blocked":
            spec_status, phase = "blocked", "execute"
        elif all_done:
            spec_status, phase = "done", "done"
        else:
            spec_status, phase = "in_progress", "execute"
        update_manifest_file(
            manifest_path,
            spec_status=spec_status,
            phase=phase,
            task_id=args.task_id,
            execution_date=args.date,
            summary=args.summary,
            files_changed=args.files_changed,
        )
        update_registry_file(registry_path, spec_status)
    except (FileNotFoundError, ValueError) as exc:
        print_errors([str(exc)])
        return 1

    print(f"OK: synced {args.task_id} ({args.status}); spec status is {spec_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
