"""Shared helpers for MAGIA scripts.

Import-only by design; no `if __name__ == "__main__"` entrypoint.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType

CANONICAL_DOCS_PREFIX = ("docs", "boards")
CANONICAL_BOARD_ROOT_TEMPLATE = "docs/boards/<board_id>/<cycle_version>/"
CANONICAL_SPEC_PACKAGE_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}specs/specNNN"
BOARD_ROOT_TEMPLATE = CANONICAL_BOARD_ROOT_TEMPLATE
SPEC_PACKAGE_TEMPLATE = CANONICAL_SPEC_PACKAGE_TEMPLATE
SPEC_ID_RE = re.compile(r"^spec\d{3}$")
PLACEHOLDER_SEGMENTS = {"<board_id>", "<cycle_version>", "board_id", "cycle_version", "*"}


def spec_package_path(board_root: Path, spec_id: str) -> Path:
    return board_root / "specs" / spec_id


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


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


def find_canonical_root_index(parts: tuple[str, ...]) -> int | None:
    for index in range(0, len(parts) - 1):
        if parts[index : index + 2] == CANONICAL_DOCS_PREFIX:
            return index
    return None


def validate_concrete_segment(label: str, value: str) -> str | None:
    if not value or value in PLACEHOLDER_SEGMENTS or "<" in value or ">" in value:
        return f"{label} must be a concrete dynamic path segment, got `{value or '<empty>'}`."
    if "/" in value or "\\" in value:
        return f"{label} must be one path segment, got `{value}`."
    return None


def canonical_spec_package_error(spec_package_path: Path) -> str | None:
    parts = spec_package_path.resolve().parts
    index = find_canonical_root_index(parts)
    if index is None:
        return f"spec package path must be under `{CANONICAL_SPEC_PACKAGE_TEMPLATE}`."
    if len(parts) <= index + 5:
        return "spec package path must include `<board_id>`, `<cycle_version>`, `specs`, and specNNN."

    board_id = parts[index + 2]
    cycle_version = parts[index + 3]
    specs_segment = parts[index + 4]
    spec_id = parts[index + 5]

    for label, value in (("board_id", board_id), ("cycle_version", cycle_version)):
        error = validate_concrete_segment(label, value)
        if error:
            return error

    if specs_segment != "specs" or not SPEC_ID_RE.match(spec_id):
        return "spec package path must end with `specs/specNNN` under `BOARD_ROOT`."
    if len(parts) != index + 6:
        return f"spec package path must point directly to `{CANONICAL_SPEC_PACKAGE_TEMPLATE}`, not a nested child path."
    return None


def spec_package_path_error(spec_package_path: Path) -> str | None:
    return canonical_spec_package_error(spec_package_path)


def board_root(repo_root: Path, board_id: str, cycle_version: str) -> Path:
    return repo_root / "docs" / "boards" / board_id / cycle_version


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

    board_error = validate_concrete_segment("board_id", board_id or "")
    if board_error:
        raise ValueError(board_error)
    cycle_error = validate_concrete_segment("cycle_version", cycle_version or "")
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
    spec_error = validate_concrete_segment("spec_id", spec_id or "")
    if spec_error:
        raise ValueError(spec_error)
    if spec_id is None or not SPEC_ID_RE.match(spec_id):
        raise ValueError(f"spec_id must match specNNN, got `{spec_id or '<empty>'}`.")

    resolved_board_root = resolve_board_root(
        repo_root,
        board_root_override=board_root_override,
        board_id=board_id,
        cycle_version=cycle_version,
    )
    return spec_package_path(resolved_board_root, spec_id)
