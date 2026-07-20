"""Shared, self-contained helpers for MAGIA board execution scripts."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType
from typing import Any

CANONICAL_DOCS_PREFIX = ("docs", "boards")
CANONICAL_BOARD_ROOT_TEMPLATE = "docs/boards/<board_id>/<year>/cycles/<cycle_id>/"
CANONICAL_SPEC_PACKAGE_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}specs/<spec_id>/"
CANONICAL_SPEC_REGISTRY_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}registry/<spec_id>.yaml"
BOARD_ROOT_TEMPLATE = CANONICAL_BOARD_ROOT_TEMPLATE
SPEC_PACKAGE_TEMPLATE = CANONICAL_SPEC_PACKAGE_TEMPLATE
SPEC_REGISTRY_TEMPLATE = CANONICAL_SPEC_REGISTRY_TEMPLATE

CYCLE_ID_RE = re.compile(
    r"^cycle-(?P<date>\d{4}-\d{2}-\d{2})-(?P<key>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
SPEC_ID_RE = re.compile(
    r"^spec-(?P<date>\d{4}-\d{2}-\d{2})-(?P<feature>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
TASK_ID_RE = re.compile(r"^task\d{3}$")
PLACEHOLDER_SEGMENTS = {
    "<board_id>", "<year>", "<cycle_id>", "<spec_id>",
    "board_id", "year", "cycle_id", "spec_id", "*",
}


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def dedupe_preserve_order(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def posix_rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def load_local_module(anchor_file: str | Path, script_name: str) -> ModuleType:
    script_path = Path(anchor_file).resolve().with_name(script_name)
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_path}")
    spec = importlib.util.spec_from_file_location(script_path.stem, str(script_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}")
    print(f"FAILED: {len(errors)} errors, 0 warnings")


def validate_concrete_segment(label: str, value: str | None) -> str | None:
    if not value or value in PLACEHOLDER_SEGMENTS or "<" in value or ">" in value:
        return f"{label} must be a concrete dynamic path segment, got `{value or '<empty>'}`."
    if value in {".", ".."} or "/" in value or "\\" in value or ".." in value:
        return f"{label} must be one safe path segment, got `{value}`."
    if value != value.strip():
        return f"{label} must not contain leading or trailing whitespace."
    return None


def parse_cycle_id(value: str) -> dict[str, str]:
    match = CYCLE_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"cycle_id must use cycle-YYYY-MM-DD-cycle-key, got `{value}`")
    return match.groupdict()


def parse_spec_id(value: str) -> dict[str, str]:
    match = SPEC_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"spec_id must use spec-YYYY-MM-DD-feature-key, got `{value}`")
    return match.groupdict()


def infer_year_from_cycle_id(cycle_id: str) -> str:
    return parse_cycle_id(cycle_id)["date"][:4]


def board_root(repo_root: Path, board_id: str, year: str | int, cycle_id: str) -> Path:
    return repo_root / "docs" / "boards" / board_id / str(year) / "cycles" / cycle_id


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
    year: str | int | None = None,
    cycle_id: str | None = None,
) -> Path:
    if board_root_override is not None:
        return resolve_runtime_path(repo_root, board_root_override)

    board_error = validate_concrete_segment("board_id", board_id)
    if board_error:
        raise ValueError(board_error)
    cycle_error = validate_concrete_segment("cycle_id", cycle_id)
    if cycle_error:
        raise ValueError(cycle_error)
    assert board_id is not None and cycle_id is not None
    parsed_year = infer_year_from_cycle_id(cycle_id)
    resolved_year = str(year) if year is not None else parsed_year
    if resolved_year != parsed_year:
        raise ValueError(f"year `{resolved_year}` conflicts with cycle_id creation year `{parsed_year}`")
    return board_root(repo_root, board_id, resolved_year, cycle_id)


def find_canonical_root_index(parts: tuple[str, ...]) -> int | None:
    for index in range(0, len(parts) - 1):
        if parts[index : index + 2] == CANONICAL_DOCS_PREFIX:
            return index
    return None


def board_root_path_error(path: Path) -> str | None:
    parts = path.resolve().parts
    index = find_canonical_root_index(parts)
    if index is None or len(parts) != index + 6:
        return f"board root must match `{CANONICAL_BOARD_ROOT_TEMPLATE}`."
    board_id, year, cycles_segment, cycle_id = parts[index + 2 : index + 6]
    if cycles_segment != "cycles":
        return f"board root must match `{CANONICAL_BOARD_ROOT_TEMPLATE}`."
    for label, value in (("board_id", board_id), ("year", year), ("cycle_id", cycle_id)):
        error = validate_concrete_segment(label, value)
        if error:
            return error
    try:
        inferred_year = infer_year_from_cycle_id(cycle_id)
    except ValueError as exc:
        return str(exc)
    if year != inferred_year:
        return f"year `{year}` conflicts with cycle_id creation year `{inferred_year}`."
    return None


def spec_package_path(board_root_path: Path, spec_id: str) -> Path:
    return board_root_path / "specs" / spec_id


def spec_registry_path(board_root_path: Path, spec_id: str) -> Path:
    return board_root_path / "registry" / f"{spec_id}.yaml"


def spec_package_path_error(spec_package: Path) -> str | None:
    parts = spec_package.resolve().parts
    index = find_canonical_root_index(parts)
    if index is None or len(parts) != index + 8:
        return f"spec package path must match `{CANONICAL_SPEC_PACKAGE_TEMPLATE}`."
    root = Path(*parts[: index + 6])
    root_error = board_root_path_error(root)
    if root_error:
        return root_error
    if parts[index + 6] != "specs":
        return f"spec package path must match `{CANONICAL_SPEC_PACKAGE_TEMPLATE}`."
    try:
        parse_spec_id(parts[index + 7])
    except ValueError as exc:
        return str(exc)
    return None


def resolve_spec_package_path(
    repo_root: Path,
    *,
    board_root_override: str | Path | None = None,
    board_id: str | None = None,
    year: str | int | None = None,
    cycle_id: str | None = None,
    spec_id: str | None = None,
) -> Path:
    if spec_id is None:
        raise ValueError("spec_id is required")
    parse_spec_id(spec_id)
    resolved_root = resolve_board_root(
        repo_root,
        board_root_override=board_root_override,
        board_id=board_id,
        year=year,
        cycle_id=cycle_id,
    )
    return spec_package_path(resolved_root, spec_id)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PyYAML is required") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML value must be a mapping")
    return data


def replace_top_level_scalar(lines: list[str], key: str, value: str) -> list[str]:
    prefix = f"{key}:"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{key}: {value}"
            return lines
    raise ValueError(f"missing top-level `{key}`")
