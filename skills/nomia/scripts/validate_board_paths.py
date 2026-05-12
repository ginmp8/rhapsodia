#!/usr/bin/env python3
"""Validate nomia canonical board artifact paths."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from nomia_utils import BOARD_ROOT_TEMPLATE, normalize_path, read_normalized_lines, resolve_board_root, unique

CANONICAL_PARTS = ("docs", "boards")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SPEC_ID_RE = re.compile(r"^spec\d{3}$")
SKILL_PACKAGE_DIRS = {"agents", "assets", "evals", "examples", "references", "scripts"}
SKILL_PACKAGE_FILES = {"SKILL.md", "skill.md"}
BOARD_SCOPED_ARTIFACTS = {
    "feature-map.yaml",
    "internal-notes.md",
    "portfolio.md",
    "portfolio.yaml",
    "release-notes.md",
    "rfc-proposals.md",
    "governance-decisions.md",
    "roadmap.md",
    "roadmap.yaml",
}
SPEC_SCOPED_ARTIFACTS = {
    "feature-report.md",
    "ops.yaml",
    "replanning.md",
    "stakeholder-brief.md",
    "status.md",
}
nomia_ARTIFACTS = BOARD_SCOPED_ARTIFACTS | SPEC_SCOPED_ARTIFACTS


def path_parts(path: str) -> list[str]:
    return [part for part in normalize_path(path).strip("/").lstrip("./").split("/") if part]


def has_skill_package_anchor(parts: list[str], skill_name: str) -> bool:
    for index, part in enumerate(parts):
        if part != skill_name:
            continue
        remainder = parts[index + 1 :]
        if not remainder:
            return True
        if remainder[0] in SKILL_PACKAGE_DIRS or remainder[0] in SKILL_PACKAGE_FILES:
            return True
    return False


def is_skill_package_path(path: str) -> bool:
    return has_skill_package_anchor(path_parts(path), "nomia")


def is_nomia_artifact(path: str) -> bool:
    return Path(path).name in nomia_ARTIFACTS


def is_under_canonical_root(parts: list[str]) -> bool:
    return len(parts) >= 2 and tuple(parts[:2]) == CANONICAL_PARTS


def validate_slug(label: str, value: str, errors: list[str]) -> None:
    if not value:
        errors.append(f"{label} is required")
    elif not SLUG_RE.match(value):
        errors.append(f"{label} `{value}` must be lowercase slug-safe")


def validate_spec_id(value: str, errors: list[str], path: str) -> None:
    if not SPEC_ID_RE.match(value):
        errors.append(f"{path}: spec_id `{value}` must use `specNNN` format")


def validate_path(path: str, expected_board_id: str | None, expected_cycle_version: str | None) -> list[str]:
    errors: list[str] = []
    if is_skill_package_path(path):
        return []

    parts = path_parts(path)
    under_root = is_under_canonical_root(parts)

    if not under_root and is_nomia_artifact(path):
        return [f"{path}: nomia artifact must be under {BOARD_ROOT_TEMPLATE}"]

    if not under_root:
        return []

    if len(parts) >= 4:
        board_id = parts[2]
        cycle_version = parts[3]
        validate_slug("board_id", board_id, errors)
        validate_slug("cycle_version", cycle_version, errors)
        if expected_board_id and board_id != expected_board_id:
            errors.append(f"{path}: board_id must be `{expected_board_id}`")
        if expected_cycle_version and cycle_version != expected_cycle_version:
            errors.append(f"{path}: cycle_version must be `{expected_cycle_version}`")

    if len(parts) == 5:
        artifact_name = parts[4]
        if artifact_name not in BOARD_SCOPED_ARTIFACTS:
            if artifact_name in SPEC_SCOPED_ARTIFACTS:
                errors.append(f"{path}: `{artifact_name}` must be under {BOARD_ROOT_TEMPLATE}specs/<spec_id>/")
            else:
                errors.append(f"{path}: artifact name is not nomia-owned")
        return errors

    if len(parts) == 7 and parts[4] == "specs":
        spec_id = parts[5]
        artifact_name = parts[6]
        validate_spec_id(spec_id, errors, path)
        if artifact_name not in SPEC_SCOPED_ARTIFACTS:
            if artifact_name in BOARD_SCOPED_ARTIFACTS:
                errors.append(f"{path}: `{artifact_name}` must be directly under {BOARD_ROOT_TEMPLATE}")
            else:
                errors.append(f"{path}: artifact name is not nomia-owned")
        return errors

    errors.append(
        f"{path}: expected {BOARD_ROOT_TEMPLATE}<board-artifact> or {BOARD_ROOT_TEMPLATE}specs/<spec_id>/<spec-artifact>"
    )
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=f"Validate nomia artifact paths under {BOARD_ROOT_TEMPLATE}."
    )
    parser.add_argument("paths", nargs="*", help="Changed paths or artifact paths to validate.")
    parser.add_argument("--changed-files", help="Newline-delimited file containing changed paths.")
    parser.add_argument("--board-root", help="Explicit BOARD_ROOT override. When omitted, use --board_id and --cycle_version if provided.")
    parser.add_argument("--board_id", help="Expected board_id slug.")
    parser.add_argument("--cycle_version", help="Expected cycle_version slug.")
    args = parser.parse_args(argv)

    paths = [normalize_path(path).lstrip("./") for path in args.paths]
    if args.changed_files:
        changed_files = Path(args.changed_files).resolve()
        if not changed_files.exists():
            print(f"ERROR: changed-files list does not exist: {changed_files}")
            print("FAILED: 1 errors, 0 warnings")
            return 1
        paths.extend(normalize_path(path).lstrip("./") for path in read_normalized_lines(changed_files))

    errors: list[str] = []
    if args.board_root:
        try:
            resolved_board_root = resolve_board_root(
                Path.cwd(),
                board_root_override=args.board_root,
                board_id=args.board_id,
                cycle_version=args.cycle_version,
            )
        except ValueError as exc:
            errors.append(str(exc))
        else:
            parts = [part for part in resolved_board_root.as_posix().split("/") if part]
            if len(parts) >= 2:
                args.board_id = parts[-2]
                args.cycle_version = parts[-1]
    if args.board_id:
        validate_slug("board_id", args.board_id, errors)
    if args.cycle_version:
        validate_slug("cycle_version", args.cycle_version, errors)

    if not paths:
        errors.append("provide at least one path or --changed-files")

    for path in paths:
        errors.extend(validate_path(path, args.board_id, args.cycle_version))

    errors = unique(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1

    print(f"OK: validated {len(paths)} paths")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
