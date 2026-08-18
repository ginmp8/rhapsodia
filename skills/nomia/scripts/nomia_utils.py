#!/usr/bin/env python3
"""Shared helpers for nomia validation scripts."""

from __future__ import annotations

import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


CANONICAL_BOARD_ROOT_TEMPLATE = "docs/boards/<board_id>/<year>/cycles/<cycle_id>/"
CANONICAL_SPEC_PACKAGE_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}specs/<spec_id>/"
CANONICAL_SPEC_REGISTRY_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}registry/<spec_id>.yaml"
BOARD_ROOT_TEMPLATE = CANONICAL_BOARD_ROOT_TEMPLATE
SPEC_PACKAGE_TEMPLATE = CANONICAL_SPEC_PACKAGE_TEMPLATE
TEMPLATE_TOKEN_RE = re.compile(r"<[^>\n]+>")

SENSITIVE_FILE_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "id_rsa",
    "id_ed25519",
}
SENSITIVE_FILE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"}
PRIVATE_KEY_HEADERS = tuple(
    f"-----BEGIN {kind}-----".encode("ascii")
    for kind in (
        "PRIVATE KEY",
        "ENCRYPTED PRIVATE KEY",
        "RSA PRIVATE KEY",
        "EC PRIVATE KEY",
        "OPENSSH PRIVATE KEY",
    )
)


def sensitive_package_reason(path: Path) -> str | None:
    """Return a high-confidence package-security violation for a path."""
    name = path.name.lower()
    if path.is_symlink():
        return "symlink is not allowed in a skill package"
    if name == ".env" or name.startswith(".env.") or name in SENSITIVE_FILE_NAMES:
        return "sensitive credential or environment file is not allowed"
    if path.suffix.lower() in SENSITIVE_FILE_SUFFIXES:
        return "private key or credential container is not allowed"
    if path.is_file():
        try:
            if path.stat().st_size <= 2_000_000:
                sample = path.read_bytes()
                if any(header in sample for header in PRIVATE_KEY_HEADERS):
                    return "private key material is not allowed"
        except OSError as exc:
            return f"file cannot be safely inspected: {exc}"
    return None
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
YEAR_RE = re.compile(r"^\d{4}$")
CYCLE_ID_RE = re.compile(
    r"^cycle-(?P<date>\d{4}-\d{2}-\d{2})-(?P<cycle_key>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
SPEC_ID_RE = re.compile(
    r"^spec-(?P<date>\d{4}-\d{2}-\d{2})-(?P<feature_key>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
# Read-only recognition for governance-adapt input. These patterns are never
# accepted by canonical writers, path validators, or normal operational modes.
LEGACY_CYCLE_ID_RE = re.compile(
    r"^(?:cycle-)?(?P<date>\d{4}-\d{2}-\d{2})-(?P<cycle_key>[a-z0-9]+(?:-[a-z0-9]+)*)--(?P<ulid>[0-9a-hjkmnp-tv-z]{26})$"
)
LEGACY_SPEC_ID_RE = re.compile(
    r"^spec-(?P<date>\d{4}-\d{2}-\d{2})-(?P<feature_key>[a-z0-9]+(?:-[a-z0-9]+)*)--(?P<ulid>[0-9a-hjkmnp-tv-z]{26})$"
)




def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """Write text atomically in the destination directory and avoid partial artifacts."""
    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

def compact_yaml_exception(exc: Exception) -> str:
    mark = getattr(exc, "problem_mark", None)
    problem = str(getattr(exc, "problem", exc)).replace("\n", " ")
    if mark is not None:
        return f"invalid YAML at line {mark.line + 1}, column {mark.column + 1}: {problem}"
    return problem


def load_yaml_mapping(path: Path, requirement: str = "PyYAML is required to validate nomia YAML artifacts.") -> dict[str, Any]:
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


def parse_cycle_id(value: str) -> dict[str, str]:
    match = CYCLE_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"cycle_id has invalid canonical format: {value!r}")
    parsed = match.groupdict()
    if date.fromisoformat(parsed["date"]).isoformat() != parsed["date"]:
        raise ValueError(f"cycle_id has invalid date: {value!r}")
    return parsed


def parse_spec_id(value: str) -> dict[str, str]:
    match = SPEC_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"spec_id has invalid canonical format: {value!r}")
    parsed = match.groupdict()
    if date.fromisoformat(parsed["date"]).isoformat() != parsed["date"]:
        raise ValueError(f"spec_id has invalid date: {value!r}")
    return parsed


def validate_spec_id_format(value: Any) -> str | None:
    if value in (None, "") or has_unresolved_template_token(value):
        return None
    try:
        parse_spec_id(str(value))
    except ValueError:
        return "spec_id must use spec-YYYY-MM-DD-feature-key"
    return None


def validate_cycle_id_format(value: Any) -> str | None:
    if value in (None, "") or has_unresolved_template_token(value):
        return None
    try:
        parse_cycle_id(str(value))
    except ValueError:
        return "cycle_id must use cycle-YYYY-MM-DD-cycle-key"
    return None


def is_legacy_cycle_id(value: Any) -> bool:
    """Return whether value matches the former ULID cycle id for read-only adaptation."""
    return isinstance(value, str) and LEGACY_CYCLE_ID_RE.fullmatch(value) is not None


def is_legacy_spec_id(value: Any) -> bool:
    """Return whether value matches the former ULID spec id for read-only adaptation."""
    return isinstance(value, str) and LEGACY_SPEC_ID_RE.fullmatch(value) is not None


def validate_id_provenance(value: Any, *, id_value: Any, field_name: str) -> str | None:
    """Require explicit evidence provenance whenever an externally supplied id is present."""
    if id_value in (None, "") or has_unresolved_template_token(id_value):
        return None
    if has_unresolved_template_token(value):
        return None
    if not isinstance(value, str) or not value.strip() or value.strip() == "unknown":
        return f"{field_name} must be a non-empty evidence reference when the id is provided"
    return None


def infer_year_from_cycle_id(cycle_id: str) -> str:
    return parse_cycle_id(cycle_id)["date"][:4]


def board_root(repo_root: Path, board_id: str, year: str | int, cycle_id: str) -> Path:
    return repo_root / "docs" / "boards" / board_id / str(year) / "cycles" / cycle_id


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
    if not board_id or not cycle_id:
        raise ValueError("board_id and cycle_id are required when BOARD_ROOT is not provided.")
    if not SLUG_RE.fullmatch(board_id):
        raise ValueError(f"board_id `{board_id}` must be lowercase slug-safe")
    parsed_year = infer_year_from_cycle_id(cycle_id)
    resolved_year = str(year) if year is not None else parsed_year
    if not YEAR_RE.fullmatch(resolved_year):
        raise ValueError(f"year `{resolved_year}` must use YYYY format")
    if resolved_year != parsed_year:
        raise ValueError(f"year `{resolved_year}` conflicts with cycle_id creation year `{parsed_year}`")
    return board_root(repo_root, board_id, resolved_year, cycle_id)


def parse_canonical_board_root(path: str | Path) -> dict[str, str]:
    parts = [part for part in normalize_path(str(path)).strip("/").split("/") if part]
    for index in range(max(0, len(parts) - 5)):
        if parts[index:index + 2] != ["docs", "boards"]:
            continue
        if index + 5 >= len(parts) or parts[index + 4] != "cycles":
            continue
        board_id, year, cycle_id = parts[index + 2], parts[index + 3], parts[index + 5]
        if not SLUG_RE.fullmatch(board_id):
            raise ValueError(f"board_id `{board_id}` must be lowercase slug-safe")
        if not YEAR_RE.fullmatch(year):
            raise ValueError(f"year `{year}` must use YYYY format")
        parsed_year = infer_year_from_cycle_id(cycle_id)
        if year != parsed_year:
            raise ValueError(f"year `{year}` conflicts with cycle_id creation year `{parsed_year}`")
        return {"board_id": board_id, "year": year, "cycle_id": cycle_id}
    raise ValueError(f"BOARD_ROOT must match {CANONICAL_BOARD_ROOT_TEMPLATE}")


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


def main() -> int:
    """Document the import-only contract for generic package auditors."""
    print("nomia_utils.py is an import-only helper for nomia validators and scaffold scripts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
