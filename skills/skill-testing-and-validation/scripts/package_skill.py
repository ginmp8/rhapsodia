#!/usr/bin/env python3
"""Package a skill folder atomically with canonical archive root and a hash receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".zip"}
MAX_BYTES = 25 * 1024 * 1024
NAME_RE = re.compile(r"^name:\s*([a-z0-9-]+)\s*$", re.MULTILINE)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def skill_name(root: Path) -> str | None:
    path = root / "SKILL.md"
    if not path.exists():
        return None
    match = NAME_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    return match.group(1) if match else None


def iter_package_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix.lower() not in EXCLUDE_SUFFIXES:
            yield path


def validate_root(root: Path) -> list[str]:
    errors: list[str] = []
    if not (root / "SKILL.md").exists():
        errors.append("SKILL.md missing")
    if len(list(root.glob("SKILL.md"))) != 1:
        errors.append("expected exactly one root SKILL.md")
    if not skill_name(root):
        errors.append("portable lowercase skill name missing from SKILL.md frontmatter")
    return errors


def preflight(root: Path, output: Path, files: list[Path]) -> list[str]:
    errors: list[str] = []
    authored = output.absolute()
    resolved = output.resolve()
    if authored.suffix.lower() != ".zip" or resolved.suffix.lower() != ".zip":
        errors.append("output must remain a .zip after canonical path resolution")
    for source in files:
        try:
            if source.resolve() == resolved:
                errors.append(f"output aliases package input: {source.relative_to(root).as_posix()}")
                break
        except OSError:
            continue
    return errors


def package(root: Path, output: Path) -> dict[str, Any]:
    root = root.resolve()
    output = output.absolute()
    errors = validate_root(root)
    files = list(iter_package_files(root)) if not errors else []
    errors.extend(preflight(root, output, files))
    result: dict[str, Any] = {
        "receipt_version": 1,
        "status": "fail" if errors else "pending",
        "passed": False,
        "errors": errors,
        "target": str(root),
        "output": str(output),
        "output_resolved": str(output.resolve()),
        "size_bytes": None,
        "file_count": len(files),
        "sha256": None,
        "archive_root": skill_name(root),
    }
    if errors:
        return result
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent))
    os.close(fd)
    temp = Path(temp_name)
    try:
        archive_root = skill_name(root) or root.name
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
            for file_path in files:
                arcname = Path(archive_root) / file_path.relative_to(root)
                archive.write(file_path, arcname.as_posix())
        size = temp.stat().st_size
        if size > MAX_BYTES:
            result["errors"] = ["archive exceeds 25 MiB upload limit"]
            result["status"] = "fail"
            return result
        digest = sha256(temp)
        os.replace(temp, output)
        result.update({"passed": True, "status": "pass", "size_bytes": size, "sha256": digest})
        return result
    finally:
        if temp.exists():
            temp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill folder atomically as skill.zip.")
    parser.add_argument("target", help="Skill folder")
    parser.add_argument("output", nargs="?", default="skill.zip", help="Output zip path")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()
    result = package(Path(args.target), Path(args.output))
    if args.report:
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
