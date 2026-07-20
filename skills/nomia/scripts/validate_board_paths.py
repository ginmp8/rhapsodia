#!/usr/bin/env python3
"""Validate nomia canonical board artifact paths."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from nomia_utils import (
    BOARD_ROOT_TEMPLATE,
    SPEC_ID_RE,
    YEAR_RE,
    infer_year_from_cycle_id,
    normalize_path,
    parse_canonical_board_root,
    parse_cycle_id,
    read_normalized_lines,
    resolve_board_root,
    unique,
)

CANONICAL_PARTS = ("docs", "boards")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
SKILL_PACKAGE_DIRS = {"agents", "assets", "evals", "examples", "references", "scripts", "tests"}
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
    elif not SLUG_RE.fullmatch(value):
        errors.append(f"{label} `{value}` must be lowercase slug-safe")


def validate_spec_id(value: str, errors: list[str], path: str) -> None:
    if not SPEC_ID_RE.fullmatch(value):
        errors.append(f"{path}: spec_id `{value}` must use spec-YYYY-MM-DD-feature-key--ULID format")


def validate_path(
    path: str,
    expected_board_id: str | None,
    expected_cycle_id: str | None,
    expected_year: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if is_skill_package_path(path):
        return []

    parts = path_parts(path)
    under_root = is_under_canonical_root(parts)

    if not under_root and is_nomia_artifact(path):
        return [f"{path}: nomia artifact must be under {BOARD_ROOT_TEMPLATE}"]
    if not under_root:
        return []

    if len(parts) < 7 or parts[4] != "cycles":
        return [f"{path}: expected canonical root {BOARD_ROOT_TEMPLATE}"]

    board_id, year, cycle_id = parts[2], parts[3], parts[5]
    validate_slug("board_id", board_id, errors)
    if not YEAR_RE.fullmatch(year):
        errors.append(f"{path}: year `{year}` must use YYYY format")
    try:
        parsed_year = infer_year_from_cycle_id(cycle_id)
    except ValueError as exc:
        errors.append(f"{path}: {exc}")
    else:
        if year != parsed_year:
            errors.append(f"{path}: year `{year}` conflicts with cycle_id creation year `{parsed_year}`")
    if expected_board_id and board_id != expected_board_id:
        errors.append(f"{path}: board_id must be `{expected_board_id}`")
    if expected_year and year != expected_year:
        errors.append(f"{path}: year must be `{expected_year}`")
    if expected_cycle_id and cycle_id != expected_cycle_id:
        errors.append(f"{path}: cycle_id must be `{expected_cycle_id}`")

    if len(parts) == 7:
        artifact_name = parts[6]
        if artifact_name not in BOARD_SCOPED_ARTIFACTS:
            if artifact_name in SPEC_SCOPED_ARTIFACTS:
                errors.append(f"{path}: `{artifact_name}` must be under {BOARD_ROOT_TEMPLATE}specs/<spec_id>/")
            else:
                errors.append(f"{path}: artifact name is not nomia-owned")
        return errors

    if len(parts) == 9 and parts[6] == "specs":
        spec_id = parts[7]
        artifact_name = parts[8]
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
    parser = argparse.ArgumentParser(description=f"Validate nomia artifact paths under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("paths", nargs="*", help="Changed paths or artifact paths to validate.")
    parser.add_argument("--changed-files", help="Newline-delimited file containing changed paths.")
    parser.add_argument("--board-root", help="Explicit BOARD_ROOT override. When omitted, use --board_id, --year, and --cycle_id.")
    parser.add_argument("--board_id", help="Expected board_id slug.")
    parser.add_argument("--year", help="Expected creation year in YYYY format.")
    parser.add_argument("--cycle_id", help="Expected immutable cycle_id.")
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
                year=args.year,
                cycle_id=args.cycle_id,
            )
            parsed = parse_canonical_board_root(resolved_board_root)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            for field in ("board_id", "year", "cycle_id"):
                supplied = getattr(args, field)
                if supplied and supplied != parsed[field]:
                    errors.append(f"{field} `{supplied}` conflicts with BOARD_ROOT `{parsed[field]}`")
                setattr(args, field, parsed[field])
    elif args.cycle_id:
        try:
            parsed_year = infer_year_from_cycle_id(args.cycle_id)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if args.year and args.year != parsed_year:
                errors.append(f"year `{args.year}` conflicts with cycle_id creation year `{parsed_year}`")
            args.year = args.year or parsed_year

    if args.board_id:
        validate_slug("board_id", args.board_id, errors)
    if args.year and not YEAR_RE.fullmatch(args.year):
        errors.append(f"year `{args.year}` must use YYYY format")
    if args.cycle_id:
        try:
            parse_cycle_id(args.cycle_id)
        except ValueError as exc:
            errors.append(str(exc))

    if not paths:
        errors.append("provide at least one path or --changed-files")

    for path in paths:
        errors.extend(validate_path(path, args.board_id, args.cycle_id, args.year))

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
