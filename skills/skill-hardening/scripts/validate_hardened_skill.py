#!/usr/bin/env python3
"""Validate hardening readiness gates for a ChatGPT skill folder."""

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
from inventory_skill import parse_frontmatter, read_text  # noqa: E402
from package_skill import validate_archive, validate_folder  # noqa: E402


def _load_scenario_items(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], str(exc)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)], None
    if isinstance(data, dict) and isinstance(data.get("scenarios"), list):
        return [item for item in data["scenarios"] if isinstance(item, dict)], None
    return [], "scenario file must be a list or an object with a scenarios list"


def scenario_summary(target: Path) -> dict[str, Any]:
    paths = [
        target / "examples" / "hardening-scenarios.json",
        target / "evals" / "activation-scenarios.json",
    ]
    categories: dict[str, int] = {}
    files: list[dict[str, Any]] = []
    total = 0
    errors: list[str] = []
    required_fields = {"id", "category", "prompt", "expected_behavior"}
    ids: set[str] = set()

    for path in paths:
        if not path.exists():
            files.append({"path": str(path), "exists": False, "count": 0})
            continue
        items, error = _load_scenario_items(path)
        if error:
            errors.append(f"{path}: {error}")
        file_categories: dict[str, int] = {}
        for item in items:
            missing = sorted(required_fields - set(item))
            if missing:
                errors.append(f"{path}: scenario {item.get('id', '<missing-id>')} missing fields {missing}")
            sid = str(item.get("id", ""))
            if sid in ids:
                errors.append(f"{path}: duplicate scenario id {sid}")
            if sid:
                ids.add(sid)
            category = str(item.get("category", "unknown"))
            categories[category] = categories.get(category, 0) + 1
            file_categories[category] = file_categories.get(category, 0) + 1
        total += len(items)
        files.append({"path": str(path), "exists": True, "count": len(items), "categories": file_categories})

    return {
        "paths": files,
        "exists": any(item.get("exists") for item in files),
        "count": total,
        "categories": categories,
        "errors": errors,
    }


def frontmatter_is_minimal(target: Path) -> tuple[bool, str]:
    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md missing"
    data = parse_frontmatter(read_text(skill_md))
    keys = set(data)
    expected = {"name", "description"}
    values_lower = all(value == value.lower() for value in data.values())
    passed = keys == expected and values_lower and bool(data.get("name")) and bool(data.get("description"))
    return passed, f"keys={sorted(keys)}, lowercase_values={values_lower}"


def run_validation(target: Path, min_score: int, package_output: str | None = None) -> dict:
    audit = audit_target(target)
    gates = list(audit["gates"])

    inv = audit["inventory"]
    scripts = inv.get("scripts", [])
    templates = inv.get("templates", [])
    references = inv.get("references", [])
    examples = inv.get("examples", [])
    unreferenced = inv.get("unreferenced_resources", [])
    placeholder_hits = inv.get("placeholder_hits", [])
    folder_errors = validate_folder(target)
    scenarios = scenario_summary(target)
    minimal_frontmatter_passed, minimal_frontmatter_evidence = frontmatter_is_minimal(target)

    gates.append({
        "name": "minimum_score",
        "passed": audit["total_score"] >= min_score,
        "severity": "major",
        "evidence": f"score {audit['total_score']} / 100, required {min_score}",
    })
    gates.append({
        "name": "resource_layer_present",
        "passed": bool(references or scripts or templates or examples),
        "severity": "major",
        "evidence": f"references={len(references)}, scripts={len(scripts)}, templates={len(templates)}, examples={len(examples)}",
    })
    gates.append({
        "name": "script_or_validation_present",
        "passed": bool(scripts) or bool(inv.get("has_validation")),
        "severity": "major",
        "evidence": f"scripts={len(scripts)}, has_validation={inv.get('has_validation')}",
    })
    gates.append({
        "name": "minimal_frontmatter",
        "passed": minimal_frontmatter_passed,
        "severity": "major",
        "evidence": minimal_frontmatter_evidence,
    })
    gates.append({
        "name": "package_builder_present",
        "passed": "scripts/package_skill.py" in scripts,
        "severity": "major",
        "evidence": "scripts/package_skill.py present" if "scripts/package_skill.py" in scripts else "scripts/package_skill.py missing",
    })
    gates.append({
        "name": "folder_package_validation",
        "passed": not folder_errors,
        "severity": "blocker",
        "evidence": "folder package checks passed" if not folder_errors else "; ".join(folder_errors[:5]),
    })
    gates.append({
        "name": "scenario_suite_present",
        "passed": scenarios.get("exists") and scenarios.get("count", 0) >= 20 and len(scenarios.get("categories", {})) >= 4 and not scenarios.get("errors"),
        "severity": "minor",
        "evidence": f"count={scenarios.get('count')}, categories={scenarios.get('categories')}, errors={len(scenarios.get('errors', []))}",
    })
    gates.append({
        "name": "unreferenced_resource_budget",
        "passed": len(unreferenced) <= 3,
        "severity": "minor",
        "evidence": f"unreferenced resources={len(unreferenced)}",
    })
    gates.append({
        "name": "no_residual_scaffold_markers",
        "passed": len(placeholder_hits) == 0,
        "severity": "blocker",
        "evidence": f"marker hits={len(placeholder_hits)}",
    })

    package_result = None
    if package_output:
        package_result = validate_archive(Path(package_output))
        gates.append({
            "name": "package_output_valid",
            "passed": package_result.get("status") == "pass",
            "severity": "blocker",
            "evidence": "archive validation passed" if package_result.get("status") == "pass" else "; ".join(package_result.get("errors", [])[:5]),
        })

    blocker_failed = [g for g in gates if not g["passed"] and g["severity"] == "blocker"]
    major_failed = [g for g in gates if not g["passed"] and g["severity"] == "major"]
    status = "pass" if not blocker_failed and not major_failed else "fail"
    return {
        "target_path": str(target.resolve()),
        "status": status,
        "score": audit["total_score"],
        "min_score": min_score,
        "gates": gates,
        "audit_verdict": audit["verdict"],
        "scenario_summary": scenarios,
        "package_output": package_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a hardened ChatGPT skill folder.")
    parser.add_argument("--target", required=True, help="Path to the target skill folder.")
    parser.add_argument("--min-score", type=int, default=85, help="Minimum hardening audit score. Default: 85.")
    parser.add_argument("--package-output", help="Optional skill.zip path to validate as part of readiness.")
    parser.add_argument("--json-output", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        print(f"ERROR: target is not a directory: {target}", file=sys.stderr)
        return 2

    result = run_validation(target, args.min_score, args.package_output)
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")

    print(f"status: {result['status']}")
    print(f"score: {result['score']}/100")
    for gate in result["gates"]:
        status = "pass" if gate["passed"] else "fail"
        print(f"{status}: {gate['name']} ({gate['severity']}) - {gate['evidence']}")

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
