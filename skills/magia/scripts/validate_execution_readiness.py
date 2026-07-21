#!/usr/bin/env python3
"""Validate dependency, requirement, task, and validation-plan readiness for RALPH execution."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from board_contract import load_registry, validate_board
from magia_utils import BOARD_ROOT_TEMPLATE, TASK_ID_RE, parse_spec_id, print_errors, spec_package_path

TASK_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(?P<task_id>task\d{3}):\s*(?P<title>.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(?P<value>.+?)\s*$")
NON_CONCRETE = {"", "unknown", "none", "n/a", "not-applicable", "not applicable", "tbd"}
GENERIC_TASK_WORDS = {"task", "work", "change", "update", "implement", "fix", "first", "second", "feature"}
OBJECTIVE_HEADINGS = {"objective", "objectives", "goal", "goals", "desired outcome", "problem statement"}
ACCEPTANCE_HEADINGS = {
    "acceptance criterion",
    "acceptance criteria",
    "success criterion",
    "success criteria",
    "expected behavior",
}
VALIDATION_HEADINGS = {
    "validation plan",
    "planned check",
    "planned checks",
    "validation check",
    "validation checks",
    "test plan",
    "verification",
    "checks",
}
NON_CONCRETE_PHRASE_RE = re.compile(
    r"\b(?:" + "to" + r"do|placeholder|lorem ipsum|example only|sample text|to be (?:defined|decided|determined))\b"
    r"|\b(?:no|not|missing|absent)\s+(?:concrete\s+)?(?:objective|goal|requirement|acceptance criterion|validation check|expected result)\b"
    r"|\bdoes not define\b",
    re.IGNORECASE,
)
VALIDATION_ACTION_RE = re.compile(
    r"\b(?:run|execute|test|build|lint|compile|smoke|migrate|inspect|check|manually|verify|confirm)\b|`[^`]+`",
    re.IGNORECASE,
)
VALIDATION_OUTCOME_RE = re.compile(
    r"\b(?:expect(?:ed)?|verify that|confirm that|must|should|exit code|returns?|produces?|contains?|equals?|matches?|passes?|succeeds?|no errors?|without errors?)\b",
    re.IGNORECASE,
)


def _normalize(value: str) -> str:
    return value.strip().strip("`").strip().lower()


def _heading_name(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    return stripped.lstrip("#").strip().rstrip("#").strip().lower()


def _is_concrete(value: str, *, minimum_words: int = 1) -> bool:
    normalized = _normalize(value)
    if normalized in NON_CONCRETE or normalized.startswith("<"):
        return False
    if NON_CONCRETE_PHRASE_RE.search(normalized):
        return False
    return len(re.findall(r"[A-Za-z0-9]+", normalized)) >= minimum_words


def _has_acceptance_criterion(prd_path: Path) -> bool:
    in_acceptance = False
    for line in prd_path.read_text(encoding="utf-8-sig").splitlines():
        heading = _heading_name(line)
        if heading is not None:
            in_acceptance = heading in ACCEPTANCE_HEADINGS
            continue
        if in_acceptance and (match := BULLET_RE.match(line)) and _is_concrete(
            match.group("value"), minimum_words=5
        ):
            return True
    return False


def _has_concrete_objective(prd_path: Path) -> bool:
    in_objective = False
    for line in prd_path.read_text(encoding="utf-8-sig").splitlines():
        heading = _heading_name(line)
        if heading is not None:
            in_objective = heading in OBJECTIVE_HEADINGS
            continue
        if not in_objective:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        match = BULLET_RE.match(line)
        value = match.group("value") if match else stripped
        if _is_concrete(value, minimum_words=5):
            return True
    return False


def _has_concrete_validation_check(validation_path: Path) -> bool:
    in_validation = False
    for line in validation_path.read_text(encoding="utf-8-sig").splitlines():
        heading = _heading_name(line)
        if heading is not None:
            in_validation = heading in VALIDATION_HEADINGS
            continue
        if not in_validation:
            continue
        match = BULLET_RE.match(line)
        if not match:
            continue
        value = match.group("value")
        if not _is_concrete(value, minimum_words=5):
            continue
        if VALIDATION_ACTION_RE.search(value) and VALIDATION_OUTCOME_RE.search(value):
            return True
    return False


def _task_title_error(title: str) -> str | None:
    words = re.findall(r"[A-Za-z0-9]+", title.lower())
    if len(words) < 3:
        return "selected task title must contain at least three descriptive words"
    if set(words) <= GENERIC_TASK_WORDS:
        return "selected task title is too generic to bound execution"
    return None


def collect_errors(board_root: Path, spec_id: str, task_id: str | None = None) -> list[str]:
    errors: list[str] = []
    try:
        parse_spec_id(spec_id)
    except ValueError as exc:
        errors.append(str(exc))
    errors.extend(validate_board(board_root))
    records, registry_errors = load_registry(board_root)
    errors.extend(registry_errors)
    record = records.get(spec_id)
    if record is None:
        errors.append(f"missing selected registry entry `{spec_id}`")
    else:
        if record.get("status") in {"cancelled", "superseded", "done"}:
            errors.append(f"selected spec status `{record.get('status')}` is not executable")
        for dependency in record.get("depends_on_specs") or []:
            dependency_record = records.get(str(dependency))
            if dependency_record is None:
                continue
            if dependency_record.get("status") != "done":
                errors.append(f"dependency `{dependency}` is `{dependency_record.get('status')}`, expected `done`")

    package = spec_package_path(board_root, spec_id)
    for name in ("manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"):
        if not (package / name).is_file():
            errors.append(f"missing execution input: {package / name}")

    prd_path = package / "prd.md"
    if prd_path.is_file():
        if not _has_concrete_objective(prd_path):
            errors.append("prd.md must contain a concrete observable objective before execution")
        if not _has_acceptance_criterion(prd_path):
            errors.append("prd.md must contain at least one concrete acceptance criterion before execution")

    validation_path = package / "validation.md"
    if validation_path.is_file() and not _has_concrete_validation_check(validation_path):
        errors.append("validation.md must contain at least one concrete planned validation check before execution")

    if task_id:
        if not TASK_ID_RE.fullmatch(task_id):
            errors.append(f"task_id must use taskNNN, got `{task_id}`")
        elif (package / "tasks.md").is_file():
            tasks = {
                match.group("task_id"): match.group("title")
                for line in (package / "tasks.md").read_text(encoding="utf-8-sig").splitlines()
                if (match := TASK_LINE_RE.match(line))
            }
            if task_id not in tasks:
                errors.append(f"selected task `{task_id}` does not exist in tasks.md")
            else:
                title_error = _task_title_error(tasks[task_id])
                if title_error:
                    errors.append(f"selected task `{task_id}` {title_error}: `{tasks[task_id]}`")

    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate dependencies, requirements, task specificity, and validation-plan readiness."
    )
    parser.add_argument("board_root", help=f"Canonical board root under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True)
    parser.add_argument("--task-id")
    args = parser.parse_args(argv)

    errors = collect_errors(Path(args.board_root).resolve(), args.spec_id, args.task_id)
    if errors:
        print_errors(errors)
        return 1
    print(f"OK: {args.spec_id} is ready for execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
