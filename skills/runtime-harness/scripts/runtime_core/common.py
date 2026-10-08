"""Bounded data and filesystem primitives shared by the local runtime."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

MAX_INPUT = 65536
MAX_STATE = 4 * 1024 * 1024
MAX_RESOURCE = 8 * 1024 * 1024
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,95}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
PRIVATE_PARTS = {".git", ".ssh", ".aws", ".azure", ".kube", ".gnupg", ".npmrc", ".pypirc"}
PUBLIC_ENV = {".env.example", ".env.sample", ".env.template"}


class RuntimeFault(Exception):
    def __init__(self, code: str, message: str, exit_code: int = 2):
        super().__init__(message)
        self.code, self.exit_code = code, exit_code

    def result(self) -> dict:
        return {"status": "error", "error": {"code": self.code, "message": str(self)}}


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(data: bytes, limit: int = MAX_INPUT) -> object:
    if len(data) > limit:
        raise RuntimeFault("INPUT_TOO_LARGE", "Input exceeds the bounded JSON size.")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError("non-finite JSON number")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)
        canonical(value)  # Reject escaped lone surrogates and numeric overflow too.
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise RuntimeFault("INVALID_INPUT", "Expected finite UTF-8 JSON with unique object keys.") from exc


def fields(value, required: set[str], optional: set[str] | None = None) -> dict:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - (optional or set()):
        raise RuntimeFault("INVALID_INPUT", "Missing or unsupported contract fields.")
    return value


def number(value, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise RuntimeFault("INVALID_INPUT", f"Expected an integer in {minimum}..{maximum}.")
    return value


def safe_text(value, limit: int = 200) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > limit or any(ord(c) < 32 for c in value):
        raise RuntimeFault("INVALID_INPUT", "Expected bounded nonempty single-line text.")
    return value


def relative_parts(value: str) -> list[str]:
    if not isinstance(value, str) or not value or any(c in value for c in "\\:%?#\x00") or any(ord(c) < 32 for c in value):
        raise RuntimeFault("UNSAFE_PATH", "Only canonical local relative resource paths are allowed.")
    parts = value.split("/")
    for part in parts:
        low = part.casefold()
        if part in ("", ".", "..") or low in PRIVATE_PARTS or low.endswith((".pem", ".key")):
            raise RuntimeFault("UNSAFE_PATH", "Protected or ambiguous path component.")
        if low.startswith(".env") and low not in PUBLIC_ENV:
            raise RuntimeFault("UNSAFE_PATH", "Private environment files are not runtime resources.")
        if part.endswith((" ", ".")) or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part):
            raise RuntimeFault("UNSAFE_PATH", "Nonportable filesystem component.")
    return parts


def confined(root: Path, relative: str, *, write: bool = False) -> Path:
    """The explicitly selected root is canonical; descendants may not redirect."""
    parts = relative_parts(relative)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise RuntimeFault("UNSAFE_PATH", "Symbolic links are not allowed in the selected resource path.")
        if current.exists():
            info = current.stat()
            if not stat.S_ISDIR(info.st_mode) and not stat.S_ISREG(info.st_mode):
                raise RuntimeFault("UNSAFE_PATH", "Special filesystem objects are not supported.")
            if write and stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
                raise RuntimeFault("UNSAFE_PATH", "Refusing to replace a hard-linked file.")
    try:
        current.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeFault("UNSAFE_PATH", "Resource escapes the approved root.") from exc
    return current


def read_bytes(path: Path, limit: int = MAX_STATE) -> bytes:
    if not path.is_file():
        raise RuntimeFault("MISSING_FILE", "The selected file is unavailable.", 3)
    if path.stat().st_size > limit:
        raise RuntimeFault("INPUT_TOO_LARGE", "The selected file exceeds the size limit.")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise RuntimeFault("INPUT_TOO_LARGE", "The selected file exceeds the size limit.")
    return data


def file_hash(path: Path) -> str:
    return hashlib.sha256(read_bytes(path, MAX_RESOURCE)).hexdigest()


def atomic_write(root: Path, relative: str, data: bytes, *, immutable: bool = False) -> None:
    path = confined(root, relative, write=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path = confined(root, relative, write=True)
    if immutable and path.exists():
        if read_bytes(path) != data:
            raise RuntimeFault("CONFLICT", "An immutable object already exists with different bytes.", 4)
        return
    fd, temp_name = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        confined(root, relative, write=True)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def bounded(result: dict, budget: int) -> dict:
    """Count exactly the serialized UTF-8 envelope, including the final newline."""
    result = dict(result, output_bytes=0)
    for _ in range(12):
        size = len(canonical(result))
        if size == result["output_bytes"]:
            break
        result["output_bytes"] = size
    if len(canonical(result)) > budget:
        raise RuntimeFault("BUDGET_EXCEEDED", "Required records do not fit; reduce refs or increase budget_bytes. Nothing was silently omitted.")
    return result


def atomic_batch(targets: list[tuple[Path, str, bytes | None, bytes]]) -> None:
    """Cooperative checked writes with guarded rollback, not an OS transaction."""
    for root, rel, before, after in targets:
        p = confined(root, rel, write=True)
        actual = read_bytes(p) if p.exists() else None
        if actual != before:
            raise RuntimeFault("CONFLICT", "A managed file changed before publication.", 4)
    applied = []
    try:
        for root, rel, before, after in targets:
            if before != after:
                p = confined(root, rel, write=True)
                actual = read_bytes(p) if p.exists() else None
                if actual != before:
                    raise RuntimeFault("CONFLICT", "Concurrent modification detected before publication.", 4)
                atomic_write(root, rel, after)
                applied.append((root, rel, before, after))
    except (OSError, RuntimeFault) as original:
        recovery_needed = False
        for root, rel, before, after in reversed(applied):
            try:
                p = confined(root, rel, write=True)
                if not p.exists() or read_bytes(p) != after:
                    recovery_needed = True
                elif before is None:
                    p.unlink()
                else:
                    atomic_write(root, rel, before)
            except (OSError, RuntimeFault):
                recovery_needed = True
        if recovery_needed:
            raise RuntimeFault("RECOVERY_REQUIRED", "Publication failed and a concurrent edit prevented complete rollback. Inspect managed files before retrying.", 4) from original
        raise
