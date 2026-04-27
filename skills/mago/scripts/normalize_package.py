#!/usr/bin/env python3
"""
Conservatively normalize MAGO package structure without inventing content.

Current scope:
- normalize notes.md execution-log subsections to canonical field labels
- normalize execution-log `Status` values to the canonical enum when the mapping is obvious
- fill missing non-status canonical fields with `none`

The script intentionally avoids rewriting task plans or inventing manifest values.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validate_package import resolve_package_targets


TASK_HEADER_RE = re.compile(r"^###\s+task\d{3}\b")
FIELD_RE = re.compile(
    r"^\s*(?:-\s+)?(?:\*\*)?(?P<label>Status|Summary|Changes|Context Docs|Decisions|Follow-Ups|Blockers)(?:\*\*)?:\s*(?P<rest>.*)$",
    re.IGNORECASE,
)
CANONICAL_FIELDS = [
    "Status",
    "Summary",
    "Changes",
    "Context Docs",
    "Decisions",
    "Follow-Ups",
    "Blockers",
]

# Map lowercased labels to canonical labels for fast lookup
_LOWER_TO_CANONICAL = {f.lower(): f for f in CANONICAL_FIELDS}

STATUS_MAP = {
    "not started": "not_started",
    "not_started": "not_started",
    "in progress": "in_progress",
    "in_progress": "in_progress",
    "blocked": "blocked",
    "done": "done",
    "complete": "done",
    "completed": "done",
    "executed": "done",
}


def canonical_label(label: str) -> str:
    key = label.strip().lower()
    try:
        return _LOWER_TO_CANONICAL[key]
    except KeyError:
        raise ValueError(f"Unknown field label: {label}")


def trim_blank_lines(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def normalize_status(lines: list[str]) -> str | None:
    for line in trim_blank_lines(lines):
        text = line.strip()
        if not text:
            continue
        return STATUS_MAP.get(text.lower(), text)
    return None


def render_field(field: str, lines: list[str]) -> list[str] | None:
    normalized_lines = trim_blank_lines(lines)
    if field == "Status":
        status = normalize_status(normalized_lines)
        if status is None:
            return None
        return [f"- Status: {status}"]

    if not normalized_lines:
        return [f"- {field}: none"]

    if len(normalized_lines) == 1:
        return [f"- {field}: {normalized_lines[0].strip()}"]

    rendered = [f"- {field}:"]
    for line in normalized_lines:
        rendered.append(f"  {line}" if line else "")
    return rendered


def normalize_task_block(header: str, body_lines: list[str]) -> tuple[list[str], bool]:
    current_field: str | None = None
    current_lines: list[str] = []
    fields: dict[str, list[str]] = {}
    other_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_field, current_lines
        if current_field is not None:
            fields[current_field] = current_lines[:]
        current_field = None
        current_lines = []

    for line in body_lines:
        field_match = FIELD_RE.match(line)
        if field_match:
            flush_current()
            current_field = canonical_label(field_match.group("label"))
            rest = field_match.group("rest")
            current_lines = [rest] if rest else []
            continue

        if current_field is not None:
            current_lines.append(line)
        else:
            other_lines.append(line)

    flush_current()

    if not fields:
        return [header, *body_lines], False

    status_field = render_field("Status", fields.get("Status", []))
    if status_field is None:
        return [header, *body_lines], False

    normalized_block: list[str] = [header, ""]
    normalized_block.extend(status_field)

    for field in CANONICAL_FIELDS[1:]:
        normalized_block.extend(render_field(field, fields.get(field, [])) or [])

    leftover = trim_blank_lines(other_lines)
    if leftover:
        normalized_block.append("")
        normalized_block.extend(leftover)

    original_block = [header, *body_lines]
    return normalized_block, normalized_block != original_block


def normalize_notes_text(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    output: list[str] = []
    changed = False
    in_execution_log = False
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("## "):
            in_execution_log = line.strip() == "## Execution Log"
            output.append(line)
            i += 1
            continue

        if in_execution_log and TASK_HEADER_RE.match(line):
            header = line
            body: list[str] = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith("## ") or TASK_HEADER_RE.match(next_line):
                    break
                body.append(next_line)
                i += 1

            normalized_block, block_changed = normalize_task_block(header, body)
            output.extend(normalized_block)
            changed = changed or block_changed
            continue

        output.append(line)
        i += 1

    normalized_text = "\n".join(output)
    if text.endswith("\n"):
        normalized_text += "\n"
    return normalized_text, changed


def normalize_package(package_path: Path, check_only: bool) -> bool:
    notes_path = package_path / "notes.md"
    if not notes_path.exists():
        return False

    original = notes_path.read_text(encoding="utf-8")
    normalized, changed = normalize_notes_text(original)
    if not changed:
        return False

    if check_only:
        print(f"ERROR: {notes_path}: would be normalized")
        return True

    notes_path.write_text(normalized, encoding="utf-8")
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Conservatively normalize MAGO package structure without inventing content."
    )
    parser.add_argument("board_root", help="Path to the active BOARD_ROOT under docs/boards/<board_id>/<cycle_version>/.")
    parser.add_argument(
        "--spec-id",
        action="append",
        default=[],
        help="Repeat to normalize one or more selected spec packages under BOARD_ROOT. Omit to normalize every package under BOARD_ROOT/specs/.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report packages that would be normalized without writing changes.",
    )
    args = parser.parse_args(argv)

    package_paths = resolve_package_targets(args.board_root, args.spec_id)
    changed_count = 0
    error_count = 0
    for package_path in package_paths:
        if package_path.exists():
            if normalize_package(package_path, args.check):
                changed_count += 1
        else:
            print(f"ERROR: {package_path}: target does not exist")
            error_count += 1

    if args.check and changed_count:
        print(f"FAILED: {changed_count + error_count} errors, 0 warnings")
        return 1
    if error_count:
        print(f"FAILED: {error_count} errors, 0 warnings")
        return 1
    if args.check:
        print(f"OK: validated {len(package_paths)} package(s)")
    else:
        print(f"OK: normalized {changed_count} package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
