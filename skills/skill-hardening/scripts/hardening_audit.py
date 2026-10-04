#!/usr/bin/env python3
"""Audit package-level hardening maturity without rewarding optional package bloat."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inventory_skill import inventory  # noqa: E402
from package_skill import read_text, validate_frontmatter  # noqa: E402

DIMENSIONS = ["static_structure", "package_semantics", "resource_integration", "validation_behavior"]


def clamp(value: int, low: int = 0, high: int = 25) -> int:
    return max(low, min(high, value))


def score_inventory(inv: dict, target: Path | None = None) -> tuple[dict[str, int], list[dict], list[dict], list[dict]]:
    gates: list[dict] = []
    findings: list[dict] = []
    improvements: list[dict] = []

    def gate(name: str, passed: bool, evidence: str, severity: str = "blocker") -> None:
        gates.append({"name": name, "passed": passed, "severity": severity, "evidence": evidence})

    skill_md_exists = bool(inv.get("skill_md_exists"))
    name = inv.get("skill_name")
    description = inv.get("description") or ""
    missing_refs = inv.get("missing_referenced_paths", [])
    placeholder_hits = inv.get("placeholder_hits", [])
    references = inv.get("references", [])
    scripts = inv.get("scripts", [])
    templates = inv.get("templates", [])
    assets = inv.get("assets", [])
    examples = inv.get("examples", [])
    unreferenced = inv.get("unreferenced_resources", [])

    frontmatter_errors: list[str] = []
    if target is not None and (target / "SKILL.md").exists():
        frontmatter_errors = validate_frontmatter(read_text(target / "SKILL.md"), root_name=target.name, profile="portable")

    activation_cue = bool(re.search(r"\b(use when|use for|when|trigger|use only)\b", description, flags=re.IGNORECASE))
    gate("valid_skill_md", skill_md_exists and bool(name) and bool(description), "SKILL.md and required frontmatter present" if skill_md_exists else "SKILL.md missing")
    gate("portable_frontmatter", not frontmatter_errors, "portable core frontmatter passes" if not frontmatter_errors else "; ".join(frontmatter_errors[:5]))
    gate("activation_description", bool(description) and activation_cue, "description states activation/use boundary" if activation_cue else "description lacks a clear when-to-use cue", "major")
    gate("references_resolve", len(missing_refs) == 0, f"missing referenced paths: {missing_refs}" if missing_refs else "all referenced paths resolve")
    gate("no_scaffold_placeholders", len(placeholder_hits) == 0, f"placeholder hits: {len(placeholder_hits)}" if placeholder_hits else "no placeholder hits")
    gate("output_contract", bool(inv.get("has_output_contract")), "output contract detected" if inv.get("has_output_contract") else "output contract not detected", "major")
    gate("validation_rules", bool(inv.get("has_validation")), "validation language detected" if inv.get("has_validation") else "validation language not detected", "major")
    gate("stop_conditions", bool(inv.get("has_stop_conditions")), "stop conditions detected" if inv.get("has_stop_conditions") else "stop conditions not detected", "major")

    static = 0
    if skill_md_exists:
        static += 6
    if not frontmatter_errors:
        static += 7
    if not placeholder_hits:
        static += 5
    if inv.get("skill_md_lines", 0) <= 500:
        static += 3
    if not missing_refs:
        static += 4

    semantics = 0
    if activation_cue:
        semantics += 5
    if inv.get("has_mode_matrix"):
        semantics += 5
    if inv.get("has_output_contract"):
        semantics += 5
    if inv.get("has_validation"):
        semantics += 5
    if inv.get("has_stop_conditions"):
        semantics += 5

    # Optional resources do not earn points merely by existing. Start complete and
    # deduct only for defects in resources that are actually present.
    resource = 25
    resource -= min(10, len(missing_refs) * 5)
    resource -= min(8, len(unreferenced) * 2)
    if placeholder_hits:
        resource -= min(7, len(placeholder_hits))

    validation = 0
    if inv.get("has_validation"):
        validation += 8
    if inv.get("has_output_contract"):
        validation += 6
    if inv.get("has_stop_conditions"):
        validation += 5
    if not missing_refs:
        validation += 3
    if not placeholder_hits:
        validation += 3

    scores = {
        "static_structure": clamp(static),
        "package_semantics": clamp(semantics),
        "resource_integration": clamp(resource),
        "validation_behavior": clamp(validation),
    }

    if frontmatter_errors:
        findings.append({"severity": "blocker", "area": "frontmatter", "finding": "; ".join(frontmatter_errors[:5])})
        improvements.append({"priority": 1, "area": "frontmatter", "recommendation": "Conform the portable core frontmatter to the Agent Skills specification/profile."})
    if missing_refs:
        findings.append({"severity": "blocker", "area": "references", "finding": f"Referenced paths are missing: {', '.join(missing_refs)}"})
    if placeholder_hits:
        findings.append({"severity": "blocker", "area": "placeholders", "finding": f"Placeholder text remains in {len(placeholder_hits)} locations."})
    if not activation_cue:
        improvements.append({"priority": 2, "area": "activation", "recommendation": "Make the description state both what the skill does and when it should activate."})
    if not inv.get("has_output_contract"):
        improvements.append({"priority": 3, "area": "semantics", "recommendation": "Define the observable output/closure contract for the skill."})
    if not inv.get("has_validation"):
        improvements.append({"priority": 4, "area": "validation", "recommendation": "Define validation evidence appropriate to the skill's actual output class."})
    if not inv.get("has_stop_conditions"):
        improvements.append({"priority": 5, "area": "safety", "recommendation": "Add stop conditions for missing evidence, unsafe scope, or invalid state."})
    if unreferenced:
        findings.append({"severity": "minor", "area": "resource_integration", "finding": f"Unreferenced resources: {', '.join(unreferenced[:10])}"})
        improvements.append({"priority": 6, "area": "resource_integration", "recommendation": "Reference operational resources with a loading/use condition, classify asset-only files, or remove truly unused resources."})

    return scores, gates, findings, improvements


def verdict(total: int, gates: list[dict]) -> str:
    blocker_failed = any((not item["passed"]) and item["severity"] == "blocker" for item in gates)
    major_failed = any((not item["passed"]) and item["severity"] == "major" for item in gates)
    if blocker_failed:
        return "reject"
    if total >= 85 and not major_failed:
        return "approve"
    if total >= 70:
        return "approve_with_reservations"
    return "reject"


def markdown_report(audit: dict) -> str:
    inv = audit["inventory"]
    lines = [
        f"# Skill Hardening Audit: {inv.get('skill_name') or Path(inv['target_path']).name}",
        "",
        "## Executive Summary",
        "",
        f"- Target: `{inv['target_path']}`",
        f"- Score: {audit['total_score']}/100",
        f"- Verdict: `{audit['verdict']}`",
        "- Score meaning: deterministic structural maturity only; it is not behavioral quality evidence.",
        f"- References: {len(inv.get('references', []))}; scripts: {len(inv.get('scripts', []))}; templates: {len(inv.get('templates', []))}; examples: {len(inv.get('examples', []))}",
        "",
        "## Scorecard",
        "",
        "| Layer | Score |",
        "|---|---:|",
    ]
    for key in DIMENSIONS:
        lines.append(f"| {key} | {audit['scores'][key]}/25 |")
    lines.extend(["", "## Auxiliary Signals", ""])
    for key, value in audit["auxiliary_signals"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Gates", "", "| Gate | Status | Severity | Evidence |", "|---|---|---|---|"])
    for item in audit["gates"]:
        status = "pass" if item["passed"] else "fail"
        evidence = str(item["evidence"]).replace("|", "\\|")
        lines.append(f"| {item['name']} | {status} | {item['severity']} | {evidence} |")
    lines.extend(["", "## Resource Inventory", ""])
    for label in ["references", "scripts", "templates", "assets", "examples"]:
        values = inv.get(label, [])
        lines.extend([f"### {label}", ""])
        lines.extend([f"- `{value}`" for value in values] if values else ["- none"])
        lines.append("")
    lines.extend(["## Findings", ""])
    if audit["findings"]:
        for item in audit["findings"]:
            lines.append(f"- **{item['severity']} / {item['area']}**: {item['finding']}")
    else:
        lines.append("- No structural findings detected by the static audit.")
    lines.extend(["", "## Prioritized Improvements", ""])
    if audit["improvements"]:
        for item in sorted(audit["improvements"], key=lambda value: value["priority"]):
            lines.append(f"{item['priority']}. **{item['area']}**: {item['recommendation']}")
    else:
        lines.append("- No static improvements suggested. Use a non-saturated behavioral/runtime signal if an improvement claim is needed.")
    lines.extend([
        "", "## Evidence Notes", "",
        "Optional directories and scripts are not maturity requirements by themselves. This audit scores required semantics and defects in resources that actually exist.",
        "Behavioral, runtime, perceptual, and semantic-review claims require their own evidence layers.",
    ])
    return "\n".join(lines) + "\n"


def audit_target(target: Path) -> dict:
    target = Path(target).resolve()
    inv_obj = inventory(target)
    inv = asdict(inv_obj)
    scores, gates, findings, improvements = score_inventory(inv, target)
    total = sum(scores.values())
    return {
        "target_path": inv["target_path"],
        "inventory": inv,
        "scores": scores,
        "total_score": total,
        "gates": gates,
        "findings": findings,
        "improvements": improvements,
        "auxiliary_signals": {
            "missing_reference_count": len(inv.get("missing_referenced_paths", [])),
            "unreferenced_resource_count": len(inv.get("unreferenced_resources", [])),
            "placeholder_count": len(inv.get("placeholder_hits", [])),
            "script_count": len(inv.get("scripts", [])),
            "example_count": len(inv.get("examples", [])),
        },
        "verdict": verdict(total, gates),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit hardening maturity for an Agent Skills-compatible folder.")
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
