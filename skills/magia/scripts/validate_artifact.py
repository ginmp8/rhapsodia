#!/usr/bin/env python3
"""Dispatch canonical MAGIA artifact validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from magia_utils import parse_spec_id

EXECUTION_ARTIFACTS = {"implementation-notes.md", "validation-evidence.md"}
SHARED_SPEC_ARTIFACTS = {"manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md", "technical-design.md"}


def infer_board_context(path: Path) -> tuple[Path, Path, str | None]:
    parts = list(path.resolve().parts)
    try:
        docs_index = [part.lower() for part in parts].index("docs")
    except ValueError as exc:
        raise ValueError(f"{path}: path is outside docs/boards/") from exc
    expected = ["docs", "boards"]
    if [part.lower() for part in parts[docs_index : docs_index + 2]] != expected or len(parts) <= docs_index + 5:
        raise ValueError(f"{path}: path is outside docs/boards/<board_id>/<year>/cycles/<cycle_id>/")
    if parts[docs_index + 4].lower() != "cycles":
        raise ValueError(f"{path}: path is outside docs/boards/<board_id>/<year>/cycles/<cycle_id>/")
    repo_root = Path(*parts[:docs_index])
    board_root = Path(*parts[: docs_index + 6])
    spec_id: str | None = None
    if len(parts) > docs_index + 7 and parts[docs_index + 6].lower() == "specs":
        spec_id = parts[docs_index + 7]
        parse_spec_id(spec_id)
    return repo_root, board_root, spec_id


def validate_one(path: Path) -> int:
    from validate_execution_state import main as validate_execution_state
    from validate_repo_board import main as validate_repo_board
    repo_root, board_root, spec_id = infer_board_context(path)
    rc = validate_repo_board([str(repo_root), "--board-root", str(board_root)])
    if rc:
        return rc
    if path.name in EXECUTION_ARTIFACTS:
        if not spec_id:
            print(f"ERROR: {path}: could not infer canonical spec_id")
            return 1
        return validate_execution_state([str(board_root), "--spec-id", spec_id])
    if path.name in SHARED_SPEC_ARTIFACTS and not spec_id:
        print(f"ERROR: {path}: shared spec artifact is outside a canonical spec package")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGIA artifacts through canonical board/state validators.")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)
    result = 0
    for raw in args.paths:
        result = max(result, validate_one(Path(raw).resolve()))
    return result


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
