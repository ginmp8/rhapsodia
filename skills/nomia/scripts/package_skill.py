#!/usr/bin/env python3
"""Validate and package the nomia skill as an installable skill.zip."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

# Keep validation and packaging read-only with respect to the source tree.
sys.dont_write_bytecode = True
import sysconfig
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

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


def python_env(skill_root: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    python_paths: list[str] = [str(skill_root / "scripts")]
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    venv_site = Path(sys.executable).resolve().parents[1] / "lib" / version / "site-packages"
    purelib = sysconfig.get_paths().get("purelib")
    platlib = sysconfig.get_paths().get("platlib")
    for candidate in [venv_site if venv_site.exists() else None, purelib, platlib, env.get("PYTHONPATH")]:
        if candidate:
            python_paths.extend(str(candidate).split(os.pathsep))
    deduped: list[str] = []
    for value in python_paths:
        if value and value not in deduped:
            deduped.append(value)
    env["PYTHONPATH"] = os.pathsep.join(deduped)
    return env


def command(skill_root: Path, script_name: str, *args: str) -> list[str]:
    return [sys.executable, "-S", str(skill_root / "scripts" / script_name), *args]


def run_gate(name: str, command_line: list[str], env: dict[str, str]) -> GateResult:
    completed = subprocess.run(command_line, text=True, capture_output=True, env=env, check=False)
    return GateResult(
        name=name,
        command=command_line,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


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
    root = skill_root.resolve()
    destination = output.resolve()
    try:
        destination.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("output zip must be outside the skill folder to avoid packaging itself")

    files = collect_package_files(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    temporary.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                rel = f"nomia/{path.relative_to(root).as_posix()}"
                info = zipfile.ZipInfo(rel, date_time=ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return len(files)


def validate_and_package(skill_root: Path, output: Path) -> PackageResult:
    root = skill_root.resolve()
    env = python_env(root)
    gates = [
        run_gate("package-structure", command(root, "validate_skill_package.py", "--target", str(root)), env),
        run_gate("activation-scenarios", command(root, "validate_activation_scenarios.py", str(root / "examples" / "activation-scenarios.json")), env),
        run_gate("governance-scenarios", command(root, "validate_governance_scenarios.py", str(root / "evals" / "governance-scenarios.json")), env),
        run_gate("golden-examples", command(root, "validate_golden_examples.py", "--skill-root", str(root)), env),
        run_gate("identity-contract", command(root, "validate_identity_contract.py", "--target", str(root)), env),
        run_gate("release-contract", command(root, "validate_release_contract.py", "--target", str(root)), env),
        run_gate("contract-preservation", command(root, "validate_contract_preservation.py", "--target", str(root)), env),
        run_gate("documentation-links", command(root, "validate_documentation.py", "--target", str(root)), env),
        run_gate("assurance-contract", command(root, "validate_assurance_contract.py", "--target", str(root)), env),
        run_gate(
            "unit-tests",
            [sys.executable, "-S", "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py"],
            env,
        ),
    ]
    if any(gate.returncode != 0 for gate in gates):
        return PackageResult(str(root), str(output.resolve()), "fail", gates, 0)
    try:
        count = zip_skill(root, output)
    except Exception as exc:
        gates.append(GateResult("package-content", ["internal", "collect-package-files"], 1, "", str(exc)))
        output.unlink(missing_ok=True)
        return PackageResult(str(root), str(output.resolve()), "fail", gates, 0)

    archive_errors = validate_archive(output)
    gates.append(
        GateResult(
            "archive-content",
            ["internal", "validate-archive", str(output.resolve())],
            1 if archive_errors else 0,
            "archive content is safe" if not archive_errors else "",
            "\n".join(archive_errors),
        )
    )
    reproducibility_errors = validate_reproducible_archive(output)
    gates.append(
        GateResult(
            "archive-reproducibility",
            ["internal", "validate-reproducible-archive", str(output.resolve())],
            1 if reproducibility_errors else 0,
            "archive metadata is deterministic" if not reproducibility_errors else "",
            "\n".join(reproducibility_errors),
        )
    )
    if archive_errors or reproducibility_errors:
        output.unlink(missing_ok=True)
        return PackageResult(str(root), str(output.resolve()), "fail", gates, 0)
    return PackageResult(str(root), str(output.resolve()), "pass", gates, count)


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
    parser = argparse.ArgumentParser(description="Validate and package nomia as skill.zip.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="Path to the nomia skill root.")
    parser.add_argument("--output", required=True, help="Destination zip path. Use skill.zip as the file name for release packaging.")
    parser.add_argument("--json-output", help="Optional path for machine-readable package evidence.")
    args = parser.parse_args(argv)

    if Path(args.output).name != "skill.zip":
        print("ERROR: output file name must be exactly skill.zip", file=sys.stderr)
        return 2

    result = validate_and_package(Path(args.target), Path(args.output))
    payload = to_jsonable(result)
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(output, json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"status: {result.status}")
    print(f"target: {result.target}")
    print(f"output: {result.output}")
    for gate in result.gates:
        print(f"{gate.status}: {gate.name}")
        if gate.stdout:
            for line in gate.stdout.splitlines():
                print(f"  stdout: {line}")
        if gate.stderr:
            for line in gate.stderr.splitlines():
                print(f"  stderr: {line}")
    if result.status == "pass":
        print(f"packaged_files: {result.packaged_files}")
    return 0 if result.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
