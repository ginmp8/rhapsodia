"""Small, dependency-free boundary helpers shared by the local graph commands."""
from __future__ import annotations
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

MAX_BYTES = 32 * 1024 * 1024
MAX_ITEMS = 100_000

def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def parse_json(text: str) -> Any:
    def invalid(value):
        raise ValueError("non-finite JSON number: " + value)
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid)

def read_json(path: Path, max_bytes: int = MAX_BYTES) -> Any:
    path = Path(path)
    if path.stat().st_size > max_bytes:
        raise ValueError(f"input exceeds byte limit {max_bytes}: {path.name}")
    return parse_json(path.read_text(encoding="utf-8-sig"))

def finite_tree(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise ValueError("data nesting exceeds 64 levels")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite number")
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise ValueError("JSON object keys must be strings")
        for child in value.values(): finite_tree(child, depth + 1)
    elif isinstance(value, list):
        if len(value) > MAX_ITEMS: raise ValueError("array exceeds item budget")
        for child in value: finite_tree(child, depth + 1)
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise ValueError("unsupported data value: " + type(value).__name__)

def safe_output(path: Path, inputs=()) -> Path:
    raw = Path(path).expanduser().absolute()
    if raw.is_symlink(): raise ValueError("output must not be a symbolic link")
    resolved = raw.resolve()
    for source in inputs:
        src = Path(source).expanduser().resolve()
        if resolved == src or (resolved.exists() and src.exists() and os.path.samefile(resolved, src)):
            raise ValueError("output aliases a protected input")
    if resolved.exists() and not resolved.is_file():
        raise ValueError("output is not a regular file")
    return resolved

def atomic_write(path: Path, payload: str | bytes, inputs=(), overwrite: bool = True) -> None:
    path = safe_output(path, inputs)
    if path.exists() and not overwrite: raise FileExistsError(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    data = payload.encode("utf-8") if isinstance(payload, str) else payload
    fd, temporary = tempfile.mkstemp(prefix=".graph-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data); out.flush(); os.fsync(out.fileno())
        if path.exists() and not overwrite: raise FileExistsError(str(path))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def write_json(path: Path, value: Any, inputs=(), overwrite: bool = True) -> None:
    finite_tree(value)
    atomic_write(path, json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", inputs, overwrite)

def integer(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low},{high}]")
    return value
