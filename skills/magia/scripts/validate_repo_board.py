#!/usr/bin/env python3
"""Validate MAGIA repository-board placement, canonical contract, and package quality."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from board_contract import validate_board
from magia_utils import (
    BOARD_ROOT_TEMPLATE,
    dedupe_preserve_order,
    parse_cycle_id,
    parse_spec_id,
    is_relative_to,
    posix_rel,
    print_errors,
    resolve_board_root,
    validate_concrete_segment,
)

CANONICAL_ARTIFACT_NAMES = {
    "cycle.yaml",
    "manifest.yaml",
    "prd.md",
    "tasks.md",
    "validation.md",
    "notes.md",
    "implementation-notes.md",
    "validation-evidence.md",
}
REQUIRED_SPEC_FILES = {"manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"}
PLACEHOLDER_RE = re.compile(r"<[^>]+>")


def iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts)


def validate_canonical_segments(board_id: str, year: str, cycle_id: str) -> list[str]:
    errors: list[str] = []
    for label, value in (("board_id", board_id), ("year", year), ("cycle_id", cycle_id)):
        error = validate_concrete_segment(label, value)
        if error:
            errors.append(error)
    if not errors:
        try:
            parsed = parse_cycle_id(cycle_id)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if year != parsed["date"][:4]:
                errors.append(f"year `{year}` conflicts with cycle_id creation year `{parsed['date'][:4]}`")
    return errors


def collect_artifact_placement_errors(repo_root: Path, canonical_root: Path) -> list[str]:
    errors: list[str] = []
    docs_root = repo_root / "docs"
    boards_root = docs_root / "boards"

    for path in iter_files(boards_root):
        if path.name in CANONICAL_ARTIFACT_NAMES and not is_relative_to(path, canonical_root):
            errors.append(f"{posix_rel(path, repo_root)} is a MAGIA/planning artifact outside the selected {BOARD_ROOT_TEMPLATE.rstrip('/')}.")

    for path in iter_files(docs_root):
        if path.name in CANONICAL_ARTIFACT_NAMES and not is_relative_to(path, boards_root):
            errors.append(f"{posix_rel(path, repo_root)} is a MAGIA/planning artifact outside docs/boards/.")

    return errors


def collect_package_shape_errors(repo_root: Path, canonical_root: Path) -> list[str]:
    errors: list[str] = []
    specs_root = canonical_root / "specs"
    registry_root = canonical_root / "registry"

    if not canonical_root.exists():
        return [f"missing BOARD_ROOT: {posix_rel(canonical_root, repo_root)}"]
    if not (canonical_root / "cycle.yaml").is_file():
        errors.append(f"missing required artifact: {posix_rel(canonical_root / 'cycle.yaml', repo_root)}")
    if not registry_root.is_dir():
        errors.append(f"missing required registry directory: {posix_rel(registry_root, repo_root)}")
    if (canonical_root / "spec-catalog.yaml").exists():
        errors.append("spec-catalog.yaml is a generated projection and must not be an active board artifact")
    if (canonical_root / "define-queue.yaml").exists():
        errors.append("define-queue.yaml is a generated projection and must not be an active board artifact")

    if specs_root.exists():
        for child in sorted(specs_root.iterdir()):
            if not child.is_dir():
                continue
            try:
                parse_spec_id(child.name)
            except ValueError:
                errors.append(f"invalid spec directory name: {posix_rel(child, repo_root)}")
                continue
            present = {path.name for path in child.iterdir() if path.is_file()}
            for missing in sorted(REQUIRED_SPEC_FILES - present):
                errors.append(f"missing required spec artifact: {posix_rel(child / missing, repo_root)}")
            registry_path = registry_root / f"{child.name}.yaml"
            if not registry_path.is_file():
                errors.append(f"missing matching registry entry: {posix_rel(registry_path, repo_root)}")

    return errors


def collect_placeholder_errors(repo_root: Path, canonical_root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_files(canonical_root):
        if path.suffix.lower() not in {".md", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        for match in PLACEHOLDER_RE.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            errors.append(f"{posix_rel(path, repo_root)}:{line_no}: unresolved placeholder `{match.group(0)}`")
    return errors


def collect_errors(
    repo_root: Path,
    board_id: str | None,
    year: str | None,
    cycle_id: str | None,
    board_root_override: str | None,
) -> list[str]:
    errors: list[str] = []
    if board_root_override is None:
        assert board_id is not None and year is not None and cycle_id is not None
        errors.extend(validate_canonical_segments(board_id, year, cycle_id))
        if errors:
            return errors

    try:
        canonical_root = resolve_board_root(
            repo_root,
            board_root_override=board_root_override,
            board_id=board_id,
            year=year,
            cycle_id=cycle_id,
        )
    except ValueError as exc:
        return [str(exc)]

    errors.extend(collect_artifact_placement_errors(repo_root, canonical_root))
    errors.extend(collect_package_shape_errors(repo_root, canonical_root))
    errors.extend(collect_placeholder_errors(repo_root, canonical_root))
    if canonical_root.exists():
        errors.extend(validate_board(canonical_root))
    return dedupe_preserve_order(errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Validate MAGIA artifacts under {BOARD_ROOT_TEMPLATE.rstrip('/')}.")
    parser.add_argument("repo_root", help="Repository root to inspect.")
    parser.add_argument("--board-root", help="Explicit canonical BOARD_ROOT override.")
    parser.add_argument("--board_id", help="Concrete board id when --board-root is omitted.")
    parser.add_argument("--year", help="Concrete year when --board-root is omitted.")
    parser.add_argument("--cycle-id", dest="cycle_id", help="Concrete canonical cycle id when --board-root is omitted.")
    args = parser.parse_args(argv)

    if args.board_root is None and (not args.board_id or not args.year or not args.cycle_id):
        parser.error("either --board-root or --board_id, --year, and --cycle-id are required")

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print_errors([f"repository root does not exist: {repo_root}"])
        return 1

    errors = collect_errors(repo_root, args.board_id, args.year, args.cycle_id, args.board_root)
    if errors:
        print_errors(errors)
        return 1

    print("OK: board artifacts use the canonical BOARD_ROOT and registry contract")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
