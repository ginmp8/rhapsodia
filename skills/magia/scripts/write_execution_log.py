#!/usr/bin/env python3
"""Canonical MAGIA writer for `notes.md` Execution Log entries."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, print_errors, read_lines, spec_package_path, spec_package_path_error, write_text


TASK_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(?P<task_id>task\d{3}):\s+(?P<title>.+?)\s*$")
TASK_HEADING_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})\s+-\s+.+$")
VALID_STATUSES = ("not_started", "in_progress", "blocked", "done")



def trim_blank_lines(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)

    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1

    return lines[start:end]


def join_sections(sections: list[list[str]]) -> list[str]:
    output: list[str] = []

    for section in sections:
        block = trim_blank_lines(section)
        if not block:
            continue
        if output:
            output.append("")
        output.extend(block)

    return output


def load_task_title(tasks_path: Path, task_id: str) -> str:
    for line in read_lines(tasks_path):
        match = TASK_LINE_RE.match(line)
        if match and match.group("task_id") == task_id:
            return match.group("title")
    raise ValueError(f"`{task_id}` not found in {tasks_path}")


def split_execution_log(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    start_index: int | None = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        if line.strip() == "## Execution Log":
            start_index = index
            break

    if start_index is None:
        return lines, [], []

    for index in range(start_index + 1, len(lines)):
        if lines[index].startswith("## ") and lines[index].strip() != "## Execution Log":
            end_index = index
            break

    return lines[:start_index], lines[start_index + 1 : end_index], lines[end_index:]


def parse_execution_log(log_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    preamble: list[str] = []
    entries: list[list[str]] = []
    current_entry: list[str] | None = None

    for line in log_lines:
        if TASK_HEADING_RE.match(line):
            if current_entry is not None:
                entries.append(current_entry)
            current_entry = [line]
            continue

        if current_entry is not None:
            current_entry.append(line)
        else:
            preamble.append(line)

    if current_entry is not None:
        entries.append(current_entry)

    return preamble, entries


def entry_task_id(entry: list[str]) -> str | None:
    if not entry:
        return None
    match = TASK_HEADING_RE.match(entry[0])
    return match.group("task_id") if match else None


def render_list_field(label: str, values: list[str]) -> list[str]:
    if not values:
        return [f"- {label}: none"]
    return [f"- {label}:", *(f"  - {value}" for value in values)]


def build_entry(
    task_id: str,
    title: str,
    status: str,
    summary: str,
    changes: list[str],
    context_docs: list[str],
    decisions: list[str],
    follow_ups: list[str],
    blockers: list[str],
) -> list[str]:
    lines = [
        f"### {task_id} - {title}",
        "",
        f"- Status: {status}",
        f"- Summary: {summary}",
    ]
    lines.extend(render_list_field("Changes", changes))
    lines.extend(render_list_field("Context Docs", context_docs))
    lines.extend(render_list_field("Decisions", decisions))
    lines.extend(render_list_field("Follow-Ups", follow_ups))
    lines.extend(render_list_field("Blockers", blockers))
    return lines


def write_execution_log(
    spec_package: Path,
    task_id: str,
    status: str,
    summary: str,
    changes: list[str],
    context_docs: list[str],
    decisions: list[str],
    follow_ups: list[str],
    blockers: list[str],
) -> Path:
    notes_path = spec_package / "notes.md"
    tasks_path = spec_package / "tasks.md"

    if not notes_path.exists():
        raise FileNotFoundError(f"Missing `notes.md`: {notes_path}")
    if not tasks_path.exists():
        raise FileNotFoundError(f"Missing `tasks.md`: {tasks_path}")
    if not summary.strip():
        raise ValueError("`--summary` must not be empty.")

    title = load_task_title(tasks_path, task_id)
    lines = read_lines(notes_path)
    before_log, log_lines, after_log = split_execution_log(lines)
    preamble, entries = parse_execution_log(log_lines)

    retained_entries: list[list[str]] = []
    for entry in entries:
        if entry_task_id(entry) == task_id:
            continue
        trimmed = trim_blank_lines(entry)
        if trimmed:
            retained_entries.append(trimmed)

    entry = build_entry(
        task_id=task_id,
        title=title,
        status=status,
        summary=summary.strip(),
        changes=[value.strip() for value in changes if value.strip()],
        context_docs=[value.strip() for value in context_docs if value.strip()],
        decisions=[value.strip() for value in decisions if value.strip()],
        follow_ups=[value.strip() for value in follow_ups if value.strip()],
        blockers=[value.strip() for value in blockers if value.strip()],
    )

    output = join_sections([before_log, after_log])
    if output:
        output.append("")
    output.append("## Execution Log")

    log_content = join_sections([trim_blank_lines(preamble), *retained_entries, entry])
    if log_content:
        output.append("")
        output.extend(log_content)

    write_text(notes_path, "\n".join(output) + "\n")
    return notes_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Append or refresh one canonical MAGIA `notes.md` Execution Log subsection at EOF."
    )
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected spec id in the form `specNNN`.")
    parser.add_argument("--task-id", required=True, help="Executed task id in the form `taskNNN`.")
    parser.add_argument(
        "--status",
        required=True,
        choices=VALID_STATUSES,
        help="Truthful execution status for the task subsection.",
    )
    parser.add_argument("--summary", required=True, help="Short truthful summary for the task execution log entry.")
    parser.add_argument(
        "--change",
        action="append",
        default=[],
        help="Repeat for each `Changes` list item. Omit to write `none`.",
    )
    parser.add_argument(
        "--context-doc",
        action="append",
        default=[],
        help="Repeat for each `Context Docs` list item. Omit to write `none`.",
    )
    parser.add_argument(
        "--decision",
        action="append",
        default=[],
        help="Repeat for each `Decisions` list item. Omit to write `none`.",
    )
    parser.add_argument(
        "--follow-up",
        action="append",
        default=[],
        help="Repeat for each `Follow-Ups` list item. Omit to write `none`.",
    )
    parser.add_argument(
        "--blocker",
        action="append",
        default=[],
        help="Repeat for each `Blockers` list item. Omit to write `none`.",
    )
    args = parser.parse_args(argv)

    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        print_errors([canonical_error])
        return 1

    try:
        write_execution_log(
            spec_package=spec_package,
            task_id=args.task_id,
            status=args.status,
            summary=args.summary,
            changes=args.change,
            context_docs=args.context_doc,
            decisions=args.decision,
            follow_ups=args.follow_up,
            blockers=args.blocker,
        )
    except (FileNotFoundError, ValueError) as exc:
        print_errors([str(exc)])
        return 1

    print(f"OK: updated notes for {args.task_id} ({args.status})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
