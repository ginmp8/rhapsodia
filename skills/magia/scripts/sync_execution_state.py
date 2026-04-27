#!/usr/bin/env python3
"""
Synchronize task completion state and manifest last_execution for a truthful MAGIA run.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, print_errors, read_lines, spec_package_path, spec_package_path_error, write_text, yaml_quote


TASK_LINE_RE = re.compile(r"^(?P<prefix>\s*-\s*)\[(?P<mark>[ xX])\](?P<suffix>\s+(?P<task_id>task\d{3}):\s+.+)$")
TOP_LEVEL_KEY_RE = re.compile(r"^[a-z_]+:")
VALID_SYNC_STATUSES = {"in_progress", "blocked", "done"}



def update_tasks_file(tasks_path: Path, task_id: str, status: str) -> None:
    original = tasks_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    mark = "x" if status == "done" else " "

    for index, line in enumerate(lines):
        match = TASK_LINE_RE.match(line)
        if not match or match.group("task_id") != task_id:
            continue
        lines[index] = f"{match.group('prefix')}[{mark}]{match.group('suffix')}"
        break
    else:
        raise ValueError(f"`{task_id}` not found in {tasks_path}")

    content = "\n".join(lines)
    if original.endswith("\n"):
        content += "\n"
    write_text(tasks_path, content)


def build_last_execution_block(
    task_id: str,
    execution_date: str,
    summary: str | None,
    files_changed: list[str],
) -> list[str]:
    lines = [
        "last_execution:",
        f"  task_id: {yaml_quote(task_id)}",
        f"  date: {yaml_quote(execution_date)}",
    ]
    if summary:
        lines.append(f"  summary: {yaml_quote(summary)}")
    if files_changed:
        lines.append("  files_changed:")
        for file_path in files_changed:
            lines.append(f"    - {yaml_quote(file_path)}")
    return lines


def update_manifest_file(
    manifest_path: Path,
    task_id: str,
    execution_date: str,
    summary: str | None,
    files_changed: list[str],
) -> None:
    original = manifest_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    output: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("last_execution:"):
            # skip the `last_execution:` line and any following indented or blank lines
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t") or lines[i] == ""):
                i += 1
            continue
        output.append(lines[i])
        i += 1

    while output and not output[-1].strip():
        output.pop()

    output.append("")
    output.extend(build_last_execution_block(task_id, execution_date, summary, files_changed))

    write_text(manifest_path, "\n".join(output) + "\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize tasks.md and manifest.yaml last_execution for a truthful MAGIA run."
    )
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected spec id in the form specNNN.")
    parser.add_argument("--task-id", required=True, help="Executed task id in the form taskNNN.")
    parser.add_argument(
        "--status",
        required=True,
        choices=sorted(VALID_SYNC_STATUSES),
        help="Truthful task execution status for this sync pass.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Execution date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument("--summary", help="Short truthful execution summary for manifest.yaml last_execution.")
    parser.add_argument(
        "--files-changed",
        nargs="*",
        default=[],
        help="Repository-relative POSIX paths changed by the executed task.",
    )
    args = parser.parse_args(argv)

    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        print_errors([canonical_error])
        return 1

    tasks_path = spec_package / "tasks.md"
    manifest_path = spec_package / "manifest.yaml"

    try:
        if not tasks_path.exists():
            raise FileNotFoundError(f"Missing tasks.md: {tasks_path}")
        if not manifest_path.exists():
            raise FileNotFoundError(f"Missing manifest.yaml: {manifest_path}")

        update_tasks_file(tasks_path, args.task_id, args.status)
        update_manifest_file(manifest_path, args.task_id, args.date, args.summary, args.files_changed)
    except (FileNotFoundError, ValueError) as exc:
        print_errors([str(exc)])
        return 1

    print(f"OK: synced {args.task_id} ({args.status})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
