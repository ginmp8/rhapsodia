#!/usr/bin/env python3
"""Build and validate the MAGIA skill.zip package."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any
import sys
LOCAL_SCRIPTS = Path(__file__).resolve().parent
if str(LOCAL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(LOCAL_SCRIPTS))
from package_evidence import deterministic_zip, outside, atomic_bytes, json_bytes

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skill_package import validate_zip as validate_archive  # noqa: E402
from package_policy import iter_package_candidates  # noqa: E402


def iter_package_files(target: Path) -> tuple[list[Path], list[dict[str, str]]]:
    candidates, excluded = iter_package_candidates(target)
    files = [path for path in candidates if path.is_file() and not path.is_symlink()]
    return files, excluded


def validate_output_paths(target: Path, output: Path, json_output: Path | None = None) -> list[str]:
    """Reject package/report destinations that can mutate or alias the source tree."""
    errors: list[str] = []

    def inside(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    if inside(output, target):
        errors.append("package output must resolve outside the target skill tree")
    if json_output is not None:
        if inside(json_output, target):
            errors.append("json output must resolve outside the target skill tree")
        if json_output == output:
            errors.append("json output must not alias the package output")
    return errors


def build_package(target: Path, output: Path, validation_evidence: Path | None = None) -> dict[str, Any]:
    return deterministic_zip(target, output, evidence=validation_evidence, archive_validator=validate_archive)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Data-only package construction; external executed evidence is mandatory.")
    parser.add_argument("--target")
    parser.add_argument("--output")
    parser.add_argument("--validation-evidence", type=Path)
    parser.add_argument("--validate", action="store_true", help="Retained compatibility flag; evidence is always required.")
    parser.add_argument("--validate-only", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            result = validate_archive(args.validate_only)
            if isinstance(result, list):
                result = {"status": "fail" if result else "pass", "errors": result}
        else:
            if not args.target or not args.output:
                parser.error("--target and --output are required")
            target, output = Path(args.target), Path(args.output)
            if args.json_output:
                report = outside(target, args.json_output)
                if report == output.resolve() or (args.validation_evidence and report == args.validation_evidence.resolve()):
                    raise ValueError("report must not alias archive or validation evidence")
            info = deterministic_zip(target, output, evidence=args.validation_evidence, archive_validator=validate_archive)
            result = {"status": "pass", "package": info}
        if args.json_output:
            if args.validate_only and args.json_output.resolve() == args.validate_only.resolve():
                raise ValueError("report must not overwrite inspected archive")
            atomic_bytes(args.json_output, json_bytes(result))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("status") == "pass" else 1
    except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
