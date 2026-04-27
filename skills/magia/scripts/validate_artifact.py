#!/usr/bin/env python3
"""Dispatch MAGIA artifact validation without relying on manual validator selection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SPEC_ARTIFACTS = {"manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"}


def infer_board_context(path: Path) -> tuple[Path, Path, str | None]:
    parts = list(path.parts)
    lower_parts = [part.lower() for part in parts]
    try:
        docs_index = lower_parts.index("docs")
    except ValueError as exc:
        raise ValueError(f"{path}: path is outside docs/boards/") from exc

    if len(parts) <= docs_index + 3 or lower_parts[docs_index + 1] != "boards":
        raise ValueError(f"{path}: path is outside docs/boards/<board_id>/<cycle_version>/")

    repo_root = Path(*parts[:docs_index])
    board_root = Path(*parts[: docs_index + 4])
    spec_id: str | None = None
    if len(parts) > docs_index + 5 and lower_parts[docs_index + 4] == "specs":
        spec_id = parts[docs_index + 5]
    return repo_root, board_root, spec_id


def validate_one(path: Path) -> int:
    from validate_execution_state import main as validate_execution_state_main
    from validate_repo_board import main as validate_repo_board_main

    repo_root, board_root, spec_id = infer_board_context(path)
    board_result = validate_repo_board_main([str(repo_root), "--board-root", str(board_root)])
    if board_result != 0:
        return board_result

    if path.name in SPEC_ARTIFACTS:
        if not spec_id:
            print(f"ERROR: {path}: could not infer spec_id from path")
            return 1
        return validate_execution_state_main([str(board_root), "--spec-id", spec_id])

    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a MAGIA artifact with the canonical validator for its template family.")
    parser.add_argument("paths", nargs="+", help="Artifact path(s) to validate.")
    args = parser.parse_args(argv)

    exit_code = 0
    for raw_path in args.paths:
        result = validate_one(Path(raw_path).resolve())
        if result != 0:
            exit_code = result
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
