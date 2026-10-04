#!/usr/bin/env python3
"""Validate claim-sensitive hardening readiness gates for an Agent Skills package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hardening_audit import audit_target  # noqa: E402
from package_skill import SUPPORTED_PROFILES, validate_archive, validate_folder  # noqa: E402

CORE_SCENARIO_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
ALLOWED_SCENARIO_TYPES = CORE_SCENARIO_TYPES | {"regression", "adversarial", "coexistence", "semantic_collision"}


def _load_scenario_items(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [], str(exc)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)], None
    if isinstance(data, dict) and isinstance(data.get("scenarios"), list):
        return [item for item in data["scenarios"] if isinstance(item, dict)], None
    return [], "scenario file must be a list or an object with a scenarios list"


def scenario_summary(target: Path) -> dict[str, Any]:
    paths = [target / "examples" / "hardening-scenarios.json", target / "evals" / "activation-scenarios.json"]
    types: dict[str, int] = {}
    files: list[dict[str, Any]] = []
    total = 0
    errors: list[str] = []
    required_fields = {"id", "type", "prompt", "expected_behavior", "acceptance_criteria"}
    ids: set[str] = set()
    for path in paths:
        if not path.exists():
            files.append({"path": str(path), "exists": False, "count": 0})
            continue
        items, error = _load_scenario_items(path)
        if error:
            errors.append(f"{path}: {error}")
        file_types: dict[str, int] = {}
        for item in items:
            missing = sorted(required_fields - set(item))
            if missing:
                errors.append(f"{path}: scenario {item.get('id', '<missing-id>')} missing fields {missing}")
            sid = str(item.get("id", ""))
            if sid and sid in ids:
                errors.append(f"{path}: duplicate scenario id {sid}")
            if sid:
                ids.add(sid)
            scenario_type = str(item.get("type", "unknown"))
            if scenario_type not in ALLOWED_SCENARIO_TYPES:
                errors.append(f"{path}: scenario {sid or '<missing-id>'} has invalid type {scenario_type!r}")
            else:
                types[scenario_type] = types.get(scenario_type, 0) + 1
                file_types[scenario_type] = file_types.get(scenario_type, 0) + 1
            criteria = item.get("acceptance_criteria")
            if not isinstance(criteria, list) or not criteria or not all(isinstance(value, str) and value.strip() for value in criteria):
                errors.append(f"{path}: scenario {sid or '<missing-id>'} has invalid acceptance_criteria")
        total += len(items)
        files.append({"path": str(path), "exists": True, "count": len(items), "types": file_types})
    return {
        "paths": files,
        "exists": any(item.get("exists") for item in files),
        "count": total,
        "types": types,
        "missing_required_types": sorted(CORE_SCENARIO_TYPES - set(types)),
        "errors": errors,
    }


def run_validation(
    target: Path,
    min_score: int,
    package_output: str | None = None,
    profile: str = "portable",
    require_scenarios: bool = False,
    scenario_min_per_core_type: int = 1,
    require_coexistence: bool = False,
    hosts: list[str] | None = None,
) -> dict[str, Any]:
    target = Path(target).resolve()
    audit = audit_target(target)
    gates = list(audit["gates"])
    inv = audit["inventory"]
    unreferenced = inv.get("unreferenced_resources", [])
    placeholder_hits = inv.get("placeholder_hits", [])
    folder_errors = validate_folder(target, profile=profile)
    scenarios = scenario_summary(target)

    gates.append({
        "name": "minimum_score",
        "passed": audit["total_score"] >= min_score,
        "severity": "major",
        "evidence": f"structural score {audit['total_score']} / 100, required {min_score}",
    })
    gates.append({
        "name": "folder_package_validation",
        "passed": not folder_errors,
        "severity": "blocker",
        "evidence": "folder package checks passed" if not folder_errors else "; ".join(folder_errors[:5]),
    })
    gates.append({
        "name": "unreferenced_resource_budget",
        "passed": len(unreferenced) <= 3,
        "severity": "minor",
        "evidence": f"unreferenced resources={len(unreferenced)}; optional resources are not required by presence",
    })
    gates.append({
        "name": "no_residual_scaffold_markers",
        "passed": len(placeholder_hits) == 0,
        "severity": "blocker",
        "evidence": f"marker hits={len(placeholder_hits)}",
    })

    if require_scenarios:
        missing_counts = sorted(t for t in CORE_SCENARIO_TYPES if scenarios["types"].get(t, 0) < scenario_min_per_core_type)
        gates.append({
            "name": "scenario_coverage",
            "passed": scenarios["exists"] and not scenarios["errors"] and not missing_counts,
            "severity": "major",
            "evidence": f"min_per_core_type={scenario_min_per_core_type}, types={scenarios['types']}, missing={missing_counts}, errors={len(scenarios['errors'])}",
        })
    else:
        gates.append({
            "name": "scenario_coverage",
            "passed": True,
            "severity": "minor",
            "evidence": "not required for this structural claim; scenario sufficiency must be predeclared when behavioral evidence is claimed",
        })

    if require_coexistence:
        coexistence_ok = scenarios["types"].get("coexistence", 0) > 0 and scenarios["types"].get("semantic_collision", 0) > 0
        gates.append({
            "name": "scenario_coexistence",
            "passed": coexistence_ok,
            "severity": "major",
            "evidence": f"coexistence={scenarios['types'].get('coexistence', 0)}, semantic_collision={scenarios['types'].get('semantic_collision', 0)}",
        })

    portability_result = None
    if hosts:
        try:
            from validate_portability import validate_portability  # noqa: E402
            portability_result = validate_portability(target, hosts)
            gates.append({
                "name": "portability_profiles",
                "passed": portability_result.get("status") == "pass",
                "severity": "blocker",
                "evidence": f"profiles={hosts}, status={portability_result.get('status')}",
            })
        except (ImportError, ValueError) as exc:
            portability_result = {"status": "fail", "errors": [str(exc)]}
            gates.append({"name": "portability_profiles", "passed": False, "severity": "blocker", "evidence": str(exc)})

    package_result = None
    if package_output:
        package_result = validate_archive(Path(package_output), profile=profile)
        gates.append({
            "name": "package_output_valid",
            "passed": package_result.get("status") == "pass",
            "severity": "blocker",
            "evidence": "archive validation passed" if package_result.get("status") == "pass" else "; ".join(package_result.get("errors", [])[:5]),
        })

    blocker_failed = [item for item in gates if not item["passed"] and item["severity"] == "blocker"]
    major_failed = [item for item in gates if not item["passed"] and item["severity"] == "major"]
    status = "pass" if not blocker_failed and not major_failed else "fail"
    return {
        "target_path": str(target.resolve()),
        "status": status,
        "score": audit["total_score"],
        "score_layer": "structural",
        "min_score": min_score,
        "profile": profile,
        "gates": gates,
        "audit_verdict": audit["verdict"],
        "scenario_summary": scenarios,
        "portability": portability_result,
        "package_output": package_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a hardened Agent Skills-compatible folder.")
    parser.add_argument("--target", required=True, help="Path to the target skill folder.")
    parser.add_argument("--min-score", type=int, default=85, help="Minimum structural hardening score. Default: 85.")
    parser.add_argument("--profile", choices=sorted(SUPPORTED_PROFILES), default="portable")
    parser.add_argument("--package-output", help="Optional skill.zip path to validate as part of readiness.")
    parser.add_argument("--require-scenarios", action="store_true", help="Require the four core scenario categories.")
    parser.add_argument("--scenario-min-per-core-type", type=int, default=1)
    parser.add_argument("--require-coexistence", action="store_true", help="Require coexistence and semantic-collision scenarios.")
    parser.add_argument("--hosts", help="Comma-separated portability profiles to validate structurally.")
    parser.add_argument("--json-output", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        print(f"ERROR: target is not a directory: {target}", file=sys.stderr)
        return 2
    if args.scenario_min_per_core_type < 1:
        print("ERROR: --scenario-min-per-core-type must be >= 1", file=sys.stderr)
        return 2
    hosts = [item.strip() for item in args.hosts.split(",") if item.strip()] if args.hosts else None
    result = run_validation(
        target,
        args.min_score,
        args.package_output,
        profile=args.profile,
        require_scenarios=args.require_scenarios,
        scenario_min_per_core_type=args.scenario_min_per_core_type,
        require_coexistence=args.require_coexistence,
        hosts=hosts,
    )
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    print(f"status: {result['status']}")
    print(f"score: {result['score']}/100 (structural)")
    for gate in result["gates"]:
        state = "pass" if gate["passed"] else "fail"
        print(f"{state}: {gate['name']} ({gate['severity']}) - {gate['evidence']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
