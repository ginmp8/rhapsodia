"""Shared MAGO canonical path, identity, and YAML helpers."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

CANONICAL_CYCLE_KIND = "mago-cycle"
CANONICAL_SPEC_KIND = "mago-spec"
CANONICAL_CATALOG_KIND = "mago-spec-catalog"
CANONICAL_QUEUE_KIND = "mago-define-queue"
CANONICAL_BOARD_ROOT_TEMPLATE = "docs/boards/<board_id>/<year>/cycles/<cycle_id>/"
CANONICAL_SPEC_PACKAGE_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}specs/<spec_id>/"
CANONICAL_SPEC_REGISTRY_TEMPLATE = f"{CANONICAL_BOARD_ROOT_TEMPLATE}registry/<spec_id>.yaml"
BOARD_ROOT_TEMPLATE = CANONICAL_BOARD_ROOT_TEMPLATE
SPEC_PACKAGE_TEMPLATE = CANONICAL_SPEC_PACKAGE_TEMPLATE

ULID_ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
ULID_RE = re.compile(r"^[0-9a-hjkmnp-tv-z]{26}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CYCLE_ID_RE = re.compile(
    r"^cycle-(?P<date>\d{4}-\d{2}-\d{2})-(?P<key>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
SPEC_ID_RE = re.compile(
    r"^spec-(?P<date>\d{4}-\d{2}-\d{2})-(?P<feature>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
LEGACY_CYCLE_ID_RE = re.compile(
    r"^(?:cycle-)?(?P<date>\d{4}-\d{2}-\d{2})-(?P<key>[a-z0-9]+(?:-[a-z0-9]+)*)--(?P<ulid>[0-9a-hjkmnp-tv-z]{26})$"
)
LEGACY_SPEC_ID_RE = re.compile(
    r"^spec-(?P<date>\d{4}-\d{2}-\d{2})-(?P<feature>[a-z0-9]+(?:-[a-z0-9]+)*)--(?P<ulid>[0-9a-hjkmnp-tv-z]{26})$"
)
SEMVER_RE = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9a-z.-]+)?(?:\+[0-9a-z.-]+)?$")
PLACEHOLDER_SEGMENTS = {
    "<board_id>", "<year>", "<cycle_id>", "<spec_id>",
    "board_id", "year", "cycle_id", "spec_id", "*",
}


def slugify(value: str) -> str:
    text = value.strip().lower().replace("_", " ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not text or not SLUG_RE.fullmatch(text):
        raise ValueError(f"value cannot be converted to a safe lowercase kebab-case slug: {value!r}")
    return text


def new_ulid(timestamp_ms: int | None = None, entropy: bytes | None = None) -> str:
    """Reject retired ULID generation while preserving the former public helper symbol."""
    del timestamp_ms, entropy
    raise ValueError("ULID generation is retired; canonical MAGO identities have no automatic suffix")


def validate_iso_date(value: str) -> date:
    if not DATE_RE.fullmatch(value):
        raise ValueError(f"date must use YYYY-MM-DD, got {value!r}")
    return date.fromisoformat(value)


def parse_utc_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp is required")
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"timestamp must use ISO-8601 with timezone, got {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp must include a timezone, got {value!r}")
    return parsed.astimezone(timezone.utc)


def normalize_utc_timestamp(value: str) -> str:
    return parse_utc_timestamp(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_cycle_id(cycle_key: str, created_date: str | None = None, ulid: str | None = None) -> str:
    day = validate_iso_date(created_date or datetime.now(timezone.utc).date().isoformat()).isoformat()
    key = slugify(cycle_key)
    if ulid is not None:
        raise ValueError("ULID suffixes are not valid in canonical cycle_id values")
    return f"cycle-{day}-{key}"


def make_spec_id(feature_key: str, created_date: str | None = None, ulid: str | None = None) -> str:
    day = validate_iso_date(created_date or datetime.now(timezone.utc).date().isoformat()).isoformat()
    feature = slugify(feature_key)
    if ulid is not None:
        raise ValueError("ULID suffixes are not valid in canonical spec_id values")
    return f"spec-{day}-{feature}"


def parse_cycle_id(value: str) -> dict[str, str]:
    match = CYCLE_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"cycle_id has invalid canonical format: {value!r}")
    validate_iso_date(match.group("date"))
    return match.groupdict()


def parse_spec_id(value: str) -> dict[str, str]:
    match = SPEC_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"spec_id has invalid canonical format: {value!r}")
    validate_iso_date(match.group("date"))
    return match.groupdict()


def parse_legacy_cycle_id(value: str) -> dict[str, str]:
    match = LEGACY_CYCLE_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"legacy cycle_id has invalid read-only adapt format: {value!r}")
    validate_iso_date(match.group("date"))
    return match.groupdict()


def parse_legacy_spec_id(value: str) -> dict[str, str]:
    match = LEGACY_SPEC_ID_RE.fullmatch(value)
    if not match:
        raise ValueError(f"legacy spec_id has invalid read-only adapt format: {value!r}")
    validate_iso_date(match.group("date"))
    return match.groupdict()


def validate_spec_id(value: str) -> str | None:
    try:
        parse_spec_id(value)
        return None
    except ValueError:
        return f"spec_id must use spec-YYYY-MM-DD-feature-key, got `{value}`"


def board_root(repo_root: Path, board_id: str, year: str | int, cycle_id: str) -> Path:
    return repo_root / "docs" / "boards" / board_id / str(year) / "cycles" / cycle_id


def validate_concrete_segment(label: str, value: str | None) -> str | None:
    if not value or value in PLACEHOLDER_SEGMENTS or "<" in value or ">" in value:
        return f"{label} must be a concrete dynamic path segment, got `{value or '<empty>'}`."
    if "/" in value or "\\" in value or value in {".", ".."} or ".." in value:
        return f"{label} must be one safe path segment, got `{value}`."
    return None


def resolve_runtime_path(repo_root: Path, override: str | Path) -> Path:
    candidate = Path(override)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate.resolve()


def infer_year_from_cycle_id(cycle_id: str) -> str:
    return parse_cycle_id(cycle_id)["date"][:4]


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
    spec_error = validate_spec_id(spec_id)
    if spec_error:
        raise ValueError(spec_error)
    resolved_board_root = resolve_board_root(
        repo_root,
        board_root_override=board_root_override,
        board_id=board_id,
        year=year,
        cycle_id=cycle_id,
    )
    return resolved_board_root / "specs" / spec_id


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, 0o644)
        os.link(temporary_path, path)
    except Exception:
        raise
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def canonical_yaml_digest(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.name):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def dedupe_preserve_order(messages: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for message in messages:
        if message in seen:
            continue
        seen.add(message)
        result.append(message)
    return result


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def posix_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_yaml_file(path: Path, yaml_module: Any) -> object:
    if yaml_module is None:
        raise RuntimeError("PyYAML is not available")
    return yaml_module.safe_load(read_text_file(path))


def strip_quotes(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    return text
