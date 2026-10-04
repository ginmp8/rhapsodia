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

from validate_skill_package import validate as validate_skill_package

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".zip"}
MAX_BYTES = 25 * 1024 * 1024
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
ZIP_FILE_MODE = 0o100644 << 16
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
    structural = validate_skill_package(root)
    errors = list(structural.get("errors") or [])
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            errors.append(f"symlink inputs are not package-safe: {path.relative_to(root).as_posix()}")
    return errors


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{resolved.name}.", suffix=".tmp", dir=str(resolved.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, resolved)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def preflight(root: Path, output: Path, files: list[Path]) -> list[str]:
    errors: list[str] = []
    authored = output.absolute()
    resolved = output.resolve()
    if authored.suffix.lower() != ".zip" or resolved.suffix.lower() != ".zip":
        errors.append("output must remain a .zip after canonical path resolution")
    if is_within(resolved, root):
        errors.append("output must not be inside target tree; packaging output must remain external to validated source bytes")
    for source in files:
        try:
            if source.resolve() == resolved:
                errors.append(f"output aliases package input: {source.relative_to(root).as_posix()}")
                break
        except OSError:
            continue
    return errors


def preflight_report(root: Path, output: Path, report: Path | None) -> list[str]:
    if report is None:
        return []
    resolved_output = output.resolve()
    resolved_report = report.resolve()
    errors: list[str] = []
    if resolved_report == resolved_output:
        errors.append("report path aliases package output")
    if is_within(resolved_report, root):
        errors.append("report must remain outside target tree so delivery evidence cannot mutate validated source bytes")
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
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for file_path in files:
                arcname = (Path(archive_root) / file_path.relative_to(root)).as_posix()
                info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
                info.create_system = 3
                info.external_attr = ZIP_FILE_MODE
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, file_path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
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
    target = Path(args.target).resolve()
    output = Path(args.output).absolute()
    report = Path(args.report).absolute() if args.report else None
    delivery_errors = preflight_report(target, output, report)
    if delivery_errors:
        result = {
            "receipt_version": 1,
            "status": "fail",
            "passed": False,
            "errors": delivery_errors,
            "target": str(target),
            "output": str(output),
            "output_resolved": str(output.resolve()),
            "size_bytes": None,
            "file_count": 0,
            "sha256": None,
            "archive_root": skill_name(target),
        }
    else:
        result = package(target, output)
        if report:
            write_json_atomic(report, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
