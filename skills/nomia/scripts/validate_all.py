#!/usr/bin/env python3
"""Run the complete reproducible Nomia validation ledger."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import sysconfig
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from nomia_utils import atomic_write_text


@dataclass
class Gate:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def status(self) -> str:
        return "pass" if self.returncode == 0 else "fail"


def environment(root: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    paths = [str(root / "scripts")]
    for candidate in (
        sysconfig.get_paths().get("purelib"),
        sysconfig.get_paths().get("platlib"),
        env.get("PYTHONPATH"),
    ):
        if candidate:
            paths.extend(str(candidate).split(os.pathsep))
    env["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(value for value in paths if value))
    return env


def script(root: Path, name: str, *args: str) -> list[str]:
    return [sys.executable, "-S", str(root / "scripts" / name), *args]


def run(name: str, command: list[str], env: dict[str, str]) -> Gate:
    completed = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    return Gate(name, command, completed.returncode, completed.stdout.strip(), completed.stderr.strip())


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    env = environment(root)
    commands = [
        ("package-structure", script(root, "validate_skill_package.py", "--target", str(root))),
        ("activation-scenarios", script(root, "validate_activation_scenarios.py", str(root / "examples" / "activation-scenarios.json"))),
        ("governance-scenarios", script(root, "validate_governance_scenarios.py", str(root / "evals" / "governance-scenarios.json"))),
        ("golden-examples", script(root, "validate_golden_examples.py", "--skill-root", str(root))),
        ("identity-contract", script(root, "validate_identity_contract.py", "--target", str(root))),
        ("contract-preservation", script(root, "validate_contract_preservation.py", "--target", str(root))),
        ("unit-tests", [sys.executable, "-S", "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py"]),
    ]
    gates = [run(name, command, env) for name, command in commands]
    return {
        "target": str(root),
        "status": "pass" if all(gate.returncode == 0 for gate in gates) else "fail",
        "gate_count": len(gates),
        "gates": [asdict(gate) | {"status": gate.status} for gate in gates],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run every required Nomia validation gate.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate(Path(args.target))
    if args.json_output:
        path = Path(args.json_output).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(path, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"status: {result['status']}")
    print(f"target: {result['target']}")
    for gate in result["gates"]:
        print(f"{gate['status']}: {gate['name']}")
        for stream in ("stdout", "stderr"):
            if gate[stream]:
                for line in gate[stream].splitlines():
                    print(f"  {stream}: {line}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
