#!/usr/bin/env python3
"""Audit package-level hardening maturity for a ChatGPT skill."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inventory_skill import inventory  # noqa: E402


DIMENSIONS = [
    "static_structure",
    "package_semantics",
    "resource_integration",
    "validation_behavior",
]


def clamp(value: int, low: int = 0, high: int = 25) -> int:
    return max(low, min(high, value))


def score_inventory(inv: dict) -> tuple[dict[str, int], list[dict], list[dict], list[dict]]:
    gates: list[dict] = []
    findings: list[dict] = []
    improvements: list[dict] = []

    def gate(name: str, passed: bool, evidence: str, severity: str = "blocker") -> None:
        gates.append({"name": name, "passed": passed, "severity": severity, "evidence": evidence})

    skill_md_exists = bool(inv.get("skill_md_exists"))
    name = inv.get("skill_name")
    description = inv.get("description") or ""
    desc_words = len(description.split())
    missing_refs = inv.get("missing_referenced_paths", [])
    placeholder_hits = inv.get("placeholder_hits", [])
    references = inv.get("references", [])
    scripts = inv.get("scripts", [])
    templates = inv.get("templates", [])
    assets = inv.get("assets", [])
    examples = inv.get("examples", [])
    unreferenced = inv.get("unreferenced_resources", [])

    gate("valid_skill_md", skill_md_exists and bool(name) and bool(description), "SKILL.md and required frontmatter present" if skill_md_exists else "SKILL.md missing")
    gate("specific_description", desc_words >= 25, f"description has {desc_words} words", "major")
    gate("references_resolve", len(missing_refs) == 0, f"missing referenced paths: {missing_refs}" if missing_refs else "all referenced paths resolve")
    gate("no_scaffold_placeholders", len(placeholder_hits) == 0, f"placeholder hits: {len(placeholder_hits)}" if placeholder_hits else "no placeholder hits")
    gate("output_contract", bool(inv.get("has_output_contract")), "output contract detected" if inv.get("has_output_contract") else "output contract not detected", "major")
    gate("validation_rules", bool(inv.get("has_validation")), "validation language detected" if inv.get("has_validation") else "validation language not detected", "major")
    gate("minimal_frontmatter", bool(name) and bool(description), "name and description fields detected" if name and description else "missing name or description", "major")
    gate("package_tooling", "scripts/package_skill.py" in scripts, "package builder present" if "scripts/package_skill.py" in scripts else "package builder missing", "major")
    gate("scenario_examples", bool(examples), f"examples={len(examples)}", "minor")

    static = 0
    if skill_md_exists:
        static += 6
    if name and description:
        static += 5
    if "agents/openai.yaml" in inv.get("agents", []):
        static += 3
    if len(inv.get("top_level_dirs", [])) >= 2:
        static += 3
    if not placeholder_hits:
        static += 4
    if inv.get("skill_md_lines", 0) <= 500:
        static += 4

    semantics = 0
    if desc_words >= 25:
        semantics += 5
    if inv.get("has_mode_matrix"):
        semantics += 5
    if inv.get("has_output_contract"):
        semantics += 5
    if inv.get("has_validation"):
        semantics += 5
    if inv.get("has_stop_conditions"):
        semantics += 5

    resource = 0
    if references:
        resource += 5
    if scripts:
        resource += 5
    if templates:
        resource += 4
    if assets and not templates:
        resource += 2
    if not missing_refs:
        resource += 4
    if len(unreferenced) <= 2:
        resource += 4
    if references and scripts and templates:
        resource += 3
    if examples:
        resource += 1

    validation = 0
    if inv.get("has_validation"):
        validation += 6
    if any("validate" in p or "audit" in p or "test" in p for p in scripts):
        validation += 7
    if "scripts/package_skill.py" in scripts:
        validation += 1
    if inv.get("has_output_contract"):
        validation += 4
    if inv.get("has_stop_conditions"):
        validation += 4
    if templates and scripts:
        validation += 2
    if not missing_refs and not placeholder_hits:
        validation += 2

    scores = {
        "static_structure": clamp(static),
        "package_semantics": clamp(semantics),
        "resource_integration": clamp(resource),
        "validation_behavior": clamp(validation),
    }

    if not references:
        findings.append({"severity": "major", "area": "references", "finding": "No reference files found."})
        improvements.append({"priority": 1, "area": "references", "recommendation": "Move detailed or branch-specific rules into referenced files loaded conditionally from SKILL.md."})
    if not scripts:
        findings.append({"severity": "major", "area": "scripts", "finding": "No deterministic helper or validator scripts found."})
        improvements.append({"priority": 2, "area": "scripts", "recommendation": "Add scripts for fragile checks, scaffolding, validation, inventory, or report generation when the workflow repeats."})
    if not templates:
        findings.append({"severity": "minor", "area": "templates", "finding": "No reusable output templates found under assets/templates/."})
        improvements.append({"priority": 3, "area": "templates", "recommendation": "Add templates for repeated report or artifact shapes when the target skill generates durable outputs."})
    if "scripts/package_skill.py" not in scripts:
        findings.append({"severity": "major", "area": "packaging", "finding": "No deterministic package builder found."})
        improvements.append({"priority": 3, "area": "packaging", "recommendation": "Add a package builder and archive validator for skill.zip delivery."})
    if not examples:
        findings.append({"severity": "minor", "area": "examples", "finding": "No concrete scenario examples found."})
        improvements.append({"priority": 7, "area": "examples", "recommendation": "Add activation, non-activation, ambiguous, and edge-case scenario examples."})
    if missing_refs:
        findings.append({"severity": "blocker", "area": "references", "finding": f"Referenced paths are missing: {', '.join(missing_refs)}"})
    if placeholder_hits:
        findings.append({"severity": "blocker", "area": "placeholders", "finding": f"Placeholder text remains in {len(placeholder_hits)} locations."})
    if not inv.get("has_mode_matrix"):
        improvements.append({"priority": 4, "area": "workflow", "recommendation": "Add a mode selection matrix if the skill supports multiple intents or artifact types."})
    if not inv.get("has_stop_conditions"):
        improvements.append({"priority": 5, "area": "safety", "recommendation": "Add stop conditions for missing inputs, unsafe paths, invalid state, and unsupported requests."})
    if unreferenced:
        findings.append({"severity": "minor", "area": "resource_integration", "finding": f"Unreferenced resources: {', '.join(unreferenced[:10])}"})
        improvements.append({"priority": 6, "area": "resource_integration", "recommendation": "Reference useful resources from SKILL.md with loading conditions, or delete unused resources."})

    return scores, gates, findings, improvements


def verdict(total: int, gates: list[dict]) -> str:
    blocker_failed = any((not gate["passed"]) and gate["severity"] == "blocker" for gate in gates)
    major_failed = any((not gate["passed"]) and gate["severity"] == "major" for gate in gates)
    if blocker_failed:
        return "reject"
    if total >= 85 and not major_failed:
        return "approve"
    if total >= 70:
        return "approve_with_reservations"
    return "reject"


def markdown_report(audit: dict) -> str:
    inv = audit["inventory"]
    lines: list[str] = []
    lines.append(f"# Skill Hardening Audit: {inv.get('skill_name') or Path(inv['target_path']).name}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Target: `{inv['target_path']}`")
    lines.append(f"- Score: {audit['total_score']}/100")
    lines.append(f"- Verdict: `{audit['verdict']}`")
    lines.append(f"- References: {len(inv.get('references', []))}; scripts: {len(inv.get('scripts', []))}; templates: {len(inv.get('templates', []))}; examples: {len(inv.get('examples', []))}")
    lines.append("")
    lines.append("## Scorecard")
    lines.append("")
    lines.append("| Layer | Score |")
    lines.append("|---|---:|")
    for key in DIMENSIONS:
        lines.append(f"| {key} | {audit['scores'][key]}/25 |")
    lines.append("")
    lines.append("## Gates")
    lines.append("")
    lines.append("| Gate | Status | Severity | Evidence |")
    lines.append("|---|---|---|---|")
    for gate in audit["gates"]:
        status = "pass" if gate["passed"] else "fail"
        evidence = str(gate["evidence"]).replace("|", "\\|")
        lines.append(f"| {gate['name']} | {status} | {gate['severity']} | {evidence} |")
    lines.append("")
    lines.append("## Resource Inventory")
    lines.append("")
    for label in ["references", "scripts", "templates", "assets", "examples"]:
        values = inv.get(label, [])
        lines.append(f"### {label}")
        lines.append("")
        if values:
            for value in values:
                lines.append(f"- `{value}`")
        else:
            lines.append("- none")
        lines.append("")
    lines.append("## Findings")
    lines.append("")
    if audit["findings"]:
        for item in audit["findings"]:
            lines.append(f"- **{item['severity']} / {item['area']}**: {item['finding']}")
    else:
        lines.append("- No structural findings detected by the static audit.")
    lines.append("")
    lines.append("## Prioritized Improvements")
    lines.append("")
    if audit["improvements"]:
        for item in sorted(audit["improvements"], key=lambda x: x["priority"]):
            lines.append(f"{item['priority']}. **{item['area']}**: {item['recommendation']}")
    else:
        lines.append("- No static improvements suggested. Consider behavioral scenario testing for a non-saturated signal.")
    lines.append("")
    lines.append("## Evidence Notes")
    lines.append("")
    lines.append("This audit is deterministic static evidence. It does not prove activation precision, output conformance, or robustness unless scenario results are supplied separately.")
    return "\n".join(lines) + "\n"


def audit_target(target: Path) -> dict:
    inv_obj = inventory(target)
    inv = asdict(inv_obj)
    scores, gates, findings, improvements = score_inventory(inv)
    total = sum(scores.values())
    return {
        "target_path": inv["target_path"],
        "inventory": inv,
        "scores": scores,
        "total_score": total,
        "gates": gates,
        "findings": findings,
        "improvements": improvements,
        "verdict": verdict(total, gates),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit hardening maturity for a ChatGPT skill folder.")
    parser.add_argument("--target", required=True, help="Path to target skill folder.")
    parser.add_argument("--output", help="Optional Markdown report path.")
    parser.add_argument("--json-output", help="Optional JSON report path.")
    parser.add_argument("--fail-under", type=int, default=None, help="Exit nonzero if score is below this value.")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        print(f"ERROR: target is not a directory: {target}", file=sys.stderr)
        return 2

    audit = audit_target(target)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown_report(audit), encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(markdown_report(audit))

    if args.json_output:
        jout = Path(args.json_output)
        jout.parent.mkdir(parents=True, exist_ok=True)
        jout.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {jout}")

    if args.fail_under is not None and audit["total_score"] < args.fail_under:
        print(f"ERROR: score {audit['total_score']} is below threshold {args.fail_under}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
