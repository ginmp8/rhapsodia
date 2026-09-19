from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

STATE_VERSION = "llm-wiki-state/1"
DEFAULT_SCHEMA_VERSION = "llm-wiki/2"
FRONTMATTER_ORDER = [
    "wiki_schema_version",
    "page_id",
    "page_type",
    "title",
    "canonical_key",
    "source_ids",
    "source_paths",
    "reviewed_source_ids",
    "conflict_ids",
    "status",
    "supersedes_page_ids",
    "source_date",
    "ingest_date",
    "created_date",
    "last_material_update",
    "updated_date",
]
LIST_FIELDS = {"source_ids", "source_paths", "reviewed_source_ids", "conflict_ids", "supersedes_page_ids"}
PAGE_TYPES = {"source", "entity", "concept", "synthesis"}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_id(prefix: str, payload: Any, length: int = 24) -> str:
    return f"{prefix}:{sha256_bytes(canonical_json_bytes(payload))[:length]}"


def normalize_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    return re.sub(r"\s+", " ", value)


def canonical_page_id(page_type: str, key: str) -> str:
    if page_type not in PAGE_TYPES:
        raise ValueError(f"unsupported page_type: {page_type}")
    if page_type == "source":
        if not key.startswith("sha256:") or len(key) != len("sha256:") + 64:
            raise ValueError("source page key must be a sha256:<64-hex> source_id")
        return f"source:{key.split(':', 1)[1]}"
    normalized = normalize_key(key)
    if not normalized:
        raise ValueError("canonical key must not be empty")
    return stable_id(page_type, {"key": normalized})


def ensure_within(root: Path, candidate: Path) -> Path:
    root = root.resolve(strict=True)
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes allowed root: {candidate}") from exc
    return resolved


def relative_posix(root: Path, path: Path) -> str:
    root = root.resolve(strict=True)
    path = path.resolve(strict=False)
    return path.relative_to(root).as_posix()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    lines = text[4:end].splitlines()
    data: dict[str, Any] = {}
    current_list: str | None = None
    for raw in lines:
        if not raw.strip():
            continue
        if raw.startswith("  - "):
            if current_list is None:
                raise ValueError("list item without field")
            item = raw[4:].strip()
            data[current_list].append(json.loads(item) if item.startswith(('"', "'")) else item)
            continue
        current_list = None
        if ":" not in raw:
            raise ValueError(f"invalid frontmatter line: {raw}")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_list = key
        else:
            try:
                data[key] = json.loads(value)
            except json.JSONDecodeError:
                data[key] = value
    return data, text[end + 5 :]


def render_frontmatter(metadata: dict[str, Any]) -> str:
    unknown = sorted(set(metadata) - set(FRONTMATTER_ORDER))
    if unknown:
        raise ValueError(f"unsupported frontmatter fields: {', '.join(unknown)}")
    lines = ["---"]
    for key in FRONTMATTER_ORDER:
        if key not in metadata or metadata[key] is None:
            continue
        value = metadata[key]
        if key in LIST_FIELDS:
            if not isinstance(value, list):
                raise ValueError(f"{key} must be a list")
            vals = sorted({str(v) for v in value})
            lines.append(f"{key}:")
            for item in vals:
                lines.append(f"  - {json.dumps(item, ensure_ascii=False)}")
        else:
            lines.append(f"{key}: {json.dumps(str(value), ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n"
