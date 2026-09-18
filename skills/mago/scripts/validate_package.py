#!/usr/bin/env python3
"""
Validate cross-artifact consistency for MAGO spec packages.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from mago_utils import dedupe_preserve_order, strip_quotes

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback exists for environments without PyYAML
    yaml = None


TASK_HEADER_RE = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s+(?P<task_id>task\d{3}):\s+.+$")
DEPENDENCIES_RE = re.compile(r"^\s*-\s+Dependencies:\s*(?P<value>.+?)\s*$")
NOTES_TASK_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})\b")
NOTES_STATUS_RE = re.compile(r"^\s*-\s+Status:\s*(?P<value>.+?)\s*$")
MANIFEST_TOP_LEVEL_RE = re.compile(r"^[a-z_]+:")
MANIFEST_NESTED_KEY_RE = re.compile(r"^\s+([a-z_]+):\s*(.+?)?\s*$")
MANIFEST_NESTED_TASK_ID_RE = re.compile(r"^\s+task_id:\s*(.+?)\s*$")
VALID_EXECUTION_STATUSES = {"not_started", "in_progress", "blocked", "done"}
VALID_LAST_EXECUTION_KEYS = {"task_id", "date", "summary", "files_changed"}


@dataclass(frozen=True)
class TaskRef:
    task_id: str
    line_number: int
    checked: bool = False


class ManifestParseError(ValueError):
    pass



def parse_tasks(tasks_path: Path) -> tuple[dict[str, TaskRef], list[str], list[tuple[int, str]]]:
    task_map: dict[str, TaskRef] = {}
    duplicates: list[str] = []
    dependency_lines: list[tuple[int, str]] = []

    for line_number, line in enumerate(tasks_path.read_text(encoding="utf-8").splitlines(), start=1):
        task_match = TASK_HEADER_RE.match(line)
        if task_match:
            task_id = task_match.group("task_id")
            if task_id in task_map:
                duplicates.append(
                    f"{tasks_path}:{line_number}: duplicate task id `{task_id}` "
                    f"(first seen on line {task_map[task_id].line_number})"
                )
            else:
                task_map[task_id] = TaskRef(
                    task_id=task_id,
                    line_number=line_number,
                    checked=task_match.group("mark").lower() == "x",
                )
            continue

        dependency_match = DEPENDENCIES_RE.match(line)
        if dependency_match:
            dependency_lines.append((line_number, dependency_match.group("value").strip()))

    return task_map, duplicates, dependency_lines


def extract_dependency_ids(value: str) -> tuple[list[str], bool]:
    if value.lower() == "none":
        return [], True

    dependency_ids = re.findall(r"task\d{3}", value)
    normalized = re.sub(r"task\d{3}", "", value)
    normalized = normalized.replace(",", " ").strip()
    is_clean = not normalized
    return dependency_ids, is_clean


def parse_notes_task_ids(notes_path: Path) -> tuple[list[TaskRef], list[str], list[str]]:
    refs: list[TaskRef] = []
    duplicates: list[str] = []
    warnings: list[str] = []
    seen: dict[str, int] = {}
    current_task_id: str | None = None
    current_task_line: int | None = None
    current_has_status = False

    for line_number, line in enumerate(notes_path.read_text(encoding="utf-8").splitlines(), start=1):
        match = NOTES_TASK_RE.match(line)
        if match:
            if current_task_id is not None and not current_has_status and current_task_line is not None:
                warnings.append(
                    f"{notes_path}:{current_task_line}: execution-log subsection `{current_task_id}` "
                    "is missing canonical `- Status: ...`"
                )
            task_id = match.group("task_id")
            current_task_id = task_id
            current_task_line = line_number
            current_has_status = False
            refs.append(TaskRef(task_id=task_id, line_number=line_number))
            if task_id in seen:
                duplicates.append(
                    f"{notes_path}:{line_number}: duplicate execution-log subsection for `{task_id}` "
                    f"(first seen on line {seen[task_id]})"
                )
            else:
                seen[task_id] = line_number
            continue

        status_match = NOTES_STATUS_RE.match(line)
        if status_match and current_task_id is not None:
            current_has_status = True
            status_value = strip_quotes(status_match.group("value")) or ""
            if status_value not in VALID_EXECUTION_STATUSES:
                warnings.append(
                    f"{notes_path}:{line_number}: execution-log status `{status_value}` for `{current_task_id}` "
                    f"is noncanonical; use one of {sorted(VALID_EXECUTION_STATUSES)}"
                )

    if current_task_id is not None and not current_has_status and current_task_line is not None:
        warnings.append(
            f"{notes_path}:{current_task_line}: execution-log subsection `{current_task_id}` "
            "is missing canonical `- Status: ...`"
        )

    return refs, duplicates, warnings


def parse_manifest_data(manifest_path: Path) -> dict[str, object]:
    if yaml is not None:
        try:
            loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:  # type: ignore[attr-defined]
            mark = getattr(exc, "problem_mark", None)
            location = f":{mark.line + 1}:{mark.column + 1}" if mark is not None else ""
            problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
            raise ManifestParseError(f"{manifest_path}{location}: invalid YAML: {problem}") from None
        if not isinstance(loaded, dict):
            return {"status": None, "phase": None, "last_execution_task_id": None, "last_execution_keys": set()}

        status = strip_quotes(str(loaded.get("status"))) if loaded.get("status") is not None else None
        phase = strip_quotes(str(loaded.get("phase"))) if loaded.get("phase") is not None else None

        last_execution = loaded.get("last_execution")
        task_id = None
        last_execution_keys: set[str] = set()
        if isinstance(last_execution, dict) and last_execution.get("task_id") is not None:
            last_execution_keys = {str(key) for key in last_execution.keys()}
            task_id = strip_quotes(str(last_execution.get("task_id")))

        return {
            "status": status,
            "phase": phase,
            "last_execution_task_id": task_id,
            "last_execution_keys": last_execution_keys,
        }

    status = None
    phase = None
    last_execution_task_id = None
    in_last_execution = False
    last_execution_keys: set[str] = set()

    for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if MANIFEST_TOP_LEVEL_RE.match(line):
            in_last_execution = line.startswith("last_execution:")
            key, value = line.split(":", 1)
            scalar = strip_quotes(value)
            if key == "status":
                status = scalar
            elif key == "phase":
                phase = scalar
            continue

        if in_last_execution:
            nested_key = MANIFEST_NESTED_KEY_RE.match(line)
            if nested_key:
                last_execution_keys.add(nested_key.group(1))
            nested = MANIFEST_NESTED_TASK_ID_RE.match(line)
            if nested:
                last_execution_task_id = strip_quotes(nested.group(1))

    return {
        "status": status,
        "phase": phase,
        "last_execution_task_id": last_execution_task_id,
        "last_execution_keys": last_execution_keys,
    }


def validate_package(package_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    technical_design_path = package_path / "technical-design.md"
    if technical_design_path.exists():
        from validate_technical_design import validate as validate_technical_design

        errors.extend(validate_technical_design(technical_design_path))

    tasks_path = package_path / "tasks.md"
    if not tasks_path.exists():
        return [f"{package_path}: missing required tasks.md"], warnings

    task_map, duplicate_task_errors, dependency_lines = parse_tasks(tasks_path)
    errors.extend(duplicate_task_errors)
    if not task_map:
        errors.append(f"{tasks_path}: no task ids in `taskNNN` format were found")

    known_task_ids = set(task_map)

    for line_number, dependency_value in dependency_lines:
        dependency_ids, clean_format = extract_dependency_ids(dependency_value)
        if dependency_value.lower() != "none" and not clean_format:
            warnings.append(
                f"{tasks_path}:{line_number}: dependency line contains non-task text: `{dependency_value}`"
            )
        for dependency_id in dependency_ids:
            if dependency_id not in known_task_ids:
                errors.append(
                    f"{tasks_path}:{line_number}: dependency `{dependency_id}` does not exist in tasks.md"
                )

    notes_path = package_path / "notes.md"
    if notes_path.exists():
        note_refs, duplicate_note_errors, note_warnings = parse_notes_task_ids(notes_path)
        errors.extend(duplicate_note_errors)
        warnings.extend(note_warnings)
        for ref in note_refs:
            if ref.task_id not in known_task_ids:
                errors.append(
                    f"{notes_path}:{ref.line_number}: execution-log task `{ref.task_id}` does not exist in tasks.md"
                )

    manifest_path = package_path / "manifest.yaml"
    if manifest_path.exists():
        try:
            manifest_data = parse_manifest_data(manifest_path)
        except ManifestParseError as exc:
            errors.append(str(exc))
            return dedupe_preserve_order(errors), dedupe_preserve_order(warnings)

        last_execution_task_id = manifest_data["last_execution_task_id"]
        if last_execution_task_id and last_execution_task_id not in known_task_ids:
            errors.append(
                f"{manifest_path}: `last_execution.task_id` references `{last_execution_task_id}`, "
                "which does not exist in tasks.md"
            )
        manifest_last_execution_keys = manifest_data["last_execution_keys"]
        unexpected_keys = sorted(set(manifest_last_execution_keys) - VALID_LAST_EXECUTION_KEYS)
        if unexpected_keys:
            warnings.append(
                f"{manifest_path}: `last_execution` uses noncanonical key(s) {unexpected_keys}; "
                "canonical shape keeps `task_id` required and `date`, `summary`, `files_changed` optional"
            )

        if manifest_data["status"] == "done" or manifest_data["phase"] == "done":
            open_tasks = sorted(task_id for task_id, ref in task_map.items() if not ref.checked)
            if open_tasks:
                preview = ", ".join(open_tasks[:5])
                suffix = "" if len(open_tasks) <= 5 else ", ..."
                errors.append(
                    f"{manifest_path}: package is marked done but still has open tasks in tasks.md: "
                    f"{preview}{suffix}"
                )

    return dedupe_preserve_order(errors), dedupe_preserve_order(warnings)


def resolve_package_targets(board_root_raw: str, spec_ids: Iterable[str]) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    board_root = Path(board_root_raw).resolve()

    for spec_id in spec_ids:
        candidate = board_root / "specs" / spec_id
        if candidate not in seen:
            resolved.append(candidate)
            seen.add(candidate)

    if resolved:
        return resolved

    specs_dir = board_root / "specs"
    if specs_dir.is_dir():
        for child in sorted(specs_dir.iterdir()):
            if child.is_dir() and (child / "tasks.md").exists() and child not in seen:
                resolved.append(child)
                seen.add(child)
    elif board_root not in seen:
        resolved.append(board_root)
        seen.add(board_root)

    return resolved


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate cross-artifact consistency for MAGO spec packages."
    )
    parser.add_argument("board_root", help="Path to the canonical BOARD_ROOT.")
    parser.add_argument(
        "--spec-id",
        action="append",
        default=[],
        help="Repeat to validate one or more selected spec packages under BOARD_ROOT. Omit to validate every package under BOARD_ROOT/specs/.",
    )
    args = parser.parse_args(argv)

    package_paths = resolve_package_targets(args.board_root, args.spec_id)
    if not package_paths:
        print("ERROR: no package targets found")
        print("FAILED: 1 errors, 0 warnings")
        return 1

    total_errors = 0
    total_warnings = 0

    for package_path in package_paths:
        if not package_path.exists():
            print(f"ERROR: {package_path}: target does not exist")
            total_errors += 1
            continue

        errors, warnings = validate_package(package_path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")

    if total_errors:
        print(f"FAILED: {total_errors} errors, {total_warnings} warnings")
        return 1

    if total_warnings:
        print(f"OK: validated {len(package_paths)} package(s) with {total_warnings} warning(s)")
    else:
        print(f"OK: validated {len(package_paths)} package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
