#!/usr/bin/env python3
"""Validate a non-authoritative Mago traceability projection."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

PREFIX_KIND = {"REQ-": "requirements", "AC-": "acceptance", "DECISION-": "decisions", "task": "tasks", "VAL-": "validations"}
LINK_KIND = {"requirements": "REQ-", "acceptance": "AC-", "decisions": "DECISION-", "tasks": "task", "validations": "VAL-"}

def kind(identifier: str) -> str | None:
    for prefix, value in PREFIX_KIND.items():
        if identifier.startswith(prefix):
            return value
    return None

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("projection")
    ap.add_argument("--profile", choices=("quick", "standard", "governed"), default="standard")
    ap.add_argument("--json-output")
    args = ap.parse_args()
    data = json.loads(Path(args.projection).read_text(encoding="utf-8"))
    errors = list(data.get("render_errors", []))
    if data.get("authoritative") is not False:
        errors.append("traceability projection must be explicitly non-authoritative")
    records = data.get("records")
    if not isinstance(records, dict):
        errors.append("records must be an object")
        records = {}
    sets = {v: {i for i in records if kind(i) == v} for v in PREFIX_KIND.values()}
    for identifier, links in records.items():
        if kind(identifier) is None:
            errors.append(f"unknown identifier format: {identifier}")
            continue
        if not isinstance(links, dict):
            errors.append(f"{identifier}: links must be an object")
            continue
        for field, values in links.items():
            if field not in LINK_KIND:
                continue
            if not isinstance(values, list):
                errors.append(f"{identifier}: {field} must be a list")
                continue
            for target in values:
                if target not in sets[field]:
                    errors.append(f"{identifier}: unknown {field} link {target}")
    for req in sorted(sets["requirements"]):
        linked_ac = {x for x in sets["acceptance"] if req in records[x].get("requirements", [])}
        linked_dec = {x for x in sets["decisions"] if req in records[x].get("requirements", [])}
        linked_tasks = {x for x in sets["tasks"] if req in records[x].get("requirements", [])}
        linked_vals = {x for x in sets["validations"] if req in records[x].get("requirements", [])}
        if not linked_ac:
            errors.append(f"{req}: missing acceptance link")
        if args.profile == "governed" and not linked_dec:
            errors.append(f"{req}: governed profile requires decision link")
        if not linked_tasks:
            errors.append(f"{req}: missing task link")
        if not linked_vals:
            errors.append(f"{req}: missing validation link")
        for task in linked_tasks:
            if not set(records[task].get("acceptance", [])) & linked_ac:
                errors.append(f"{req}: {task} is not linked to its acceptance criteria")
            if args.profile == "governed" and not set(records[task].get("decisions", [])) & linked_dec:
                errors.append(f"{req}: {task} is not linked to a governed decision")
            if not set(records[task].get("validations", [])) & linked_vals:
                errors.append(f"{req}: {task} is not linked to validation")
    coverage = {
        "requirements": len(sets["requirements"]),
        "acceptance": len(sets["acceptance"]),
        "decisions": len(sets["decisions"]),
        "tasks": len(sets["tasks"]),
        "validations": len(sets["validations"]),
        "complete_requirements": 0,
    }
    for req in sets["requirements"]:
        checks = [
            any(req in records[x].get("requirements", []) for x in sets["acceptance"]),
            any(req in records[x].get("requirements", []) for x in sets["tasks"]),
            any(req in records[x].get("requirements", []) for x in sets["validations"]),
        ]
        if args.profile == "governed":
            checks.append(any(req in records[x].get("requirements", []) for x in sets["decisions"]))
        if all(checks):
            coverage["complete_requirements"] += 1
    coverage["percent"] = round(100 * coverage["complete_requirements"] / max(1, coverage["requirements"]), 2)
    result = {"status": "pass" if not errors else "fail", "profile": args.profile, "coverage": coverage, "errors": errors}
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
