#!/usr/bin/env python3
"""Validate MAGIA repository-board artifact placement and package quality."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, dedupe_preserve_order, is_relative_to, posix_rel, print_errors, resolve_board_root, validate_concrete_segment

CANONICAL_ARTIFACT_NAMES = {
    "spec-catalog.yaml",
    "manifest.yaml",
    "prd.md",
    "tasks.md",
    "validation.md",
    "notes.md",
}
REQUIRED_SPEC_FILES = {"manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"}
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
SPEC_DIR_RE = re.compile(r"^spec\d{3}$")


def iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts)


def validate_canonical_segments(board_id: str, cycle_version: str) -> list[str]:
    errors: list[str] = []
    for label, value in (("board_id", board_id), ("cycle_version", cycle_version)):
        error = validate_concrete_segment(label, value)
        if error:
            errors.append(error)
    return errors


def collect_artifact_placement_errors(repo_root: Path, canonical_root: Path) -> list[str]:
    errors: list[str] = []
    docs_root = repo_root / "docs"
    boards_root = docs_root / "boards"

    for path in iter_files(boards_root):
        if path.name in CANONICAL_ARTIFACT_NAMES and not is_relative_to(path, canonical_root):
            errors.append(
                f"{posix_rel(path, repo_root)} is a MAGIA artifact outside {BOARD_ROOT_TEMPLATE.rstrip('/')}."
            )

    for path in iter_files(docs_root):
        if path.name in CANONICAL_ARTIFACT_NAMES and not is_relative_to(path, boards_root):
            errors.append(f"{posix_rel(path, repo_root)} is a MAGIA artifact outside docs/boards/.")

    return errors


def collect_package_shape_errors(repo_root: Path, canonical_root: Path) -> list[str]:
    errors: list[str] = []
    spec_catalog = canonical_root / "spec-catalog.yaml"
    specs_root = canonical_root / "specs"

    if not canonical_root.exists():
        return [f"missing BOARD_ROOT: {posix_rel(canonical_root, repo_root)}"]
    if not spec_catalog.exists():
        errors.append(f"missing required artifact: {posix_rel(spec_catalog, repo_root)}")

    if specs_root.exists():
        for child in sorted(specs_root.iterdir()):
            if not child.is_dir():
                continue
            if not SPEC_DIR_RE.match(child.name):
                errors.append(f"invalid spec directory name: {posix_rel(child, repo_root)}")
                continue
            present = {path.name for path in child.iterdir() if path.is_file()}
            for missing in sorted(REQUIRED_SPEC_FILES - present):
                errors.append(f"missing required spec artifact: {posix_rel(child / missing, repo_root)}")

    return errors


def collect_placeholder_errors(repo_root: Path, canonical_root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_files(canonical_root):
        if path.suffix.lower() not in {".md", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for match in PLACEHOLDER_RE.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            errors.append(f"{posix_rel(path, repo_root)}:{line_no}: unresolved placeholder `{match.group(0)}`")
    return errors


def collect_errors(
    repo_root: Path,
    board_id: str | None,
    cycle_version: str | None,
    board_root_override: str | None,
) -> list[str]:
    errors: list[str] = []
    if board_root_override is None:
        assert board_id is not None
        assert cycle_version is not None
        errors = validate_canonical_segments(board_id, cycle_version)
        if errors:
            return errors

    try:
        canonical_root = resolve_board_root(
            repo_root,
            board_root_override=board_root_override,
            board_id=board_id,
            cycle_version=cycle_version,
        )
    except ValueError as exc:
        return [str(exc)]

    errors.extend(collect_artifact_placement_errors(repo_root, canonical_root))
    errors.extend(collect_package_shape_errors(repo_root, canonical_root))
    errors.extend(collect_placeholder_errors(repo_root, canonical_root))
    return dedupe_preserve_order(errors)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=f"Validate MAGIA artifacts under {BOARD_ROOT_TEMPLATE.rstrip('/')}."
    )
    parser.add_argument("repo_root", help="Repository root to inspect.")
    parser.add_argument("--board-root", help="Explicit BOARD_ROOT override. When omitted, derive it from --board_id and --cycle_version.")
    parser.add_argument("--board_id", help="Concrete dynamic board id segment when --board-root is omitted.")
    parser.add_argument("--cycle_version", help="Concrete dynamic cycle version segment when --board-root is omitted.")
    args = parser.parse_args(argv)

    if args.board_root is None and (not args.board_id or not args.cycle_version):
        parser.error("either --board-root or both --board_id and --cycle_version are required")

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print_errors([f"repository root does not exist: {repo_root}"])
        return 1

    errors = collect_errors(repo_root, args.board_id, args.cycle_version, args.board_root)
    if errors:
        print_errors(errors)
        return 1

    print("OK: board artifacts use BOARD_ROOT")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
