"""Small shared helpers for MAGO validation and normalization scripts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

CANONICAL_BOARD_ROOT_TEMPLATE = "docs/boards/<board_id>/<cycle_version>/"
CANONICAL_SPEC_PACKAGE_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}specs/<spec_id>/"
BOARD_ROOT_TEMPLATE = CANONICAL_BOARD_ROOT_TEMPLATE
SPEC_PACKAGE_TEMPLATE = CANONICAL_SPEC_PACKAGE_TEMPLATE
SPEC_ID_RE = re.compile(r"^spec\d{3}$")
PLACEHOLDER_SEGMENTS = {"<board_id>", "<cycle_version>", "<spec_id>", "board_id", "cycle_version", "spec_id", "*"}


def board_root(repo_root: Path, board_id: str, cycle_version: str) -> Path:
    """Return the resolved BOARD_ROOT for concrete path segments."""
    return repo_root / "docs" / "boards" / board_id / cycle_version


def validate_concrete_segment(label: str, value: str | None) -> str | None:
    if not value or value in PLACEHOLDER_SEGMENTS or "<" in value or ">" in value:
        return f"{label} must be a concrete dynamic path segment, got `{value or '<empty>'}`."
    if "/" in value or "\\" in value:
        return f"{label} must be one path segment, got `{value}`."
    return None


def resolve_runtime_path(repo_root: Path, override: str | Path) -> Path:
    candidate = Path(override)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate.resolve()


def resolve_board_root(
    repo_root: Path,
    *,
    board_root_override: str | Path | None = None,
    board_id: str | None = None,
    cycle_version: str | None = None,
) -> Path:
    if board_root_override is not None:
        return resolve_runtime_path(repo_root, board_root_override)

    board_error = validate_concrete_segment("board_id", board_id)
    if board_error:
        raise ValueError(board_error)
    cycle_error = validate_concrete_segment("cycle_version", cycle_version)
    if cycle_error:
        raise ValueError(cycle_error)
    assert board_id is not None
    assert cycle_version is not None
    return board_root(repo_root, board_id, cycle_version)


def resolve_spec_package_path(
    repo_root: Path,
    *,
    board_root_override: str | Path | None = None,
    board_id: str | None = None,
    cycle_version: str | None = None,
    spec_id: str | None = None,
) -> Path:
    spec_error = validate_concrete_segment("spec_id", spec_id)
    if spec_error:
        raise ValueError(spec_error)
    if spec_id is None or not SPEC_ID_RE.fullmatch(spec_id):
        raise ValueError(f"spec_id must match `specNNN`, got `{spec_id or '<empty>'}`.")

    resolved_board_root = resolve_board_root(
        repo_root,
        board_root_override=board_root_override,
        board_id=board_id,
        cycle_version=cycle_version,
    )
    return resolved_board_root / "specs" / spec_id


def dedupe_preserve_order(messages: Iterable[str]) -> list[str]:
    """Return strings in first-seen order without duplicates."""
    seen: set[str] = set()
    result: list[str] = []
    for message in messages:
        if message in seen:
            continue
        seen.add(message)
        result.append(message)
    return result


def is_relative_to(path: Path, parent: Path) -> bool:
    """Compatibility wrapper for safe containment checks."""
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def posix_rel(path: Path, root: Path) -> str:
    """Return a stable repository-relative POSIX path for diagnostics."""
    return path.relative_to(root).as_posix()


def read_text_file(path: Path) -> str:
    """Read UTF-8 text from a path."""
    return path.read_text(encoding="utf-8")


def read_yaml_file(path: Path, yaml_module: Any) -> object:
    """Read YAML with the caller-provided yaml module."""
    if yaml_module is None:
        raise RuntimeError("PyYAML is not available")
    return yaml_module.safe_load(read_text_file(path))


def strip_quotes(value: str | None) -> str | None:
    """Trim whitespace and remove matching single or double quotes from a scalar."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    return text
