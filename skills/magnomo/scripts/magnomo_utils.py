#!/usr/bin/env python3
"""Shared helpers for Magnomo validation scripts."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


CANONICAL_BOARD_ROOT_TEMPLATE = "docs/boards/<board_id>/<cycle_version>/"
CANONICAL_SPEC_PACKAGE_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}specs/<spec_id>/"
BOARD_ROOT_TEMPLATE = CANONICAL_BOARD_ROOT_TEMPLATE
SPEC_PACKAGE_TEMPLATE = CANONICAL_SPEC_PACKAGE_TEMPLATE
TEMPLATE_TOKEN_RE = re.compile(r"<[^>\n]+>")


def compact_yaml_exception(exc: Exception) -> str:
    mark = getattr(exc, "problem_mark", None)
    problem = str(getattr(exc, "problem", exc)).replace("\n", " ")
    if mark is not None:
        return f"invalid YAML at line {mark.line + 1}, column {mark.column + 1}: {problem}"
    return problem


def load_yaml_mapping(path: Path, requirement: str = "PyYAML is required to validate Magnomo YAML artifacts.") -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError(requirement)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ValueError(compact_yaml_exception(exc)) from exc
    if not isinstance(data, dict):
        raise ValueError("top-level YAML value must be a mapping")
    return data


def normalize_path(raw_path: str) -> str:
    return raw_path.strip().replace("\\", "/")


def resolve_runtime_path(repo_root: Path, override: str | Path) -> Path:
    candidate = Path(str(override))
    if not candidate.is_absolute():
        candidate = repo_root / normalize_path(str(override))
    return candidate.resolve()


def board_root(repo_root: Path, board_id: str, cycle_version: str) -> Path:
    return repo_root / "docs" / "boards" / board_id / cycle_version


def resolve_board_root(
    repo_root: Path,
    *,
    board_root_override: str | Path | None = None,
    board_id: str | None = None,
    cycle_version: str | None = None,
) -> Path:
    if board_root_override is not None:
        return resolve_runtime_path(repo_root, board_root_override)
    if not board_id or not cycle_version:
        raise ValueError("board_id and cycle_version are required when BOARD_ROOT is not provided.")
    return board_root(repo_root, board_id, cycle_version)


def read_normalized_lines(path: Path) -> list[str]:
    return [normalize_path(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def unique(messages: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for message in messages:
        if message not in seen:
            seen.add(message)
            result.append(message)
    return result


def find_unresolved_template_tokens_in_text(text: str) -> list[str]:
    return sorted(set(TEMPLATE_TOKEN_RE.findall(text)))


def has_unresolved_template_token(value: Any) -> bool:
    return isinstance(value, str) and bool(TEMPLATE_TOKEN_RE.search(value))


def scan_unresolved_template_tokens(value: Any, prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            errors.extend(scan_unresolved_template_tokens(child, child_prefix))
        return errors
    if isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            errors.extend(scan_unresolved_template_tokens(child, child_prefix))
        return errors
    if isinstance(value, str):
        tokens = find_unresolved_template_tokens_in_text(value)
        if tokens:
            errors.append(
                f"`{prefix or '<root>'}` contains unresolved template token(s): {', '.join(tokens)}"
            )
    return errors


def is_missing(value: Any) -> bool:
    return value in (None, "", "unknown") or value == []


def is_iso_date(value: Any) -> bool:
    if value in (None, ""):
        return True
    if has_unresolved_template_token(value):
        return True
    if isinstance(value, date):
        return True
    try:
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def parse_iso_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if has_unresolved_template_token(value):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None
