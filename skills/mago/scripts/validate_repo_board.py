#!/usr/bin/env python3
"""Validate one canonical MAGO board root and sibling identity uniqueness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mago_utils import (
    BOARD_ROOT_TEMPLATE,
    CANONICAL_CYCLE_KIND,
    CANONICAL_SPEC_KIND,
    posix_rel,
    read_yaml_file,
    resolve_board_root,
)
from validate_concurrent_board import validate as validate_cycle_board

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

ACTIVE_CYCLE_STATUSES = {"proposed", "planned", "in_progress"}


def validate_repository_uniqueness(repo_root: Path, board_root: Path) -> list[str]:
    """Detect merge-time identity conflicts across sibling cycles."""
    if yaml is None:
        return ["PyYAML is required for repository uniqueness validation"]

    errors: list[str] = []
    try:
        cycles_root = board_root.parent
        year = board_root.parent.parent.name
        board_id = board_root.parent.parent.parent.name
        expected_root = repo_root / "docs" / "boards" / board_id / year / "cycles"
        if cycles_root.resolve() != expected_root.resolve():
            return [
                f"{posix_rel(board_root, repo_root)}: canonical root must live under "
                f"`{posix_rel(expected_root, repo_root)}/`"
            ]
    except (ValueError, IndexError):
        return [f"{board_root}: cannot derive canonical board/year scope for uniqueness validation"]

    cycle_uids: dict[str, list[Path]] = {}
    active_cycle_keys: dict[str, list[Path]] = {}
    spec_uids: dict[str, list[Path]] = {}

    for cycle_dir in sorted(path for path in cycles_root.iterdir() if path.is_dir()):
        cycle_path = cycle_dir / "cycle.yaml"
        if not cycle_path.is_file():
            continue
        try:
            cycle = read_yaml_file(cycle_path, yaml) or {}
        except Exception as exc:
            errors.append(f"{posix_rel(cycle_path, repo_root)}: invalid YAML during uniqueness scan: {exc}")
            continue
        if not isinstance(cycle, dict) or cycle.get("kind") != CANONICAL_CYCLE_KIND:
            errors.append(f"{posix_rel(cycle_path, repo_root)}: invalid canonical cycle metadata")
            continue

        cycle_uid = str(cycle.get("cycle_uid", "")).strip()
        if cycle_uid:
            cycle_uids.setdefault(cycle_uid, []).append(cycle_path)
        cycle_key = str(cycle.get("cycle_key", "")).strip()
        if cycle_key and cycle.get("status") in ACTIVE_CYCLE_STATUSES:
            active_cycle_keys.setdefault(cycle_key, []).append(cycle_path)

        registry_root = cycle_dir / "registry"
        if not registry_root.is_dir():
            continue
        for registry_path in sorted(registry_root.glob("*.yaml")):
            try:
                record = read_yaml_file(registry_path, yaml) or {}
            except Exception as exc:
                errors.append(f"{posix_rel(registry_path, repo_root)}: invalid YAML during uniqueness scan: {exc}")
                continue
            if not isinstance(record, dict) or record.get("kind") != CANONICAL_SPEC_KIND:
                errors.append(f"{posix_rel(registry_path, repo_root)}: invalid canonical registry metadata")
                continue
            spec_uid = str(record.get("spec_uid", "")).strip()
            if spec_uid:
                spec_uids.setdefault(spec_uid, []).append(registry_path)

    def report_duplicates(label: str, values: dict[str, list[Path]]) -> None:
        for value, paths in sorted(values.items()):
            if len(paths) < 2:
                continue
            rendered = ", ".join(posix_rel(path, repo_root) for path in paths)
            errors.append(f"duplicate {label} `{value}` across sibling cycles: {rendered}")

    report_duplicates("cycle_uid", cycle_uids)
    report_duplicates("active cycle_key", active_cycle_keys)
    report_duplicates("spec_uid", spec_uids)
    return errors


def validate(
    repo_root: Path,
    board_id: str | None = None,
    board_root_override: str | None = None,
    *,
    year: str | None = None,
    cycle_id: str | None = None,
) -> tuple[list[str], list[str]]:
    repo_root = repo_root.resolve()
    try:
        canonical_root = resolve_board_root(
            repo_root,
            board_root_override=board_root_override,
            board_id=board_id,
            year=year,
            cycle_id=cycle_id,
        )
    except ValueError as exc:
        return [str(exc)], []

    if not repo_root.is_dir():
        return [f"repo root does not exist or is not a directory: {repo_root}"], []
    if not canonical_root.is_dir():
        try:
            rendered = posix_rel(canonical_root, repo_root)
        except ValueError:
            rendered = str(canonical_root)
        return [f"resolved BOARD_ROOT does not exist: {rendered}"], []

    report = validate_cycle_board(canonical_root)
    errors = list(report.errors)
    warnings = list(report.warnings)
    errors.extend(validate_repository_uniqueness(repo_root, canonical_root))
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Validate canonical MAGO artifacts under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("repo_root", help="Repository root to validate.")
    parser.add_argument("--board-root", help="Explicit canonical BOARD_ROOT override.")
    parser.add_argument("--board-id", "--board_id", dest="board_id", help="Board path segment when deriving a root.")
    parser.add_argument("--year", help="Creation year; inferred from --cycle-id when omitted.")
    parser.add_argument("--cycle-id", dest="cycle_id", help="Immutable cycle identity.")
    args = parser.parse_args(argv)

    if args.board_root is None and (not args.board_id or not args.cycle_id):
        parser.error("provide --board-root or both --board-id and --cycle-id")

    errors, warnings = validate(
        Path(args.repo_root),
        args.board_id,
        args.board_root,
        year=args.year,
        cycle_id=args.cycle_id,
    )

    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print(f"FAILED: {len(errors)} errors, {len(warnings)} warnings")
        return 1
    if warnings:
        print(f"OK: board validated with {len(warnings)} warning(s)")
    else:
        print("OK: board validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
