#!/usr/bin/env python3
"""Build and validate the MAGIA skill.zip package."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_skill_package  # noqa: E402

EXCLUDED_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "benchmark-reports", "test-results", "tmp", ".tmp"}
EXCLUDED_FILE_NAMES = {".DS_Store", "test-results.json"}
SECRET_NAME_RE = re.compile(r"(secret|credential|private[_-]?key|\.env$|id_rsa|token)", re.IGNORECASE)


def is_sensitive_name(name: str) -> bool:
    return bool(SECRET_NAME_RE.search(name))


def should_exclude(rel_path: str) -> tuple[bool, str | None]:
    parts = Path(rel_path).parts
    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return True, "excluded directory"
    name = parts[-1]
    if name in EXCLUDED_FILE_NAMES or name.endswith(("~", ".swp", ".swo")):
        return True, "excluded file"
    if name.endswith(".zip"):
        return True, "nested zip"
    if is_sensitive_name(name):
        return True, "sensitive-looking file name"
    return False, None


def iter_package_files(target: Path) -> tuple[list[Path], list[dict[str, str]]]:
    files: list[Path] = []
    excluded: list[dict[str, str]] = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(target).as_posix()
        skip, reason = should_exclude(rel)
        if skip:
            excluded.append({"path": rel, "reason": reason or "excluded"})
            continue
        files.append(path)
    return files, excluded


def build_package(target: Path, output: Path) -> dict[str, Any]:
    files, excluded = iter_package_files(target)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    root_name = target.name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            rel = file_path.relative_to(target).as_posix()
            archive.write(file_path, f"{root_name}/{rel}")
    return {
        "output": str(output),
        "file_count": len(files),
        "excluded": excluded,
        "size_bytes": output.stat().st_size,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the MAGIA skill.zip package.")
    parser.add_argument("--target", required=True, help="Path to the MAGIA skill root.")
    parser.add_argument("--output", required=True, help="Path to write skill.zip.")
    parser.add_argument("--validate", action="store_true", help="Validate the folder before packaging and the zip after packaging.")
    parser.add_argument("--json-output", help="Optional path for machine-readable packaging evidence.")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    output = Path(args.output).resolve()
    result: dict[str, Any] = {"target": str(target), "output": str(output)}

    if args.validate:
        folder = validate_skill_package.validate_target(target)
        result["folder_validation"] = folder
        if folder["status"] != "pass":
            result["status"] = "fail"
            if args.json_output:
                Path(args.json_output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps(result, indent=2, sort_keys=True))
            return 1

    result["package"] = build_package(target, output)

    if args.validate:
        archive = validate_skill_package.validate_zip(output)
        result["zip_validation"] = archive
        result["status"] = "pass" if archive["status"] == "pass" else "fail"
    else:
        result["status"] = "pass"

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
