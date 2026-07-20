#!/usr/bin/env python3
"""Validate MAGO board placement, package quality, and concurrent identity rules."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

from mago_utils import (
    BOARD_ROOT_TEMPLATE,
    CANONICAL_CYCLE_KIND,
    CANONICAL_SPEC_KIND,
    SPEC_ID_RE,
    is_relative_to,
    posix_rel,
    read_yaml_file,
    resolve_board_root,
)
from validate_concurrent_board import validate as validate_cycle_board

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from validate_package import validate_package  # type: ignore
except Exception:  # pragma: no cover
    validate_package = None

SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ROOT_ARTIFACTS = {
    "cycle.yaml",
    "discovery-state.json",
    "discovery-index.yaml",
}
SPEC_ARTIFACTS = {
    "manifest.yaml",
    "prd.md",
    "technical-design.md",
    "tasks.md",
    "notes.md",
    "validation.md",
}
MAGO_ARTIFACTS = ROOT_ARTIFACTS | SPEC_ARTIFACTS | {"spec-catalog.yaml", "define-queue.yaml"}
PLACEHOLDERS = (
    "<board_id>",
    "<year>",
    "<cycle_id>",
    "<spec_id>",
    "<candidate_id>",
    "<discovery_root>",
)
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__"}
ACTIVE_CYCLE_STATUSES = {"proposed", "planned", "in_progress"}


def validate_segment(value: str, label: str) -> list[str]:
    errors: list[str] = []
    if value != value.strip():
        errors.append(f"{label}: must not contain leading or trailing whitespace")
    if not value:
        errors.append(f"{label}: is required")
        return errors
    if value in {".", ".."}:
        errors.append(f"{label}: must not be `.` or `..`")
    if "/" in value or "\\" in value:
        errors.append(f"{label}: must be one path segment, not a path")
    if ".." in value:
        errors.append(f"{label}: must not contain `..` traversal")
    if not SEGMENT_RE.fullmatch(value):
        errors.append(
            f"{label}: `{value}` is noncanonical; use lowercase letters, digits, dots, underscores, or hyphens"
        )
    return errors


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def validate_root_artifact_location(path: Path, repo_root: Path, board_root: Path) -> list[str]:
    errors: list[str] = []
    if not is_relative_to(path, board_root):
        errors.append(
            f"{posix_rel(path, repo_root)}: MAGO artifact is outside the resolved BOARD_ROOT "
            f"`{posix_rel(board_root, repo_root)}/`"
        )
        return errors

    rel = path.relative_to(board_root)
    if path.name in ROOT_ARTIFACTS and len(rel.parts) != 1:
        errors.append(
            f"{posix_rel(path, repo_root)}: `{path.name}` must be directly under the resolved BOARD_ROOT"
        )
    if path.name in {"spec-catalog.yaml", "define-queue.yaml"}:
        errors.append(
            f"{posix_rel(path, repo_root)}: generated aggregate views must be rendered outside BOARD_ROOT"
        )
    if path.name in SPEC_ARTIFACTS:
        valid_spec_path = len(rel.parts) >= 3 and rel.parts[0] == "specs" and SPEC_ID_RE.fullmatch(rel.parts[1])
        if not valid_spec_path:
            errors.append(
                f"{posix_rel(path, repo_root)}: `{path.name}` must be under "
                f"`{posix_rel(board_root, repo_root)}/specs/<canonical-spec-id>/`"
            )
    if len(rel.parts) == 2 and rel.parts[0] == "registry" and path.suffix in {".yaml", ".yml"}:
        expected_spec_id = path.stem
        if not SPEC_ID_RE.fullmatch(expected_spec_id):
            errors.append(
                f"{posix_rel(path, repo_root)}: registry filename must use canonical spec-YYYY-MM-DD-feature-key"
            )
    return errors


def validate_placeholders(board_root: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_files(board_root):
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                errors.append(f"{posix_rel(path, repo_root)}: unresolved placeholder `{placeholder}`")
    return errors



def validate_define_queue(
    board_root: Path,
    repo_root: Path,
    queue_path: Path | None = None,
) -> list[str]:
    """Validate a rendered define-queue view without making it canonical.

    The original MAGO validator exposed this surface for queue-shape and
    traceability checks. The canonical model now derives the queue from
    registry records, but the generated view remains inspectable and its
    paths must still resolve to the selected cycle.
    """
    errors: list[str] = []
    queue_path = queue_path or (board_root / "define-queue.yaml")
    if not queue_path.exists() or yaml is None:
        return errors

    try:
        data = read_yaml_file(queue_path, yaml) or {}
    except Exception as exc:
        return [f"{posix_rel(queue_path, repo_root)}: invalid YAML: {exc}"]

    if not isinstance(data, dict):
        return [f"{posix_rel(queue_path, repo_root)}: must be a mapping"]
    if data.get("kind") != "mago-define-queue":
        errors.append(f"{posix_rel(queue_path, repo_root)}: `kind` must be `mago-define-queue`")
    if data.get("generated") is not True:
        errors.append(f"{posix_rel(queue_path, repo_root)}: `generated` must be true")

    cycle_path = board_root / "cycle.yaml"
    if cycle_path.is_file():
        try:
            cycle = read_yaml_file(cycle_path, yaml) or {}
        except Exception:
            cycle = {}
        expected_cycle_id = str(cycle.get("cycle_id", "")).strip() if isinstance(cycle, dict) else ""
        if expected_cycle_id and str(data.get("cycle_id", "")).strip() != expected_cycle_id:
            errors.append(
                f"{posix_rel(queue_path, repo_root)}: `cycle_id` must match `{expected_cycle_id}`"
            )

    entries = data.get("entries")
    if not isinstance(entries, list):
        return errors + [f"{posix_rel(queue_path, repo_root)}: `entries` must be a list"]

    board_root_rel = posix_rel(board_root, repo_root)
    candidate_prefix = f"{board_root_rel}/candidates/"
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{posix_rel(queue_path, repo_root)}: entry {index} must be a mapping")
            continue
        spec_id = str(entry.get("spec_id", "")).strip()
        if not SPEC_ID_RE.fullmatch(spec_id):
            errors.append(f"{posix_rel(queue_path, repo_root)}: entry {index} has invalid `spec_id`: `{spec_id}`")
            continue
        define_target = str(entry.get("define_target", "")).strip()
        accepted_targets = {
            f"specs/{spec_id}/",
            f"{board_root_rel}/specs/{spec_id}/",
        }
        if define_target not in accepted_targets:
            errors.append(
                f"{posix_rel(queue_path, repo_root)}: entry {index} `define_target` must resolve to "
                f"`{board_root_rel}/specs/{spec_id}/`"
            )
        for candidate_path in entry.get("source_candidates", []) or []:
            candidate_text = str(candidate_path).strip()
            if candidate_text and not (
                candidate_text.startswith(candidate_prefix)
                or candidate_text.startswith("candidates/")
            ):
                errors.append(
                    f"{posix_rel(queue_path, repo_root)}: entry {index} source candidate "
                    f"`{candidate_text}` must resolve under `{candidate_prefix}`"
                )
    return errors

def validate_discovery_index(board_root: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    index_path = board_root / "discovery-index.yaml"
    if not index_path.exists() or yaml is None:
        return errors

    try:
        data = read_yaml_file(index_path, yaml) or {}
    except Exception as exc:
        return [f"{posix_rel(index_path, repo_root)}: invalid YAML: {exc}"]

    if not isinstance(data, dict):
        return [f"{posix_rel(index_path, repo_root)}: must be a mapping"]

    board_root_rel = posix_rel(board_root, repo_root)
    expected_discovery_root = f"{board_root_rel}/"
    if str(data.get("discovery_root", "")).strip() != expected_discovery_root:
        errors.append(
            f"{posix_rel(index_path, repo_root)}: `discovery_root` must be `{expected_discovery_root}`"
        )

    candidates = data.get("candidates") or []
    if not isinstance(candidates, list):
        return errors + [f"{posix_rel(index_path, repo_root)}: `candidates` must be a list"]

    expected_prefix = f"{board_root_rel}/candidates/"
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            errors.append(f"{posix_rel(index_path, repo_root)}: candidate {index} must be a mapping")
            continue
        candidate_doc = str(candidate.get("candidate_doc", "")).strip()
        if candidate_doc and not candidate_doc.startswith(expected_prefix):
            errors.append(
                f"{posix_rel(index_path, repo_root)}: candidate {index} `candidate_doc` must be under "
                f"`{expected_prefix}`"
            )
    return errors


def validate_spec_packages(board_root: Path, repo_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if validate_package is None:
        return errors, warnings

    specs_root = board_root / "specs"
    if not specs_root.is_dir():
        return errors, warnings

    for spec_package_path in sorted(path for path in specs_root.iterdir() if path.is_dir()):
        if not SPEC_ID_RE.fullmatch(spec_package_path.name):
            errors.append(
                f"{posix_rel(spec_package_path, repo_root)}: spec directory must use canonical spec-YYYY-MM-DD-feature-key"
            )
            continue
        technical_design_path = spec_package_path / "technical-design.md"
        if technical_design_path.exists():
            from validate_technical_design import validate as validate_technical_design

            errors.extend(validate_technical_design(technical_design_path))
        if not (spec_package_path / "tasks.md").exists():
            continue
        package_errors, package_warnings = validate_package(spec_package_path)
        errors.extend(package_errors)
        warnings.extend(package_warnings)
    return errors, warnings


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

    active_cycle_keys: dict[str, list[Path]] = {}

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

    def report_duplicates(label: str, values: dict[str, list[Path]]) -> None:
        for value, paths in sorted(values.items()):
            if len(paths) < 2:
                continue
            rendered = ", ".join(posix_rel(path, repo_root) for path in paths)
            errors.append(f"duplicate {label} `{value}` across sibling cycles: {rendered}")

    report_duplicates("active cycle_key", active_cycle_keys)
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

    errors: list[str] = []
    warnings: list[str] = []

    if board_root_override is None:
        assert board_id is not None
        assert cycle_id is not None
        errors.extend(validate_segment(board_id, "board_id"))
        if year is not None:
            errors.extend(validate_segment(str(year), "year"))

    if not repo_root.exists() or not repo_root.is_dir():
        errors.append(f"repo root does not exist or is not a directory: {repo_root}")
        return errors, warnings

    if not canonical_root.exists():
        try:
            rendered = posix_rel(canonical_root, repo_root)
        except ValueError:
            rendered = str(canonical_root)
        errors.append(f"resolved BOARD_ROOT does not exist: {rendered}")
        return errors, warnings

    for path in iter_files(repo_root):
        if path.name in MAGO_ARTIFACTS or (path.parent.name == "registry" and path.suffix in {".yaml", ".yml"}):
            errors.extend(validate_root_artifact_location(path, repo_root, canonical_root))

    errors.extend(validate_placeholders(canonical_root, repo_root))
    errors.extend(validate_discovery_index(canonical_root, repo_root))
    errors.extend(validate_define_queue(canonical_root, repo_root))

    concurrent_report = validate_cycle_board(canonical_root)
    errors.extend(concurrent_report.errors)
    warnings.extend(concurrent_report.warnings)

    package_errors, package_warnings = validate_spec_packages(canonical_root, repo_root)
    errors.extend(package_errors)
    warnings.extend(package_warnings)

    errors.extend(validate_repository_uniqueness(repo_root, canonical_root))
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Validate MAGO artifacts under {BOARD_ROOT_TEMPLATE}.")
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
