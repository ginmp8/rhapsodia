#!/usr/bin/env python3
"""Validate and package a skill-booster target folder as skill.zip."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

BLOCKED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "reports",
    "generated_evidence",
    "generated-evidence",
    "benchmark-results",
    "validation-reports",
}
BLOCKED_SUFFIXES = {".pyc", ".pyo"}
BLOCKED_FILENAMES = {"skill.zip"}


def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    if parts & BLOCKED_PARTS:
        return True
    if path.name in BLOCKED_FILENAMES:
        return True
    if path.suffix in BLOCKED_SUFFIXES:
        return True
    return False


def validate(target: Path) -> tuple[int, dict]:
    validator = Path(__file__).resolve().with_name("validate_skill_booster.py")
    if not validator.exists():
        return 1, {"status": "fail", "errors": [f"missing validator: {validator}"]}
    proc = subprocess.run(
        [sys.executable, str(validator), "--target", str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {"status": "fail", "errors": ["validator did not return JSON"], "stdout": proc.stdout, "stderr": proc.stderr}
    return proc.returncode, report



def validate_reconciliation(ledger: Path) -> tuple[int, dict]:
    validator = Path(__file__).resolve().with_name("validate_specialist_reconciliation.py")
    if not validator.exists():
        return 1, {"status": "fail", "errors": [f"missing reconciliation validator: {validator}"]}
    proc = subprocess.run(
        [sys.executable, str(validator), "--ledger", str(ledger)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {"status": "fail", "errors": ["reconciliation validator did not return JSON"], "stdout": proc.stdout, "stderr": proc.stderr}
    return proc.returncode, report

def package(target: Path, output: Path, reconciliation_ledger: Path | None = None) -> dict:
    target = target.resolve()
    output = output.resolve()
    if output.name != "skill.zip":
        raise ValueError("output filename must be skill.zip")
    output.parent.mkdir(parents=True, exist_ok=True)
    if target in output.parents or output == target:
        raise ValueError("output must be outside the target skill folder")
    code, validation = validate(target)
    if code != 0 or validation.get("status") != "pass":
        return {"status": "fail", "stage": "validate", "validation": validation}
    reconciliation = None
    if reconciliation_ledger is not None:
        rec_code, reconciliation = validate_reconciliation(reconciliation_ledger)
        if rec_code != 0 or reconciliation.get("finalization_allowed") is not True:
            return {"status": "fail", "stage": "specialist_reconciliation", "validation": validation, "specialist_reconciliation": reconciliation}
    files: list[str] = []
    package_errors: list[str] = []
    root_name = target.name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(target.rglob("*")):
            rel = path.relative_to(target)
            if should_exclude(rel):
                continue
            if path.is_symlink():
                package_errors.append(f"symlink is not packaged: {rel}")
                continue
            if path.is_file():
                archive_name = f"{root_name}/{rel.as_posix()}"
                zf.write(path, archive_name)
                files.append(archive_name)
    with zipfile.ZipFile(output, "r") as zf:
        bad = zf.testzip()
        names = zf.namelist()
    top_levels = sorted({name.split("/", 1)[0] for name in names if name})
    if bad:
        package_errors.append(f"corrupt zip member: {bad}")
    if top_levels != [root_name]:
        package_errors.append(f"expected one top-level directory {root_name!r}, found {top_levels}")
    if f"{root_name}/SKILL.md" not in names:
        package_errors.append(f"archive missing {root_name}/SKILL.md")
    status = "pass" if not package_errors else "fail"
    return {
        "status": status,
        "archive": str(output),
        "file_count": len(files),
        "size_bytes": output.stat().st_size if output.exists() else 0,
        "validation": validation,
        "specialist_reconciliation": reconciliation,
        "package_errors": package_errors,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package skill-booster as skill.zip.")
    parser.add_argument("--target", required=True, help="Skill folder to package")
    parser.add_argument("--output", required=True, help="Output path; basename must be skill.zip")
    parser.add_argument("--report", help="Optional JSON package report path")
    parser.add_argument("--reconciliation-ledger", help="Optional specialist reconciliation JSON; packaging fails unless finalization_allowed is true")
    args = parser.parse_args()
    try:
        ledger = Path(args.reconciliation_ledger) if args.reconciliation_ledger else None
        report = package(Path(args.target), Path(args.output), ledger)
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)]}
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.report:
        Path(args.report).write_text(text + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
