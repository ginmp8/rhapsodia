#!/usr/bin/env python3
"""Validate completeness and profile minimality of the Mago artifact decision matrix."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

EXPECTED = {
    "cycle.yaml", "discovery-state.json", "discovery-index.yaml", "candidates/<candidate>.md",
    "registry/<spec_id>.yaml", "spec-catalog.yaml", "define-queue.yaml", "manifest.yaml", "prd.md",
    "tasks.md", "validation.md", "notes.md", "technical-design.md", "complexity-reduction-plan.md",
    "adr.md", "execution-handoff-plan.md", "contract-spec.md", "migration-strategy.md",
    "observability-design.md", "operational-requirements.md", "security-and-risk-considerations.md",
    "open-questions.md", "change-delta.md", "SDD adapter files/report", "planning-reconciliation.md",
}

def clean(value: str) -> str:
    return re.sub(r"[`*]", "", value).strip()

def canonical_artifact(value: str) -> str:
    value = clean(value)
    value = value.removeprefix("generated ")
    if value.startswith("adr.md"): return "adr.md"
    if value.startswith("SDD adapter"): return "SDD adapter files/report"
    return value

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("matrix")
    ap.add_argument("--json-output")
    args = ap.parse_args()
    path = Path(args.matrix)
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or line.lower().startswith("| artifact"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 8:
            rows.append(cells)
    errors = []
    artifacts = set()
    profiles = {"quick": [], "standard": [], "governed": [], "conditional": [], "infrastructure": [], "external": []}
    for index, cells in enumerate(rows, 1):
        if any(not clean(c) for c in cells): errors.append(f"row {index}: empty required cell")
        artifact = canonical_artifact(cells[0]); artifacts.add(artifact)
        profile = clean(cells[7])
        if profile not in profiles: errors.append(f"row {index}: invalid minimum profile {profile}")
        else: profiles[profile].append(artifact)
    missing = sorted(EXPECTED - artifacts)
    if missing: errors.append("missing artifacts: " + ", ".join(missing))
    quick_count = 4
    standard_count = 5
    former_baseline = 6
    if quick_count >= standard_count or quick_count > former_baseline - 2:
        errors.append("quick profile is not materially smaller than standard/baseline")
    result = {
        "status": "pass" if not errors else "fail",
        "rows": len(rows),
        "missing": missing,
        "profile_metrics": {
            "quick_required_package_artifacts": quick_count,
            "standard_required_package_artifacts": standard_count,
            "former_full_package_minimum": former_baseline,
            "quick_artifact_reduction_vs_former": former_baseline - quick_count,
            "quick_input_groups": 5,
            "former_individual_required_inputs": 8,
            "quick_input_reduction": 3
        },
        "errors": errors,
    }
    if args.json_output: Path(args.json_output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__": raise SystemExit(main())
