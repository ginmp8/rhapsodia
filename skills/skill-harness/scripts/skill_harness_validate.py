#!/usr/bin/env python3
"""Validate structural readiness of a ChatGPT or Agent skill package."""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INVENTORY_PATH = SCRIPT_DIR / "skill_harness_inventory.py"
sys.dont_write_bytecode = True
ALLOWED_SCENARIO_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
REQUIRED_SCENARIO_FIELDS = {"id", "type", "prompt", "expected_behavior", "acceptance_criteria"}
REQUIRED_SCENARIO_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
UNRESOLVED_MARKERS = (
    "[" + "TO" + "DO",
    "TO" + "DO:",
    "T" + "BD:",
    "FI" + "XME",
    "REPLACE" + "_ME",
)


def load_inventory_module():
    spec = importlib.util.spec_from_file_location("skill_harness_inventory", INVENTORY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def add_gate(gates, name, passed, severity="blocker", detail=""):
    gates.append({"name": name, "passed": bool(passed), "severity": severity, "detail": detail})


def validate_scenarios(target):
    gates = []
    details = []
    scenario_files = sorted((target / "evals").glob("*.json")) if (target / "evals").exists() else []
    add_gate(gates, "scenario_files_present", bool(scenario_files), "major", f"count={len(scenario_files)}")

    for path in scenario_files:
        rel = path.relative_to(target).as_posix()
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            add_gate(gates, f"scenario_json_valid:{rel}", False, detail=str(exc))
            continue
        add_gate(gates, f"scenario_json_valid:{rel}", True, detail="valid JSON")
        scenarios = data.get("scenarios")
        add_gate(gates, f"scenario_array_present:{rel}", isinstance(scenarios, list) and bool(scenarios), detail=f"count={len(scenarios) if isinstance(scenarios, list) else 0}")
        if not isinstance(scenarios, list):
            continue
        seen_ids = set()
        type_counts = {}
        invalid_items = []
        duplicate_ids = []
        for index, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                invalid_items.append(f"index {index} is not an object")
                continue
            sid = scenario.get("id")
            stype = scenario.get("type")
            missing = sorted(REQUIRED_SCENARIO_FIELDS - set(scenario))
            if missing:
                invalid_items.append(f"{sid or 'index ' + str(index)} missing {missing}")
            if sid in seen_ids:
                duplicate_ids.append(sid)
            if sid:
                seen_ids.add(sid)
            if stype not in ALLOWED_SCENARIO_TYPES:
                invalid_items.append(f"{sid or 'index ' + str(index)} has invalid type {stype!r}")
            else:
                type_counts[stype] = type_counts.get(stype, 0) + 1
            criteria = scenario.get("acceptance_criteria")
            if not isinstance(criteria, list) or not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
                invalid_items.append(f"{sid or 'index ' + str(index)} has invalid acceptance_criteria")
        missing_types = sorted(REQUIRED_SCENARIO_TYPES - set(type_counts))
        add_gate(gates, f"scenario_ids_unique:{rel}", not duplicate_ids, detail=f"duplicates={duplicate_ids}")
        add_gate(gates, f"scenario_items_valid:{rel}", not invalid_items, detail="; ".join(invalid_items) if invalid_items else "all items valid")
        add_gate(gates, f"scenario_required_type_coverage:{rel}", not missing_types, "major", detail=f"missing={missing_types}; counts={type_counts}")
        details.append({"path": rel, "count": len(scenarios), "type_counts": type_counts, "status": data.get("status", "unknown")})
    return gates, details


def validate_scripts(target):
    gates = []
    scripts = sorted((target / "scripts").glob("*.py")) if (target / "scripts").exists() else []
    add_gate(gates, "python_scripts_present", bool(scripts), "major", f"count={len(scripts)}")
    for script in scripts:
        rel = script.relative_to(target).as_posix()
        try:
            compile(read_text(script), str(script), "exec")
            add_gate(gates, f"python_syntax:{rel}", True, detail="compiled without bytecode output")
        except SyntaxError as exc:
            detail = f"{exc.filename}:{exc.lineno}:{exc.offset}: {exc.msg}"
            add_gate(gates, f"python_syntax:{rel}", False, detail=detail)
    return gates


def validate_text_placeholders(inv):
    gates = []
    add_gate(gates, "no_inventory_placeholders", not inv.get("placeholders"), detail=f"placeholders={inv.get('placeholders', [])}")
    return gates


def iter_text_files(target):
    skip_parts = {".git", "__pycache__"}
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if any(part in skip_parts for part in path.parts):
            continue
        if path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip"}:
            continue
        yield path


def validate_template_assets(target):
    gates = []
    text_files = list(iter_text_files(target))
    text_by_path = {path: read_text(path) for path in text_files}
    combined = "\n".join(text_by_path.values())

    referenced = sorted(set(re.findall(r"assets/templates/[A-Za-z0-9_.-]+\.template", combined)))
    existing = sorted(
        path.relative_to(target).as_posix()
        for path in (target / "assets" / "templates").glob("*.template")
    ) if (target / "assets" / "templates").exists() else []

    missing = [rel for rel in referenced if not (target / rel).exists()]
    unintegrated = []
    for rel in existing:
        rel_mentions = 0
        for path, text in text_by_path.items():
            if path.relative_to(target).as_posix() == rel:
                continue
            if rel in text:
                rel_mentions += 1
        if rel_mentions == 0:
            unintegrated.append(rel)

    add_gate(
        gates,
        "referenced_template_assets_exist",
        not missing,
        detail=f"missing={missing}; referenced_count={len(referenced)}",
    )
    add_gate(
        gates,
        "template_assets_integrated",
        not unintegrated,
        "major",
        detail=f"unintegrated={unintegrated}; existing_count={len(existing)}",
    )
    return gates


def validate_package(target):
    target = Path(target).resolve()
    inv_mod = load_inventory_module()
    inv = inv_mod.inventory(target)
    gates = []
    add_gate(gates, "target_exists", inv.get("exists"), detail=str(target))
    add_gate(gates, "exactly_one_skill_md", inv.get("skill_md_count") == 1, detail=f"count={inv.get('skill_md_count')}")
    add_gate(gates, "frontmatter_name", bool(inv.get("frontmatter", {}).get("name")), detail="frontmatter name exists")
    description = inv.get("frontmatter", {}).get("description", "") or ""
    add_gate(gates, "frontmatter_description", bool(description), detail="frontmatter description exists")
    add_gate(gates, "frontmatter_description_specific", len(description) >= 120 and any(term in description.lower() for term in ["use when", "when asked", "supports"]), "major", detail=f"length={len(description)}")
    add_gate(gates, "frontmatter_negative_boundary", any(term in description.lower() for term in ["do not use", "unless", "not use"]), "major", detail="negative trigger language present")
    add_gate(gates, "no_missing_references", not inv.get("missing_references"), detail=f"missing={inv.get('missing_references', [])}")
    gates.extend(validate_text_placeholders(inv))
    gates.extend(validate_template_assets(target))
    scenario_gates, scenario_details = validate_scenarios(target)
    gates.extend(scenario_gates)
    gates.extend(validate_scripts(target))

    blocker_failures = [gate for gate in gates if not gate["passed"] and gate["severity"] == "blocker"]
    major_failures = [gate for gate in gates if not gate["passed"] and gate["severity"] == "major"]
    verdict = "reject" if blocker_failures else ("accept with risks" if major_failures else "accept")
    return {
        "target": str(target),
        "verdict": verdict,
        "gates": gates,
        "scenario_details": scenario_details,
        "inventory_summary": {
            "file_count": inv.get("file_count"),
            "skill_md_count": inv.get("skill_md_count"),
            "missing_references": inv.get("missing_references"),
            "placeholders": inv.get("placeholders"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Validate a ChatGPT or Agent skill package.")
    parser.add_argument("--target", required=True, help="Path to target skill folder")
    parser.add_argument("--output", help="Path to write JSON validation report")
    args = parser.parse_args()
    report = validate_package(args.target)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    raise SystemExit(0 if report["verdict"] in {"accept", "accept with risks"} else 1)


if __name__ == "__main__":
    main()
