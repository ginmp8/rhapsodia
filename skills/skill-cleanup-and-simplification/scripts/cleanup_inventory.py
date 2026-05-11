#!/usr/bin/env python3
"""Read-only cleanup inventory for skill packages and small helper projects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

PROTECTED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    "fixtures",
    "fixture",
    "expected",
    "expected-output",
    "expected-outputs",
    "golden",
    "snapshots",
    "snapshot",
    "evidence",
    "benchmark-reports",
    "reports",
}

CACHE_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".cache",
    "node_modules",
    "dist",
    "build",
}

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".7z", ".rar"}
SECRET_PATTERNS = [
    re.compile(r"(^|[._-])(secret|credential|credentials|token|private|key|cert)([._-]|$)", re.I),
    re.compile(r"^\.env($|[.])", re.I),
]
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTO" + r"DO\b", re.I),
    re.compile(r"\bREPLACE ME\b", re.I),
    re.compile(r"\bexample script\b", re.I),
    re.compile(r"\bexample asset\b", re.I),
    re.compile(r"\bapi reference\b", re.I),
]
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".js",
    ".ts",
    ".html",
    ".css",
}


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"SKILL.md", "README", "README.md"}


def file_hash(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def read_text_sample(path: Path, max_bytes: int = 20000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def classify_path(path: Path, root: Path, duplicate_hashes: dict[str, int]) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    parts = set(path.relative_to(root).parts)
    lower_name = path.name.lower()
    suffix = path.suffix.lower()
    reasons: list[str] = []
    status = "unknown"

    protected = any(part in PROTECTED_PARTS for part in parts) or any(p.search(lower_name) for p in SECRET_PATTERNS)
    if protected:
        status = "blocked"
        reasons.append("protected path, evidence, fixture, report, or secret-like name")
    elif any(part in CACHE_PARTS for part in parts):
        status = "generated"
        reasons.append("cache or generated directory")
    elif suffix in ARCHIVE_SUFFIXES:
        status = "blocked"
        reasons.append("archive or existing package should not be deleted automatically")

    size = path.stat().st_size if path.exists() else 0
    digest = file_hash(path)
    if digest and duplicate_hashes.get(digest, 0) > 1 and not protected:
        status = "duplicated" if status == "unknown" else status
        reasons.append("same sha256 as another file")

    placeholder_hits: list[str] = []
    if is_text_candidate(path) and size <= 2_000_000:
        text = read_text_sample(path)
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(text):
                placeholder_hits.append(pattern.pattern)
        if placeholder_hits and not protected:
            status = "placeholder" if status in {"unknown", "duplicated"} else status
            reasons.append("placeholder or scaffold markers found")

    if status == "unknown" and rel == "SKILL.md":
        status = "used"
        reasons.append("root skill entrypoint")
    elif status == "unknown" and rel.startswith(("references/", "assets/templates/", "scripts/", "examples/", "evals/", "agents/")):
        status = "integrable"
        reasons.append("skill support resource requires reference or usage review")

    return {
        "path": rel,
        "status": status,
        "size_bytes": size,
        "sha256": digest,
        "reasons": reasons or ["no automatic evidence"],
        "placeholder_hits": placeholder_hits,
    }


def collect_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def build_inventory(root: Path) -> dict[str, Any]:
    files = collect_files(root)
    hashes: dict[str, int] = {}
    for path in files:
        digest = file_hash(path)
        if digest:
            hashes[digest] = hashes.get(digest, 0) + 1

    entries = [classify_path(path, root, hashes) for path in files]
    status_counts: dict[str, int] = {}
    for item in entries:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    return {
        "target": str(root),
        "file_count": len(files),
        "status_counts": status_counts,
        "entries": sorted(entries, key=lambda item: item["path"]),
        "notes": [
            "This inventory is read-only and conservative.",
            "Classify and review evidence before deleting any candidate.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a read-only cleanup inventory.")
    parser.add_argument("--target", required=True, help="Target folder to inspect.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"target is not a directory: {root}")

    inventory = build_inventory(root)
    payload = json.dumps(inventory, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
        print(f"wrote inventory: {output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
