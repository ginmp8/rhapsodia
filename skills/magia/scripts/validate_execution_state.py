#!/usr/bin/env python3
"""Validate MAGIA execution-state consistency and semantic execution evidence."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from board_contract import registry_for
from planning_traceability import canonical_source_matches
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
SECTION_RE = re.compile(r"^###\s+(?P<section>.+?)\s*$")
BULLET_RE = re.compile(r"^\s*-\s+(?P<value>.+?)\s*$")
PASS_RESULTS = {"pass", "passed", "success", "successful", "ok"}
FAIL_RESULTS = {"fail", "failed", "failure", "error", "blocked"}
NON_CONCRETE = {"", "unknown", "none", "n/a", "na", "not-applicable", "not applicable", "not-run", "planned", "tbd"}
NON_CONCRETE_PHRASE_RE = re.compile(
    r"\b(?:" + "to" + r"do|placeholder|lorem ipsum|example only|sample text|to be (?:defined|decided|determined))\b"
    r"|\bno\s+(?:concrete\s+)?(?:evidence|requirement|acceptance criterion|check|command|result)\b"
    r"|\bnot\s+(?:an?\s+)?(?:requirement|acceptance criterion|check|evidence|executed)\b",
    re.IGNORECASE,
)


def normalize_value(value: str) -> str:
    return value.strip().strip("`").strip().lower()


def is_concrete(value: str) -> bool:
    normalized = normalize_value(value)
    return (
        normalized not in NON_CONCRETE
        and not normalized.startswith("<")
        and not NON_CONCRETE_PHRASE_RE.search(normalized)
    )


def parse_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [cell.strip() for cell in stripped[1:-1].split("|")]
    if not cells or all(not cell for cell in cells):
        return None
    if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
        return None
    return cells


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


def _new_validation_run() -> dict[str, Any]:
    return {
        "executed_checks": [],
        "traceability": [],
        "failed_checks": [],
        "not_run_checks": [],
        "static_evidence": [],
    }


def parse_validation_details(validation_path: Path) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    current_task: str | None = None
    current_section: str | None = None

    for line in read_lines(validation_path):
        run_match = VALIDATION_RUN_RE.match(line)
        if run_match:
            current_task = run_match.group("task_id")
            current_section = None
            runs[current_task] = _new_validation_run()
            continue
        if current_task is None:
            continue
        if line.startswith("## "):
            current_task = None
            current_section = None
            continue
        section_match = SECTION_RE.match(line)
        if section_match:
            current_section = section_match.group("section").strip().lower()
            continue

        run = runs[current_task]
        row = parse_table_row(line)
        if row:
            normalized_header = [normalize_value(cell) for cell in row]
            if normalized_header and normalized_header[0] in {
                "check", "requirement or acceptance criterion", "criterion", "requirement"
            }:
                continue
            if current_section == "executed checks" and len(row) >= 4:
                run["executed_checks"].append({
                    "check": row[0],
                    "command": row[1],
                    "result": row[2],
                    "evidence": row[3],
                })
            elif current_section in {"traceability", "acceptance coverage"} and len(row) >= 4:
                run["traceability"].append({
                    "source": row[0],
                    "check": row[1],
                    "result": row[2],
                    "evidence": row[3],
                })
            elif current_section == "not-run checks" and len(row) >= 3:
                run["not_run_checks"].append({
                    "check": row[0],
                    "reason": row[1],
                    "risk": row[2],
                })
            continue

        bullet = BULLET_RE.match(line)
        if not bullet:
            continue
        value = bullet.group("value").strip()
        normalized = normalize_value(value)
        if current_section == "failed checks" and normalized != "none":
            run["failed_checks"].append(value)
        elif current_section == "static evidence" and normalized != "none":
            run["static_evidence"].append(value)

    return runs


def parse_validation(validation_path: Path) -> set[str]:
    """Return task ids with an execution-run section; retained for compatibility."""
    return set(parse_validation_details(validation_path))


def _valid_passed_checks(run: dict[str, Any]) -> list[dict[str, str]]:
    return [
        row for row in run["executed_checks"]
        if normalize_value(row["result"]) in PASS_RESULTS
        and is_concrete(row["check"])
        and is_concrete(row["command"])
        and is_concrete(row["evidence"])
    ]


def _valid_traceability(
    spec_package: Path,
    task_id: str,
    run: dict[str, Any],
    passed_checks: list[dict[str, str]],
) -> list[dict[str, str]]:
    executed_check_names = {normalize_value(row["check"]) for row in passed_checks}
    return [
        row for row in run["traceability"]
        if normalize_value(row["result"]) in PASS_RESULTS
        and is_concrete(row["source"])
        and canonical_source_matches(spec_package, task_id, row["source"])
        and is_concrete(row["check"])
        and is_concrete(row["evidence"])
        and normalize_value(row["check"]) in executed_check_names
    ]


def _has_failed_result(run: dict[str, Any]) -> bool:
    return bool(run["failed_checks"]) or any(
        normalize_value(row["result"]) in FAIL_RESULTS for row in run["executed_checks"]
    ) or any(normalize_value(row["result"]) in FAIL_RESULTS for row in run["traceability"])


def _has_substantive_evidence(run: dict[str, Any]) -> bool:
    if run["failed_checks"] or any(is_concrete(item) for item in run["static_evidence"]):
        return True
    if any(is_concrete(row["check"]) and is_concrete(row["command"]) for row in run["executed_checks"]):
        return True
    if any(is_concrete(row["check"]) and is_concrete(row["reason"]) for row in run["not_run_checks"]):
        return True
    return False


def validate_task_evidence(spec_package: Path, task_id: str, requested_status: str) -> list[str]:
    notes_path = spec_package / "implementation-notes.md"
    validation_path = spec_package / "validation-evidence.md"
    errors: list[str] = []
    if not notes_path.is_file():
        errors.append(f"missing implementation-notes.md required for `{task_id}` evidence")
        return errors
    if not validation_path.is_file():
        errors.append(f"missing validation-evidence.md required for `{task_id}` evidence")
        return errors

    notes_status = parse_notes(notes_path)
    recorded_status = notes_status.get(task_id)
    if recorded_status != requested_status:
        errors.append(
            f"implementation-notes.md status for `{task_id}` is `{recorded_status or 'missing'}`, "
            f"expected `{requested_status}` before execution-state sync."
        )

    run = parse_validation_details(validation_path).get(task_id)
    if run is None:
        errors.append(f"validation-evidence.md has no `Execution Run - {task_id}` section.")
        return errors
    if not _has_substantive_evidence(run):
        errors.append(f"validation-evidence.md run for `{task_id}` contains no substantive evidence.")

    if requested_status == "done":
        passed_checks = _valid_passed_checks(run)
        if not passed_checks:
            errors.append(
                f"`{task_id}` cannot be done without at least one passed executed check containing "
                "a concrete check, command or method, and evidence."
            )
        if not _valid_traceability(spec_package, task_id, run, passed_checks):
            errors.append(
                f"`{task_id}` cannot be done without a passed Traceability row whose source resolves to "
                "a real PRD objective, acceptance criterion, or selected task and whose check matches the same "
                "passed executed check and evidence."
            )
        if _has_failed_result(run):
            errors.append(f"`{task_id}` cannot be done while failed or blocked validation evidence remains.")
    return errors


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

    for task_id, status in notes_status.items():
        if status in executed_statuses:
            errors.extend(validate_task_evidence(spec_package, task_id, status))

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
            "Validate MAGIA semantic evidence and execution-state consistency across tasks.md, "
            "implementation-notes.md, validation-evidence.md, manifest.yaml, and registry/<spec_id>.yaml."
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

    print("OK: execution-state records and semantic validation evidence are aligned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
