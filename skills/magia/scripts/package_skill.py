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

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_skill_package  # noqa: E402
from package_policy import iter_package_candidates  # noqa: E402


def iter_package_files(target: Path) -> tuple[list[Path], list[dict[str, str]]]:
    candidates, excluded = iter_package_candidates(target)
    files = [path for path in candidates if path.is_file() and not path.is_symlink()]
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

    security_errors = validate_skill_package.scan_package_candidates(target)
    if security_errors:
        result["status"] = "fail"
        result["security_errors"] = security_errors
        if args.json_output:
            Path(args.json_output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

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
