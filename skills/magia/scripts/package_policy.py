#!/usr/bin/env python3
"""Shared inclusion, exclusion, and sensitive-name policy for MAGIA packages."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    "htmlcov",
    "benchmark-reports",
    "test-results",
    "tmp",
    ".tmp",
}
EXCLUDED_FILE_NAMES = {".DS_Store", ".coverage", "coverage.xml", "test-results.json"}
SECRET_NAME_RE = re.compile(r"(secret|credential|private[_-]?key|\.env$|id_rsa|token)", re.IGNORECASE)


def exclusion_reason(rel_path: str) -> str | None:
    parts = Path(rel_path).parts
    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return "generated or blocked directory"
    name = parts[-1]
    if name in EXCLUDED_FILE_NAMES or name.startswith(".coverage.") or name.endswith(("~", ".swp", ".swo")):
        return "generated or temporary file"
    if name.endswith(".zip"):
        return "nested zip"
    return None


def is_sensitive_name(name: str) -> bool:
    return bool(SECRET_NAME_RE.search(name))


def iter_package_candidates(root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    candidates: list[Path] = []
    excluded: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not (path.is_file() or path.is_symlink()):
            continue
        relative = path.relative_to(root).as_posix()
        reason = exclusion_reason(relative)
        if reason:
            excluded.append({"path": relative, "reason": reason})
            continue
        candidates.append(path)
    return candidates, excluded


def blocked_zip_path(parts: Iterable[str]) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in parts)
