#!/usr/bin/env python3
"""Best-effort conversion of legacy execution records into current MAGIA artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, print_errors, read_lines, spec_package_path, spec_package_path_error

LEGACY_TASK_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})(?:\s+-\s*(?P<title>.*))?$")
STATUS_RE = re.compile(r"^[-*]?\s*(?:Status|status):\s*(?P<status>not[_ ]started|in[_ ]progress|blocked|done|complete|completed|executed)\s*$")
SUMMARY_RE = re.compile(r"^[-*]?\s*(?:Summary|summary):\s*(?P<summary>.+?)\s*$")
VALIDATION_RUN_RE = re.compile(r"^##\s+(?P<title>.*?(?P<task_id>task\d{3}).*)$")
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


def extract_legacy_execution_log(notes_path: Path) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    if not notes_path.exists():
        return records
    lines = read_lines(notes_path)
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Execution Log")
    except StopIteration:
        return records

    current: str | None = None
    for line in lines[start + 1:]:
        if line.startswith("## ") and line.strip() != "## Execution Log":
            break
        task_match = LEGACY_TASK_RE.match(line.strip())
        if task_match:
            current = task_match.group("task_id")
            records.setdefault(current, {"title": task_match.group("title") or "adapted legacy execution", "status": "unknown", "summary": "adapted from legacy notes.md"})
            continue
        if current is None:
            continue
        status_match = STATUS_RE.match(line.strip())
        if status_match:
            records[current]["status"] = STATUS_MAP.get(status_match.group("status").replace("_", " ").lower(), status_match.group("status"))
            continue
        summary_match = SUMMARY_RE.match(line.strip())
        if summary_match:
            records[current]["summary"] = summary_match.group("summary")
    return records


def extract_legacy_validation_runs(validation_path: Path) -> set[str]:
    task_ids: set[str] = set()
    if not validation_path.exists():
        return task_ids
    for line in read_lines(validation_path):
        match = VALIDATION_RUN_RE.match(line.strip())
        if match:
            task_ids.add(match.group("task_id"))
    return task_ids


def write_implementation_notes(path: Path, spec_id: str, records: dict[str, dict[str, str]]) -> None:
    lines = [
        "# Implementation Notes",
        "",
        "## Scope",
        "",
        f"- Spec or task: `{spec_id}`",
        "- Repository area: `unknown`",
        "- Date: `unknown`",
        "- Implementer: `unknown`",
        "",
        "## Summary",
        "",
        "Best-effort adaptation from legacy execution content. Treat unknown fields as unresolved until confirmed by current repository evidence.",
        "",
        "## Files and Modules Changed",
        "",
        "- `unknown`",
        "",
        "## Actual Flow",
        "",
        "unknown",
        "",
        "## Deviations from Mago Plan",
        "",
        "- `unknown`",
        "",
        "## Constraints and Limitations",
        "",
        "- legacy source was converted best effort; verify before relying on completion state",
        "",
        "## Execution Log",
    ]
    if records:
        for task_id, data in sorted(records.items()):
            legacy_status = data.get("status") or "unknown"
            status = "not_started"
            lines.extend([
                "",
                f"### {task_id} - {data.get('title') or 'adapted legacy execution'}",
                "",
                f"- Status: {status}",
                f"- Summary: legacy status `{legacy_status}`; {data.get('summary') or 'adapted from legacy notes.md'}",
                "- Changes: unknown",
                "- Context Docs: notes.md",
                "- Decisions: unknown",
                "- Follow-Ups: verify adapted legacy execution evidence before closure",
                "- Blockers: current validation evidence required before execution state can change",
            ])
    else:
        lines.extend(["", "No legacy execution log entries were found."])
    lines.extend([
        "",
        "## Validation",
        "",
        "- Executed: `unknown`",
        "- Not run: `unknown`",
        "- Static evidence: legacy notes.md adaptation only",
        "",
        "## Residual Risks",
        "",
        "- adapted content must be verified against current repository evidence before closing execution state",
        "",
        "## Handoff",
        "",
        "- Mago: review if adapted evidence conflicts with current planning artifacts",
        "- Magnomo: none",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_validation_evidence(path: Path, spec_id: str, records: dict[str, dict[str, str]], validation_runs: set[str]) -> None:
    lines = [
        "# Validation Evidence",
        "",
        "## Scope",
        "",
        f"- Spec or task: `{spec_id}`",
        "- Change under validation: legacy execution-record adaptation",
    ]
    task_ids = sorted(set(records) | validation_runs)
    if not task_ids:
        task_ids = ["taskNNN"]
    for task_id in task_ids:
        result = "unknown"
        evidence = "legacy validation.md section detected" if task_id in validation_runs else "no legacy validation run detected"
        lines.extend([
            "",
            f"## Execution Run - {task_id}",
            "",
            "### Executed Checks",
            "",
            "| Check | Command or method | Result | Evidence |",
            "|---|---|---|---|",
            f"| legacy adaptation | legacy validation.md review | {result} | {evidence} |",
            "",
            "### Failed Checks",
            "",
            "- `unknown`",
            "",
            "### Not-Run Checks",
            "",
            "| Check | Reason not run | Risk |",
            "|---|---|---|",
            "| current validation rerun | adapt mode does not execute repository checks | adapted state may be stale |",
            "",
            "### Static Evidence",
            "",
            "- legacy files were converted best effort into current MAGIA-owned artifacts",
            "",
            "### Residual Risk",
            "",
            "- verify against current repository evidence before marking completion",
            "",
            "### Recommended Follow-Up",
            "",
            "- run normal RALPH validation/closure after adaptation",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Adapt legacy notes.md/validation.md execution content into current MAGIA-owned artifacts.")
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected spec id in the form specNNN.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing current MAGIA-owned artifacts.")
    args = parser.parse_args(argv)

    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        print_errors([canonical_error])
        return 1

    notes_path = spec_package / "notes.md"
    validation_path = spec_package / "validation.md"
    implementation_notes_path = spec_package / "implementation-notes.md"
    validation_evidence_path = spec_package / "validation-evidence.md"

    if (implementation_notes_path.exists() or validation_evidence_path.exists()) and not args.overwrite:
        print_errors(["current MAGIA artifacts already exist; pass --overwrite only when replacing them is intentional"])
        return 1

    records = extract_legacy_execution_log(notes_path)
    validation_runs = extract_legacy_validation_runs(validation_path)
    if not records and not validation_runs:
        print_errors(["no legacy execution content found to adapt"])
        return 1

    write_implementation_notes(implementation_notes_path, args.spec_id, records)
    write_validation_evidence(validation_evidence_path, args.spec_id, records, validation_runs)
    print(f"OK: adapted legacy execution content into {implementation_notes_path.name} and {validation_evidence_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
