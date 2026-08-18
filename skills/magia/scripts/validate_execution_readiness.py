#!/usr/bin/env python3
"""Validate that a selected canonical spec is dependency-ready for execution."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from board_contract import load_registry, validate_board
from magia_utils import BOARD_ROOT_TEMPLATE, TASK_ID_RE, parse_spec_id, print_errors, spec_package_path

TASK_LINE_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(?P<task_id>task\d{3}):")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate dependency and package readiness for one MAGIA execution target.")
    parser.add_argument("board_root", help=f"Canonical board root under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True)
    parser.add_argument("--task-id")
    args = parser.parse_args(argv)

    errors: list[str] = []
    board_root = Path(args.board_root).resolve()
    try:
        parse_spec_id(args.spec_id)
    except ValueError as exc:
        errors.append(str(exc))
    errors.extend(validate_board(board_root))
    records, registry_errors = load_registry(board_root)
    errors.extend(registry_errors)
    record = records.get(args.spec_id)
    if record is None:
        errors.append(f"missing selected registry entry `{args.spec_id}`")
    else:
        if record.get("status") in {"cancelled", "superseded", "done"}:
            errors.append(f"selected spec status `{record.get('status')}` is not executable")
        for dependency in record.get("depends_on_specs") or []:
            dependency_record = records.get(str(dependency))
            if dependency_record is None:
                continue
            if dependency_record.get("status") != "done":
                errors.append(f"dependency `{dependency}` is `{dependency_record.get('status')}`, expected `done`")

    package = spec_package_path(board_root, args.spec_id)
    for name in ("manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"):
        if not (package / name).is_file():
            errors.append(f"missing execution input: {package / name}")
    if args.task_id:
        if not TASK_ID_RE.fullmatch(args.task_id):
            errors.append(f"task_id must use taskNNN, got `{args.task_id}`")
        elif (package / "tasks.md").is_file():
            task_ids = {
                match.group("task_id")
                for line in (package / "tasks.md").read_text(encoding="utf-8-sig").splitlines()
                if (match := TASK_LINE_RE.match(line))
            }
            if args.task_id not in task_ids:
                errors.append(f"selected task `{args.task_id}` does not exist in tasks.md")

    if errors:
        print_errors(list(dict.fromkeys(errors)))
        return 1
    print(f"OK: {args.spec_id} is ready for execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
