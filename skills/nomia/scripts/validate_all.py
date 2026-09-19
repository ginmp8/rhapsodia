#!/usr/bin/env python3
"""Run the complete reproducible Nomia validation ledger."""

from __future__ import annotations

import argparse
import json
import hashlib
import os
import re
import subprocess
import sys

# Keep validation and packaging read-only with respect to the source tree.
sys.dont_write_bytecode = True
import sysconfig
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from nomia_utils import atomic_write_text

PROTECTED_HASH_RE = re.compile(
    r"(?:current )?protected file hash changed for (?P<path>[^:]+):(?: expected [0-9a-f]{64}, got| historical [0-9a-f]{64}, current) (?P<actual>[0-9a-f]{64})"
)


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


def root_cause_id(gate: Gate) -> str | None:
    if gate.returncode == 0:
        return None
    combined = f"{gate.stdout}\n{gate.stderr}"
    match = PROTECTED_HASH_RE.search(combined)
    if match:
        return f"protected-file-hash-drift:{match.group('path')}:{match.group('actual')[:12]}"
    normalized = " ".join(line.strip() for line in combined.splitlines() if line.strip())[:500]
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12] if normalized else "no-output"
    return f"independent-gate-failure:{gate.name}:{digest}"


def summarize_root_causes(gates: list[Gate]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    for gate in gates:
        cause = root_cause_id(gate)
        if cause:
            grouped.setdefault(cause, []).append(gate.name)
    return [
        {"root_cause_id": cause, "impacted_gates": sorted(names), "gate_count": len(names)}
        for cause, names in sorted(grouped.items())
    ]


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    env = environment(root)
    commands = [
        ("package-structure", script(root, "validate_skill_package.py", "--target", str(root))),
        ("activation-scenarios", script(root, "validate_activation_scenarios.py", str(root / "examples" / "activation-scenarios.json"))),
        ("governance-scenarios", script(root, "validate_governance_scenarios.py", str(root / "evals" / "governance-scenarios.json"))),
        ("golden-examples", script(root, "validate_golden_examples.py", "--skill-root", str(root))),
        ("identity-contract", script(root, "validate_identity_contract.py", "--target", str(root))),
        ("priority-contract", script(root, "validate_priority_contract.py", "--target", str(root))),
        ("ecosystem-handoff-contract", script(root, "validate_ecosystem_handoff_contract.py", "--target", str(root))),
        ("ecosystem-compatibility", script(root, "validate_ecosystem_compatibility.py", "--target", str(root))),
        ("ecosystem-routing", script(root, "validate_ecosystem_routing_contract.py", "--target", str(root))),
        ("shared-contract-provenance", script(root, "validate_shared_contract_provenance.py", "--target", str(root))),
        ("ecosystem-release-metadata", script(root, "validate_ecosystem_release_metadata.py", "--target", str(root))),
        ("contract-semantics", script(root, "validate_contract_semantics.py", "--target", str(root))),
        ("release-contract", script(root, "validate_release_contract.py", "--target", str(root))),
        ("contract-preservation", script(root, "validate_contract_preservation.py", "--target", str(root))),
        ("documentation-links", script(root, "validate_documentation.py", "--target", str(root))),
        ("assurance-contract", script(root, "validate_assurance_contract.py", "--target", str(root))),
        ("unit-tests", [sys.executable, "-S", "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py"]),
    ]
    gates = [run(name, command, env) for name, command in commands]
    assurance = summarize_assurance(root, gates)
    gate_results = [asdict(gate) | {"status": gate.status, "root_cause_id": root_cause_id(gate)} for gate in gates]
    root_causes = summarize_root_causes(gates)
    return {
        "target": str(root),
        "status": "pass" if all(gate.returncode == 0 for gate in gates) and assurance["status"] == "pass" else "fail",
        "gate_count": len(gates),
        "failed_gate_count": sum(gate.returncode != 0 for gate in gates),
        "root_cause_count": len(root_causes),
        "root_causes": root_causes,
        "gates": gate_results,
        "assurance": assurance,
    }



def summarize_assurance(root: Path, gates: list[Gate]) -> dict[str, Any]:
    contract_path = root / "references" / "assurance-contract.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "fail", "error": str(exc), "claims": []}
    gate_status = {gate.name: gate.status for gate in gates}
    claims: list[dict[str, Any]] = []
    supported = True
    for claim in contract.get("claims", []):
        evidence_status = claim.get("evidence_status")
        ledger_gates = claim.get("ledger_gates", [])
        mapped = {name: gate_status.get(name, "not-run") for name in ledger_gates}
        if evidence_status == "planned":
            result = "planned"
        elif ledger_gates and all(status == "pass" for status in mapped.values()):
            result = "supported"
        elif evidence_status == "observed" and not ledger_gates:
            result = "observed"
        else:
            result = "unsupported"
            supported = False
        claims.append({
            "id": claim.get("id"),
            "evidence_status": evidence_status,
            "result": result,
            "ledger_gates": mapped,
            "limitations": claim.get("limitations", []),
        })
    return {
        "status": "pass" if supported else "fail",
        "claim_count": len(claims),
        "supported_claims": sum(item["result"] in {"supported", "observed"} for item in claims),
        "planned_claims": sum(item["result"] == "planned" for item in claims),
        "behavioral_activation_measured": False,
        "claims": claims,
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
