#!/usr/bin/env python3
"""Validate MAGO board artifact placement and basic quality."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

from mago_utils import BOARD_ROOT_TEMPLATE, is_relative_to, posix_rel, read_yaml_file, resolve_board_root

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - validation still works without PyYAML
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from validate_package import validate_package  # type: ignore
except Exception:  # pragma: no cover - optional local companion script
    validate_package = None

SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SPEC_ID_RE = re.compile(r"^spec\d{3}$")

ROOT_ARTIFACTS = {
    "spec-catalog.yaml",
    "define-queue.yaml",
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
MAGO_ARTIFACTS = ROOT_ARTIFACTS | SPEC_ARTIFACTS
PLACEHOLDERS = (
    "<board_id>",
    "<cycle_version>",
    "<spec_id>",
    "<candidate_id>",
    "<discovery_root>",
)
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__"}


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
    if path.name in SPEC_ARTIFACTS:
        valid_spec_path = len(rel.parts) >= 3 and rel.parts[0] == "specs" and SPEC_ID_RE.fullmatch(rel.parts[1])
        if not valid_spec_path:
            errors.append(
                f"{posix_rel(path, repo_root)}: `{path.name}` must be under "
                f"`{posix_rel(board_root, repo_root)}/specs/specNNN/`"
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


def validate_define_queue(board_root: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    queue_path = board_root / "define-queue.yaml"
    if not queue_path.exists() or yaml is None:
        return errors

    try:
        data = read_yaml_file(queue_path, yaml) or {}
    except Exception as exc:
        return [f"{posix_rel(queue_path, repo_root)}: invalid YAML: {exc}"]

    entries = data.get("entries") if isinstance(data, dict) else None
    if entries is None:
        return errors
    if not isinstance(entries, list):
        return [f"{posix_rel(queue_path, repo_root)}: `entries` must be a list"]

    board_root_rel = posix_rel(board_root, repo_root)
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{posix_rel(queue_path, repo_root)}: entry {index} must be a mapping")
            continue
        spec_id = str(entry.get("spec_id", "")).strip()
        define_target = str(entry.get("define_target", "")).strip()
        if not SPEC_ID_RE.fullmatch(spec_id):
            errors.append(f"{posix_rel(queue_path, repo_root)}: entry {index} has invalid `spec_id`: `{spec_id}`")
            continue
        expected = f"{board_root_rel}/specs/{spec_id}/"
        if define_target != expected:
            errors.append(
                f"{posix_rel(queue_path, repo_root)}: entry {index} `define_target` must be `{expected}`"
            )
        for candidate_path in entry.get("source_candidates", []) or []:
            candidate_text = str(candidate_path).strip()
            expected_prefix = f"{board_root_rel}/candidates/"
            if not candidate_text.startswith(expected_prefix):
                errors.append(
                    f"{posix_rel(queue_path, repo_root)}: entry {index} source candidate "
                    f"`{candidate_text}` must be under `{expected_prefix}`"
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

    for spec_package_path in sorted(p for p in specs_root.iterdir() if p.is_dir()):
        if not SPEC_ID_RE.fullmatch(spec_package_path.name):
            errors.append(f"{posix_rel(spec_package_path, repo_root)}: spec directory must match `specNNN`")
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


def validate(
    repo_root: Path,
    board_id: str | None,
    cycle_version: str | None,
    board_root_override: str | None,
) -> tuple[list[str], list[str]]:
    repo_root = repo_root.resolve()
    try:
        canonical_root = resolve_board_root(
            repo_root,
            board_root_override=board_root_override,
            board_id=board_id,
            cycle_version=cycle_version,
        )
    except ValueError as exc:
        return [str(exc)], []

    errors: list[str] = []
    warnings: list[str] = []
    if board_root_override is None:
        assert board_id is not None
        assert cycle_version is not None
        errors.extend(validate_segment(board_id, "board_id"))
        errors.extend(validate_segment(cycle_version, "cycle_version"))

    if not repo_root.exists() or not repo_root.is_dir():
        errors.append(f"repo root does not exist or is not a directory: {repo_root}")
        return errors, warnings

    if not canonical_root.exists():
        errors.append(f"resolved BOARD_ROOT does not exist: {posix_rel(canonical_root, repo_root)}")
        return errors, warnings

    for path in iter_files(repo_root):
        if path.name in MAGO_ARTIFACTS:
            errors.extend(validate_root_artifact_location(path, repo_root, canonical_root))

    errors.extend(validate_placeholders(canonical_root, repo_root))
    errors.extend(validate_define_queue(canonical_root, repo_root))
    errors.extend(validate_discovery_index(canonical_root, repo_root))

    package_errors, package_warnings = validate_spec_packages(canonical_root, repo_root)
    errors.extend(package_errors)
    warnings.extend(package_warnings)

    return errors, warnings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=f"Validate MAGO artifact placement and quality under {BOARD_ROOT_TEMPLATE}."
    )
    parser.add_argument("repo_root", help="Repository root to validate.")
    parser.add_argument("--board-root", help="Explicit BOARD_ROOT override. When omitted, derive it from --board_id and --cycle_version.")
    parser.add_argument("--board_id", help="Required board segment under docs/boards/ when --board-root is omitted.")
    parser.add_argument("--cycle_version", help="Required cycle version segment when --board-root is omitted.")
    args = parser.parse_args(argv)

    if args.board_root is None and (not args.board_id or not args.cycle_version):
        parser.error("either --board-root or both --board_id and --cycle_version are required")

    errors, warnings = validate(Path(args.repo_root), args.board_id, args.cycle_version, args.board_root)

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
    sys.exit(main(sys.argv[1:]))
