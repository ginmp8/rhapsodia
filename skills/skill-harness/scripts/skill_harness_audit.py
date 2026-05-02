#!/usr/bin/env python3
"""Static audit for a target ChatGPT or Agent skill package used by skill-harness."""
import argparse
import importlib.util
import json
import sys
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INVENTORY_PATH = SCRIPT_DIR / "skill_harness_inventory.py"
sys.dont_write_bytecode = True


def load_inventory_module():
    spec = importlib.util.spec_from_file_location("skill_harness_inventory", INVENTORY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_inventory(target):
    return load_inventory_module().inventory(target)


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def has_section(text, names):
    lowered = text.lower()
    return any(name.lower() in lowered for name in names)


def scenario_files(paths):
    return [p for p in paths if p.startswith("evals/") and p.endswith(".json")]


def score_target(inv):
    target = Path(inv["target"])
    skill_md = target / "SKILL.md"
    text = read_text(skill_md)
    desc = inv.get("frontmatter", {}).get("description", "") or ""
    files = inv.get("files", [])
    paths = {f["path"] for f in files}
    gates = []
    findings = []
    scores = {}

    def gate(name, passed, severity="blocker", detail=""):
        gates.append({"name": name, "passed": bool(passed), "severity": severity, "detail": detail})

    gate("exactly_one_skill_md", inv.get("skill_md_count") == 1, detail=f"count={inv.get('skill_md_count')}")
    gate("frontmatter_name", bool(inv.get("frontmatter", {}).get("name")), detail="frontmatter name exists")
    gate("frontmatter_description", bool(desc), detail="frontmatter description exists")
    gate("description_has_negative_boundary", any(w in desc.lower() for w in ["do not use", "unless", "not use"]), severity="major", detail="description states non-trigger boundary")
    gate("no_placeholders", not inv.get("placeholders"), detail=f"placeholders={len(inv.get('placeholders', []))}")
    gate("no_missing_references", not inv.get("missing_references"), detail=f"missing={inv.get('missing_references', [])}")

    desc_score = 0
    if desc:
        desc_score += 25
        if len(desc) >= 120:
            desc_score += 20
        if any(w in desc.lower() for w in ["use when", "when asked", "supports", "especially"]):
            desc_score += 25
        if any(w in desc.lower() for w in ["do not use", "without", "only when", "unless"]):
            desc_score += 10
        if len(desc) <= 1200:
            desc_score += 20
    scores["scope_and_trigger"] = min(desc_score, 100)

    input_score = 0
    if has_section(text, ["required input", "inputs", "prerequisites"]):
        input_score += 35
    if has_section(text, ["assumption", "evidence", "source"]):
        input_score += 25
    if has_section(text, ["blocked path", "scope", "activation boundaries"]):
        input_score += 30
    if has_section(text, ["final artifact", "target_skill_path"]):
        input_score += 10
    scores["inputs_and_assumptions"] = min(input_score, 100)

    workflow_score = 0
    if has_section(text, ["workflow"]):
        workflow_score += 30
    if re.search(r"\n\s*\d+\.", text):
        workflow_score += 20
    if has_section(text, ["mode", "selection"]):
        workflow_score += 20
    if has_section(text, ["stop condition"]):
        workflow_score += 15
    if has_section(text, ["progressive loading"]):
        workflow_score += 15
    scores["workflow_and_modes"] = min(workflow_score, 100)

    output_score = 0
    if has_section(text, ["output contract", "output contracts"]):
        output_score += 40
    if has_section(text, ["report", "final response", "include"]):
        output_score += 20
    if "assets/templates" in text or any(p.startswith("assets/templates/") for p in paths):
        output_score += 25
    if "package artifact" in text.lower() or "skill.zip" in text:
        output_score += 15
    scores["output_contract"] = min(output_score, 100)

    resource_score = 0
    if inv["top_dirs"].get("references") and any(p.startswith("references/") for p in paths):
        resource_score += 30
    if inv["top_dirs"].get("scripts") and any(p.startswith("scripts/") for p in paths):
        resource_score += 30
    if any(p.startswith("assets/templates/") for p in paths):
        resource_score += 15
    if scenario_files(paths):
        resource_score += 15
    if not inv.get("missing_references"):
        resource_score += 10
    scores["supporting_resources"] = min(resource_score, 100)

    validation_score = 0
    if has_section(text, ["validate", "validation", "gate"]):
        validation_score += 35
    if any("validate" in p or "audit" in p or "inventory" in p or "package" in p for p in paths):
        validation_score += 35
    if has_section(text, ["before/after", "baseline", "compare"]):
        validation_score += 20
    if has_section(text, ["auxiliary metric", "saturated"]):
        validation_score += 10
    scores["validation_and_gates"] = min(validation_score, 100)

    scenarios_score = 0
    if has_section(text, ["scenario"]):
        scenarios_score += 35
    if any("scenario" in p for p in paths):
        scenarios_score += 30
    if scenario_files(paths):
        scenarios_score += 15
    if has_section(text, ["activation", "ambiguous", "edge", "regression", "adversarial"]):
        scenarios_score += 20
    scores["scenario_readiness"] = min(scenarios_score, 100)

    maintainability_score = 100
    if len(text.splitlines()) > 500:
        maintainability_score -= 20
    if len(inv.get("placeholders", [])):
        maintainability_score -= 30
    if inv.get("missing_references"):
        maintainability_score -= 30
    if inv.get("file_count", 0) > 80:
        maintainability_score -= 10
    scores["maintainability"] = max(0, maintainability_score)

    if scores["scope_and_trigger"] < 70:
        findings.append("frontmatter description is not specific enough for reliable activation")
    if not any(w in desc.lower() for w in ["do not use", "unless", "not use"]):
        findings.append("frontmatter description lacks an explicit non-trigger boundary")
    if scores["validation_and_gates"] < 70:
        findings.append("validation and acceptance gates need to be more explicit")
    if scores["scenario_readiness"] < 70:
        findings.append("scenario suite is missing or too weak for behavior evaluation")
    if inv.get("placeholders"):
        findings.append("unresolved placeholders or scaffold content remain")
    if inv.get("missing_references"):
        findings.append("some referenced resources are missing")

    weights = {
        "scope_and_trigger": 15,
        "inputs_and_assumptions": 10,
        "workflow_and_modes": 15,
        "output_contract": 15,
        "supporting_resources": 10,
        "validation_and_gates": 15,
        "scenario_readiness": 10,
        "maintainability": 10,
    }
    total = sum(scores[k] * weights[k] for k in weights) / sum(weights.values())
    blocker_failures = [g for g in gates if not g["passed"] and g["severity"] == "blocker"]
    major_failures = [g for g in gates if not g["passed"] and g["severity"] == "major"]
    verdict = "reject" if blocker_failures else ("accept with risks" if major_failures or total < 85 or findings else "accept")
    return {"score": round(total, 1), "dimension_scores": scores, "gates": gates, "findings": findings, "verdict": verdict}


def markdown(inv, audit):
    lines = []
    lines.append(f"# Skill Harness Audit: {inv.get('frontmatter', {}).get('name') or Path(inv['target']).name}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Target: `{inv['target']}`")
    lines.append(f"- Score: {audit['score']}/100")
    lines.append(f"- Verdict: {audit['verdict']}")
    lines.append(f"- Files: {inv.get('file_count', 0)}")
    lines.append(f"- Placeholders: {len(inv.get('placeholders', []))}")
    lines.append(f"- Missing references: {len(inv.get('missing_references', []))}")
    lines.append("")
    lines.append("## Dimension Scores")
    for name, score in audit["dimension_scores"].items():
        lines.append(f"- {name}: {score}/100")
    lines.append("")
    lines.append("## Gates")
    for gate in audit["gates"]:
        status = "PASS" if gate["passed"] else "FAIL"
        lines.append(f"- {status} [{gate['severity']}] {gate['name']}: {gate['detail']}")
    lines.append("")
    lines.append("## Findings")
    if audit["findings"]:
        for finding in audit["findings"]:
            lines.append(f"- {finding}")
    else:
        lines.append("- no static findings detected")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Static audit results are structural evidence, not a substitute for target-specific scenario execution or domain validation.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Audit a target ChatGPT or Agent skill package for harness readiness.")
    parser.add_argument("--target", required=True, help="Path to target skill folder")
    parser.add_argument("--output", help="Path to write Markdown audit report")
    parser.add_argument("--json-output", help="Path to write JSON audit report")
    args = parser.parse_args()
    inv = run_inventory(args.target)
    audit = score_target(inv)
    data = {"inventory": inv, "audit": audit}
    md = markdown(inv, audit)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
