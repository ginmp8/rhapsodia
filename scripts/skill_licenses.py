"""Resolve centrally stored, immutable skill license notices without path escapes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rhapsodia-skill-legal-assets/v1"


def _safe_relative(value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("invalid license path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("noncanonical license path: " + value)
    return Path(*p.parts)


def _read_within(root: Path, relative: str) -> bytes:
    path = root / _safe_relative(relative)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("missing or unsafe license asset: " + relative)
    return path.read_bytes()


def _blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def registry(root: Path = ROOT) -> dict:
    doc = json.loads((root / "licenses" / "skill-assets.json").read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError("unsupported legal registry schema")
    rows = doc.get("skills")
    if not isinstance(rows, list) or len(rows) != 76:
        raise ValueError("expected one legal registry entry for each of 76 skills")
    names = [x.get("name") for x in rows]
    if names != sorted(names) or len(set(names)) != len(names):
        raise ValueError("legal registry must have unique sorted skill names")
    available = sorted(p.name for p in (root / "skills").iterdir()
                       if p.is_dir() and (p / "SKILL.md").is_file() and not p.is_symlink())
    if names != available:
        raise ValueError("legal registry and installed skill inventory diverge")
    for row in rows:
        if not isinstance(row.get("notices"), list):
            raise ValueError("notices must be a list")
        paths: set[str] = set()
        for notice in row["notices"]:
            original, canonical, blob = notice["path"], notice["canonical"], notice["blob_sha"]
            _safe_relative(original)
            if original in paths:
                raise ValueError("duplicated notice destination: " + original)
            paths.add(original)
            if canonical != "LICENSE" and not canonical.startswith("licenses/"):
                raise ValueError("notice outside approved legal root")
            data = _read_within(root, canonical)
            if _blob_sha(data) != blob or len(data) != notice["size"]:
                raise ValueError("license content drift: " + canonical)
            source = root / "skills" / row["name"] / _safe_relative(original)
            if source.exists() or source.is_symlink():
                raise ValueError("unmigrated notice in skill source: " + str(source))
    return doc


def restore(skill: str, root: Path = ROOT, loaded: dict | None = None) -> dict[str, bytes]:
    doc = loaded if loaded is not None else registry(root)
    row = next((x for x in doc["skills"] if x["name"] == skill), None)
    if row is None:
        raise ValueError("unknown skill: " + skill)
    assets = {notice["path"]: _read_within(root, notice["canonical"]) for notice in row["notices"]}
    if "LICENSE" not in assets:
        assets["LICENSE"] = _read_within(root, "LICENSE")
    return dict(sorted(assets.items()))
