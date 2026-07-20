#!/usr/bin/env python3
"""Validate and package the nomia skill as an installable skill.zip."""

from __future__ import annotations

import argparse
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
SAFE_INHERITED_ENV_KEYS = {
    "LANG",
    "LC_ALL",
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
    "WINDIR",
}


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
    env = {key: value for key, value in os.environ.items() if key in SAFE_INHERITED_ENV_KEYS}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
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


def trusted_skill_root() -> Path:
    """Return the skill root that owns this packaging script."""
    return Path(__file__).resolve().parents[1]


def validate_target(skill_root: Path) -> Path:
    """Reject packaging a different target with validators controlled by that target."""
    root = skill_root.resolve()
    trusted_root = trusted_skill_root()
    if root != trusted_root:
        raise ValueError(
            f"refusing external target `{root}`; run the package script bundled with that skill root"
        )
    return root


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
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def zip_skill(skill_root: Path, output: Path) -> int:
    root = skill_root.resolve()
    destination = output.resolve()
    try:
        destination.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("output zip must be outside the skill folder to avoid packaging itself")

    files = [path for path in sorted(root.rglob("*")) if should_package(path, root)]
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


def validate_and_package(skill_root: Path, output: Path) -> PackageResult:
    root = validate_target(skill_root)
    env = python_env(root)
    gates = [
        run_gate("package-structure", command(root, "validate_skill_package.py", "--target", str(root)), env),
        run_gate("activation-scenarios", command(root, "validate_activation_scenarios.py", str(root / "examples" / "activation-scenarios.json")), env),
        run_gate("golden-examples", command(root, "validate_golden_examples.py", "--skill-root", str(root)), env),
        run_gate("identity-contract", command(root, "validate_identity_contract.py", "--target", str(root)), env),
        run_gate("contract-preservation", command(root, "validate_contract_preservation.py", "--target", str(root)), env),
        run_gate(
            "unit-tests",
            [sys.executable, "-S", "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py"],
            env,
        ),
    ]
    if any(gate.returncode != 0 for gate in gates):
        return PackageResult(str(root), str(output.resolve()), "fail", gates, 0)
    count = zip_skill(root, output)
    return PackageResult(str(root), str(output.resolve()), "pass", gates, count)


def to_jsonable(result: PackageResult) -> dict[str, Any]:
    return {
        "target": result.target,
        "output": result.output,
        "status": result.status,
        "packaged_files": result.packaged_files,
        "gates": [asdict(gate) | {"status": gate.status} for gate in result.gates],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and package nomia as skill.zip.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="Path to the nomia skill root.")
    parser.add_argument("--output", required=True, help="Destination zip path. Use skill.zip as the file name for release packaging.")
    parser.add_argument("--json-output", help="Optional path for machine-readable package evidence.")
    args = parser.parse_args(argv)

    if Path(args.output).name != "skill.zip":
        print("ERROR: output file name must be exactly skill.zip", file=sys.stderr)
        return 2

    try:
        result = validate_and_package(Path(args.target), Path(args.output))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload = to_jsonable(result)
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

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
