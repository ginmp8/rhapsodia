#!/usr/bin/env python3
"""Validate and package the nomia skill as an installable skill.zip."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

# Keep validation and packaging read-only with respect to the source tree.
sys.dont_write_bytecode = True
import sysconfig
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any
import sys
LOCAL_SCRIPTS = Path(__file__).resolve().parent
if str(LOCAL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(LOCAL_SCRIPTS))
from package_evidence import deterministic_zip, verify_evidence, outside, atomic_bytes, json_bytes

from nomia_utils import PRIVATE_KEY_HEADERS, atomic_write_text, sensitive_package_reason

EXCLUDED_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_DIR_PATHS = {"docs/skill-benchmark", "reports", "generated-evidence", "evidence"}
EXCLUDED_FILE_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".zip"}
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


@dataclass
class GateResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def status(self) -> str:
        return "pass" if self.returncode == 0 else "fail"


@dataclass
class PackageResult:
    target: str
    output: str
    status: str
    gates: list[GateResult]
    packaged_files: int











def should_package(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    rel = path.relative_to(root).as_posix()
    if any(part in EXCLUDED_DIR_NAMES for part in rel_parts):
        return False
    if any(rel == excluded or rel.startswith(excluded + "/") for excluded in EXCLUDED_DIR_PATHS):
        return False
    if path.name in EXCLUDED_FILE_NAMES:
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def collect_package_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        rel_parts = path.relative_to(root).parts
        if any(part in EXCLUDED_DIR_NAMES for part in rel_parts):
            continue
        if path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        rel = path.relative_to(root).as_posix()
        reason = sensitive_package_reason(path)
        if reason:
            raise ValueError(f"unsafe package path {rel}: {reason}")
        if should_package(path, root):
            files.append(path)
    return files


def validate_archive(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    try:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                name = info.filename
                pure = PurePosixPath(name)
                if name in seen:
                    errors.append(f"duplicate archive entry: {name}")
                seen.add(name)
                if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != "nomia":
                    errors.append(f"unsafe archive entry: {name}")
                    continue
                mode = (info.external_attr >> 16) & 0o170000
                if mode == 0o120000:
                    errors.append(f"symlink archive entry is not allowed: {name}")
                reason = sensitive_package_reason(Path(pure.name))
                if reason:
                    errors.append(f"unsafe archive entry {name}: {reason}")
                if not info.is_dir() and info.file_size <= 2_000_000:
                    content = archive.read(info)
                    if any(header in content for header in PRIVATE_KEY_HEADERS):
                        errors.append(f"private key material is not allowed: {name}")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"cannot validate archive: {exc}")
    return errors



def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_reproducible_archive(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = [info.filename for info in archive.infolist()]
            if names != sorted(names):
                errors.append("archive entries are not sorted deterministically")
            for info in archive.infolist():
                if info.date_time != ZIP_TIMESTAMP:
                    errors.append(f"archive timestamp is not deterministic: {info.filename}")
                mode = (info.external_attr >> 16) & 0o777
                if not info.is_dir() and mode != 0o644:
                    errors.append(f"archive mode is not 0644: {info.filename}")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"cannot validate reproducible archive metadata: {exc}")
    return errors


def build_release_attestation(result: PackageResult) -> dict[str, Any]:
    root = Path(result.target)
    output = Path(result.output)
    version = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").is_file() else None
    contract_path = root / "tests" / "current-release-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8")) if contract_path.is_file() else {}
    protected = {}
    for rel in sorted((contract.get("protected_files") or {})):
        path = root / rel
        if path.is_file():
            protected[rel] = sha256_file(path)
    return {
        "skill": "nomia",
        "version": version,
        "package_root": "nomia",
        "archive_sha256": sha256_file(output) if output.is_file() else None,
        "archive_size_bytes": output.stat().st_size if output.is_file() else None,
        "packaged_files": result.packaged_files,
        "protected_files": protected,
        "original_contract_sha256": sha256_file(root / "tests" / "original-contract.json") if (root / "tests" / "original-contract.json").is_file() else None,
        "deterministic_zip_timestamp": list(ZIP_TIMESTAMP),
        "behavioral_activation_measured": False,
    }

def zip_skill(skill_root: Path, output: Path) -> int:
    """Low-level data-only ZIP utility; release callers must use validate_and_package."""
    collect_package_files(skill_root)
    info = deterministic_zip(skill_root, output, root_name="nomia", require_evidence=False, archive_validator=validate_archive)
    return info["file_count"]


def validate_and_package(skill_root: Path, output: Path, validation_evidence: Path | None = None) -> PackageResult:
    gates = []
    try:
        value = verify_evidence(skill_root, validation_evidence)
        gates = [GateResult(g["name"], g["command"], g["returncode"], "external evidence verified", "") for g in value["gates"]]
        collect_package_files(skill_root)
        info = deterministic_zip(skill_root, output, root_name="nomia", evidence=validation_evidence, archive_validator=validate_archive)
        return PackageResult(str(skill_root.resolve()), str(output.resolve()), "pass", gates, info["file_count"])
    except (OSError, ValueError, TypeError, KeyError) as exc:
        gates.append(GateResult("package-evidence", ["internal", "verify-external-evidence"], 1, "", str(exc)))
        return PackageResult(str(skill_root.resolve()), str(output.resolve()), "fail", gates, 0)


def to_jsonable(result: PackageResult) -> dict[str, Any]:
    payload = {
        "target": result.target,
        "output": result.output,
        "status": result.status,
        "packaged_files": result.packaged_files,
        "gates": [asdict(gate) | {"status": gate.status} for gate in result.gates],
    }
    if result.status == "pass":
        payload["release_attestation"] = build_release_attestation(result)
    return payload


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
