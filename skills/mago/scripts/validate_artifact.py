#!/usr/bin/env python3
"""Dispatch MAGO artifact validation without relying on manual validator selection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SPEC_ARTIFACTS = {"manifest.yaml", "prd.md", "technical-design.md", "tasks.md", "notes.md", "validation.md", "architecture-decisions.md", "execution-handoff-plan.md", "contract-spec.md", "migration-strategy.md", "observability-design.md", "operational-requirements.md", "security-and-risk-considerations.md", "open-questions.md"}


def infer_board_context(path: Path) -> tuple[Path, Path, str | None]:
    resolved = path.resolve()
    for parent in (resolved.parent, *resolved.parents):
        if not (parent / "cycle.yaml").is_file():
            continue
        parts = list(parent.parts)
        lower_parts = [part.lower() for part in parts]
        try:
            docs_index = lower_parts.index("docs")
        except ValueError as exc:
            raise ValueError(f"{path}: canonical cycle root is outside docs/boards/") from exc
        repo_root = Path(*parts[:docs_index])
        spec_id = None
        relative = resolved.relative_to(parent)
        if len(relative.parts) >= 3 and relative.parts[0] == "specs":
            spec_id = relative.parts[1]
        return repo_root, parent, spec_id
    raise ValueError(f"{path}: no canonical MAGO cycle root containing cycle.yaml was found")


def validate_one(path: Path) -> int:
    from validate_package import main as validate_package_main
    from validate_repo_board import main as validate_repo_board_main

    repo_root, board_root, spec_id = infer_board_context(path)
    if path.name == "technical-design.md":
        from validate_technical_design import main as validate_technical_design_main

        return validate_technical_design_main([str(path)])

    if path.name in SPEC_ARTIFACTS:
        if not spec_id:
            print(f"ERROR: {path}: could not infer spec_id from path")
            return 1
        return validate_package_main([str(board_root), "--spec-id", spec_id])

    return validate_repo_board_main([str(repo_root), "--board-root", str(board_root)])


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a MAGO artifact with the canonical validator for its template family.")
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
