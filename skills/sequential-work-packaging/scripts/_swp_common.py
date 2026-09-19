from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

SPEC_RE = re.compile(r"^spec(?P<n>[0-9]{3,})$")
TASK_RE = re.compile(r"^task(?P<n>[0-9]{3,})$")
FEATURE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CYCLE_RE = re.compile(r"^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$")
VERSION_RE = re.compile(r"^v(?P<major>0|[1-9][0-9]*)\.(?P<minor>0|[1-9][0-9]*)\.(?P<patch>0|[1-9][0-9]*)$")

CANONICAL_SPEC_FILES = {"manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"}
SPEC_STATUSES = {"planned", "in_progress", "done", "cancelled"}
CYCLE_STATUSES = {"planned", "active", "closed", "cancelled"}
TYPES = {"feature", "fix"}
CLASSIFICATIONS = {"feature", "bugfix", "refactor", "performance", "validation", "architecture", "investigation", "docs-only"}
PHASES = {"define", "execute", "review", "done"}
MODES = {"order", "define", "refine", "decompose", "audit", "normalize"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def semver_tuple(value: str) -> tuple[int, int, int] | None:
    m = VERSION_RE.fullmatch(value or "")
    if not m:
        return None
    return tuple(int(m.group(k)) for k in ("major", "minor", "patch"))


def parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw == "[]":
        return []
    if raw == "{}":
        return {}
    if raw in {"null", "~"}:
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", raw):
        return int(raw)
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        return raw[1:-1]
    return raw


def _clean_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if "\t" in text:
        raise ValueError("tabs are not supported in canonical YAML")
    return text.splitlines()


def parse_catalog(path: Path) -> dict[str, Any]:
    lines = _clean_lines(path)
    out: dict[str, Any] = {}
    specs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    pending_list_key: str | None = None
    in_specs = False

    for lineno, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            current = None
            pending_list_key = None
            if ":" not in stripped:
                raise ValueError(f"line {lineno}: expected key: value")
            key, value = stripped.split(":", 1)
            key, value = key.strip(), value.strip()
            if key in out:
                raise ValueError(f"line {lineno}: duplicate top-level key {key}")
            if key == "specs":
                if value:
                    raise ValueError(f"line {lineno}: specs must be a block list")
                out[key] = specs
                in_specs = True
            else:
                out[key] = parse_scalar(value)
                in_specs = False
            continue
        if not in_specs:
            raise ValueError(f"line {lineno}: unsupported nested YAML outside specs")
        if indent == 2 and stripped.startswith("- "):
            body = stripped[2:]
            if ":" not in body:
                raise ValueError(f"line {lineno}: expected list item key: value")
            key, value = body.split(":", 1)
            current = {key.strip(): parse_scalar(value)}
            specs.append(current)
            pending_list_key = None
            continue
        if current is None:
            raise ValueError(f"line {lineno}: spec field without spec item")
        if indent == 4:
            if ":" not in stripped:
                raise ValueError(f"line {lineno}: expected spec key: value")
            key, value = stripped.split(":", 1)
            key, value = key.strip(), value.strip()
            if key in current:
                raise ValueError(f"line {lineno}: duplicate spec key {key}")
            if value:
                current[key] = parse_scalar(value)
                pending_list_key = None
            else:
                current[key] = []
                pending_list_key = key
            continue
        if indent == 6 and stripped.startswith("- ") and pending_list_key:
            current[pending_list_key].append(parse_scalar(stripped[2:]))
            continue
        raise ValueError(f"line {lineno}: unsupported canonical YAML form")
    return out


def parse_manifest(path: Path) -> dict[str, Any]:
    lines = _clean_lines(path)
    out: dict[str, Any] = {}
    nested_key: str | None = None
    for lineno, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            if ":" not in stripped:
                raise ValueError(f"line {lineno}: expected key: value")
            key, value = stripped.split(":", 1)
            key, value = key.strip(), value.strip()
            if key in out:
                raise ValueError(f"line {lineno}: duplicate key {key}")
            if value:
                out[key] = parse_scalar(value)
                nested_key = None
            else:
                out[key] = {}
                nested_key = key
            continue
        if indent == 2 and nested_key:
            if ":" not in stripped:
                raise ValueError(f"line {lineno}: expected nested key: value")
            key, value = stripped.split(":", 1)
            out[nested_key][key.strip()] = parse_scalar(value)
            continue
        if indent >= 2 and nested_key == "traceability":
            continue
        raise ValueError(f"line {lineno}: unsupported canonical YAML form")
    return out


def parse_tasks(path: Path) -> list[dict[str, Any]]:
    task_header = re.compile(r"^- \[(?P<done>[ xX])\] Task (?P<num>[0-9]+):\s*(?P<title>.*)$")
    field = re.compile(r"^\s{2,}- (?P<key>[A-Za-z][A-Za-z ]+):\s*(?P<value>.*)$")
    tasks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = task_header.match(raw)
        if m:
            current = {
                "display_number": int(m.group("num")),
                "title": m.group("title").strip(),
                "done": m.group("done").lower() == "x",
                "line": lineno,
                "fields": {},
            }
            tasks.append(current)
            continue
        if current:
            fm = field.match(raw)
            if fm:
                current["fields"][fm.group("key").strip().lower()] = fm.group("value").strip()
    for task in tasks:
        task_id = task["fields"].get("task id")
        task["task_id"] = task_id if task_id else f"legacy-task-{task['display_number']}"
        deps = task["fields"].get("dependencies", "none")
        if deps.lower() in {"", "none", "[]"}:
            task["dependencies"] = []
        else:
            dep_text = deps.strip("[]")
            task["dependencies"] = [x.strip() for x in dep_text.split(",") if x.strip()]
    return tasks


def resolve_inside(root: Path, rel: str) -> Path:
    if not rel or Path(rel).is_absolute():
        raise ValueError("path must be a non-empty relative path")
    base = root.resolve()
    target = (base / rel).resolve(strict=False)
    try:
        common = Path(os.path.commonpath([str(base), str(target)]))
    except ValueError as exc:
        raise ValueError("path escapes root") from exc
    if common != base:
        raise ValueError("path escapes root")
    return target


def is_protected_relative(rel: str, extra: list[str] | None = None) -> bool:
    p = Path(rel)
    parts = {x.lower() for x in p.parts}
    name = p.name.lower()
    if ".git" in parts or name == ".env" or name.endswith(".pem") or name.endswith(".key"):
        return True
    for item in extra or []:
        item = item.strip("/")
        if not item:
            continue
        if rel == item or rel.startswith(item + "/"):
            return True
    return False


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(encoded)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def diagnostic(code: str, subject: str, evidence: Any, severity: str = "error", supported_fixes: list[str] | None = None) -> dict[str, Any]:
    return {
        "code": code,
        "subject": subject,
        "evidence": evidence,
        "severity": severity,
        "supported_fixes": supported_fixes or [],
    }


def tree_hash(root: Path) -> str:
    rows: list[str] = []
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        rows.append(f"{p.relative_to(root).as_posix()}\0{sha256_file(p)}")
    return sha256_bytes("\n".join(rows).encode("utf-8"))
