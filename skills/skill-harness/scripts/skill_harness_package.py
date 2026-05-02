#!/usr/bin/env python3
"""Validate and package a ChatGPT or Agent skill folder as skill.zip."""
import argparse
import importlib.util
import json
import sys
import stat
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR_PATH = SCRIPT_DIR / "skill_harness_validate.py"
sys.dont_write_bytecode = True
EXCLUDE_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build", "reports", ".reports", "artifacts", "scratch", ".scratch", "tmp", "temp", "coverage", ".coverage"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}
EXCLUDE_NAMES = {".DS_Store"}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def load_validator_module():
    spec = importlib.util.spec_from_file_location("skill_harness_validate", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def should_exclude(path, target):
    rel = path.relative_to(target)
    if set(rel.parts) & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_NAMES:
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    return False


def iter_package_files(target):
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if should_exclude(path, target):
            continue
        yield path


def add_file(zipf, path, arcname):
    data = path.read_bytes()
    info = zipfile.ZipInfo(arcname, date_time=ZIP_TIMESTAMP)
    mode = path.stat().st_mode
    perm = stat.S_IMODE(mode)
    if not perm:
        perm = 0o644
    info.external_attr = (perm & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zipf.writestr(info, data)


def package_skill(target, output, strict=False):
    target = Path(target).resolve()
    output = Path(output).resolve()
    validator = load_validator_module()
    validation = validator.validate_package(target)
    blocker_failures = [gate for gate in validation["gates"] if not gate["passed"] and gate["severity"] == "blocker"]
    major_failures = [gate for gate in validation["gates"] if not gate["passed"] and gate["severity"] == "major"]
    if blocker_failures or (strict and major_failures):
        return {
            "packaged": False,
            "output": str(output),
            "validation": validation,
            "error": "validation gates failed",
            "excluded_dirs": sorted(EXCLUDE_DIRS),
            "excluded_suffixes": sorted(EXCLUDE_SUFFIXES),
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    files = list(iter_package_files(target))
    with zipfile.ZipFile(output, "w") as zipf:
        for path in files:
            arcname = path.relative_to(target).as_posix()
            add_file(zipf, path, arcname)
    return {
        "packaged": True,
        "output": str(output),
        "file_count": len(files),
        "archive_entries": [path.relative_to(target).as_posix() for path in files],
        "validation": validation,
        "excluded_dirs": sorted(EXCLUDE_DIRS),
        "excluded_suffixes": sorted(EXCLUDE_SUFFIXES),
    }


def main():
    parser = argparse.ArgumentParser(description="Validate and package a ChatGPT or Agent skill folder as a zip.")
    parser.add_argument("--target", required=True, help="Path to target skill folder")
    parser.add_argument("--output", required=True, help="Path to write skill.zip")
    parser.add_argument("--report", help="Path to write JSON package report")
    parser.add_argument("--strict", action="store_true", help="Fail packaging when major gates fail, not only blockers")
    args = parser.parse_args()
    report = package_skill(args.target, args.output, strict=args.strict)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    raise SystemExit(0 if report.get("packaged") else 1)


if __name__ == "__main__":
    main()
