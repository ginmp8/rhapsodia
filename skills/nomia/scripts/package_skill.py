#!/usr/bin/env python3
"""Package nomia without executing validator code from the target tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import sysconfig
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXCLUDED_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_DIR_PATHS = {"docs/skill-benchmark", "reports", "generated-evidence", "evidence"}
EXCLUDED_FILE_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".zip"}
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
EVIDENCE_SCHEMA_VERSION = 1
REQUIRED_GATE_NAMES = (
    "package-structure",
    "activation-scenarios",
    "golden-examples",
    "identity-contract",
    "contract-preservation",
    "unit-tests",
)


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
    target_tree_sha256: str = ""


def python_env(skill_root: Path) -> dict[str, str]:
    """Compatibility helper for external isolated validation runners."""
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
    """Compatibility helper for external isolated validation runners."""
    return [sys.executable, "-S", str(skill_root / "scripts" / script_name), *args]


def run_gate(name: str, command_line: list[str], env: dict[str, str]) -> GateResult:
    """Run one gate only when explicitly called by an external isolated runner.

    The release packaging path deliberately does not call this function.
    """
    completed = subprocess.run(command_line, text=True, capture_output=True, env=env, check=False)
    return GateResult(
        name=name,
        command=command_line,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def should_package(path: Path, root: Path) -> bool:
    if path.is_symlink():
        return False
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


def package_files(skill_root: Path) -> list[Path]:
    root = skill_root.resolve()
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            rel = path.relative_to(root).as_posix()
            raise ValueError(f"symbolic links are not allowed in the package tree: {rel}")
        if should_package(path, root):
            files.append(path)
    return files


def tree_digest(skill_root: Path) -> str:
    root = skill_root.resolve()
    digest = hashlib.sha256()
    for path in package_files(root):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def zip_skill(skill_root: Path, output: Path) -> int:
    root = skill_root.resolve()
    destination = output.resolve()
    try:
        destination.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("output zip must be outside the skill folder to avoid packaging itself")

    files = package_files(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            rel = f"nomia/{path.relative_to(root).as_posix()}"
            info = zipfile.ZipInfo(rel, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return len(files)


def load_validation_evidence(path: Path, skill_root: Path) -> tuple[list[GateResult], str]:
    evidence_path = path.resolve()
    root = skill_root.resolve()
    try:
        evidence_path.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("validation evidence must be outside the target skill folder")

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("validation evidence must be a JSON object")
    if payload.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        raise ValueError(f"validation evidence schema_version must be {EVIDENCE_SCHEMA_VERSION}")

    expected_digest = tree_digest(root)
    supplied_digest = payload.get("target_tree_sha256")
    if supplied_digest != expected_digest:
        raise ValueError(
            "validation evidence does not match the current target tree: "
            f"expected {expected_digest}, received {supplied_digest}"
        )

    raw_gates = payload.get("gates")
    if not isinstance(raw_gates, list):
        raise ValueError("validation evidence gates must be a list")

    parsed: dict[str, GateResult] = {}
    for item in raw_gates:
        if not isinstance(item, dict):
            raise ValueError("every validation evidence gate must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("every validation evidence gate must have a name")
        if name in parsed:
            raise ValueError(f"duplicate validation evidence gate: {name}")
        command_value = item.get("command", [])
        if not isinstance(command_value, list) or not all(isinstance(value, str) for value in command_value):
            raise ValueError(f"validation evidence command for {name} must be a string list")
        returncode = item.get("returncode")
        if not isinstance(returncode, int):
            raise ValueError(f"validation evidence returncode for {name} must be an integer")
        result = GateResult(
            name=name,
            command=command_value,
            returncode=returncode,
            stdout=str(item.get("stdout", "")),
            stderr=str(item.get("stderr", "")),
        )
        parsed[name] = result

    missing = [name for name in REQUIRED_GATE_NAMES if name not in parsed]
    if missing:
        raise ValueError(f"validation evidence is missing required gates: {', '.join(missing)}")
    failed = [name for name in REQUIRED_GATE_NAMES if parsed[name].returncode != 0]
    if failed:
        raise ValueError(f"validation evidence contains failed gates: {', '.join(failed)}")

    return [parsed[name] for name in REQUIRED_GATE_NAMES], expected_digest


def validate_and_package(
    skill_root: Path,
    output: Path,
    validation_evidence: Path | None = None,
) -> PackageResult:
    root = skill_root.resolve()
    destination = output.resolve()
    try:
        if validation_evidence is None:
            raise ValueError(
                "external validation evidence is required; packaging never executes validator code from the target tree"
            )
        gates, digest = load_validation_evidence(validation_evidence, root)
        count = zip_skill(root, destination)
    except Exception as exc:
        failure = GateResult(
            name="external-validation-evidence",
            command=[],
            returncode=1,
            stdout="",
            stderr=str(exc),
        )
        return PackageResult(str(root), str(destination), "fail", [failure], 0, "")
    return PackageResult(str(root), str(destination), "pass", gates, count, digest)


def to_jsonable(result: PackageResult) -> dict[str, Any]:
    return {
        "target": result.target,
        "output": result.output,
        "status": result.status,
        "packaged_files": result.packaged_files,
        "target_tree_sha256": result.target_tree_sha256,
        "gates": [asdict(gate) | {"status": gate.status} for gate in result.gates],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Package nomia from externally produced validation evidence without executing target validators."
    )
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="Path to the nomia skill root.")
    parser.add_argument("--output", help="Destination zip path. Use skill.zip as the file name for release packaging.")
    parser.add_argument("--validation-evidence", help="External JSON evidence for the exact target tree digest.")
    parser.add_argument("--json-output", help="Optional path for machine-readable package evidence.")
    parser.add_argument("--print-tree-digest", action="store_true", help="Print the package tree SHA-256 and exit.")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if args.print_tree_digest:
        try:
            print(tree_digest(target))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        return 0

    if not args.output:
        print("ERROR: --output is required", file=sys.stderr)
        return 2
    if Path(args.output).name != "skill.zip":
        print("ERROR: output file name must be exactly skill.zip", file=sys.stderr)
        return 2
    if not args.validation_evidence:
        print("ERROR: --validation-evidence is required", file=sys.stderr)
        return 2

    result = validate_and_package(target, Path(args.output), Path(args.validation_evidence))
    payload = to_jsonable(result)
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status: {result.status}")
    print(f"target: {result.target}")
    print(f"output: {result.output}")
    if result.target_tree_sha256:
        print(f"target_tree_sha256: {result.target_tree_sha256}")
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
