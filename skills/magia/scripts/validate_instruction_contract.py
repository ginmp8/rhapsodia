#!/usr/bin/env python3
"""Guard MAGIA instruction semantics and prevent silent functional deletion."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SECTIONS = {
    "SKILL.md": [
        "## Scope Boundary", "## Role Model", "## Technical Artifact Ownership",
        "## Technical Decision Authority", "## Load Order", "## Mode Selection",
        "## Required Inputs Before Mutation", "## Execution Workflow", "## Operating Rules",
        "## Stop Conditions", "## Output Contract", "## Package Requests",
        "## Validation Checklist", "## Activation Examples",
    ],
    "references/artifacts/execution-records.md": [
        "## Ownership Boundary", "## Planning-Origin Package Rules", "## Canonical Structure",
        "## Writing Rules", "## Cross-Artifact Consistency",
        "Do not create, refine, split, resequence, rewrite, or correct task prose",
        "only toggle an existing checkbox", "Do not duplicate execution evidence",
    ],
    "references/common-execution.md": [
        "## Operational Roots", "## Source of Truth", "## Planning-Origin Execution Inputs",
        "## Core Rules", "## Context Loading", "## Editing Rules", "## Compatibility",
    ],
    "references/modes/adhoc.md": ["## Canonical Rules", "## Use When", "## Workflow", "## Rules"],
    "references/modes/ralph.md": [
        "## Canonical Rules", "## Roots", "## Planning-Origin Handoff", "## Workflow",
        "## Task Selection", "## Blockers", "## Batch Execution", "## Unattended Loop Protocol",
    ],
    "references/modes/adapt.md": ["## Scope", "## Rules", "## Script", "## Output"],
    "references/planning-handoff.md": [
        "## Contract", "## Non-Blockers", "## Real Blockers", "## Target Derivation", "## Status and Evidence",
    ],
    "references/shared-artifact-ownership.md": [
        "## Ownership Matrix", "## MAGIA Rules", "## Template Boundary", "## Legacy Adapt Policy",
    ],
    "references/validation-and-closure.md": [
        "## Validation Policy", "## Execution Records Sync", "## Underdefined Tasks",
        "## Blockers", "## Final Closure Pass", "## Final Response",
    ],
}

MIN_LINES = {
    "references/artifacts/execution-records.md": 55,
    "references/common-execution.md": 58,
    "references/modes/adhoc.md": 23,
    "references/modes/ralph.md": 45,
    "references/modes/adapt.md": 22,
    "references/planning-handoff.md": 30,
    "references/resource-map.md": 40,
    "references/shared-artifact-ownership.md": 37,
    "references/validation-and-closure.md": 49,
}


def collect_errors() -> list[str]:
    errors: list[str] = []
    retired = "magi" + "arca"
    docs = [ROOT / "SKILL.md", *sorted((ROOT / "references").rglob("*.md"))]
    for path in docs:
        text = path.read_text(encoding="utf-8-sig")
        lowered = text.lower()
        if retired in lowered:
            errors.append(f"{path.relative_to(ROOT)}: retired governance identifier")
        obsolete_cycle_key = "cycle" + "_version"
        if obsolete_cycle_key in text:
            errors.append(f"{path.relative_to(ROOT)}: obsolete cycle identity contract")
        obsolete_spec_key = "spec" + "NNN"
        if obsolete_spec_key in text:
            errors.append(f"{path.relative_to(ROOT)}: obsolete sequential spec identity")
        if "contract-v1" in lowered:
            errors.append(f"{path.relative_to(ROOT)}: obsolete handoff contract-v1 wording")
        for alias in ("priority and order hint", "preserve priority", "preserve order hint"):
            if alias in lowered:
                errors.append(f"{path.relative_to(ROOT)}: unsupported generic priority alias wording: {alias}")

    for rel, markers in REQUIRED_SECTIONS.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing instruction file: {rel}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for marker in markers:
            if marker not in text:
                errors.append(f"{rel}: missing required contract marker `{marker}`")

    for rel, minimum in MIN_LINES.items():
        path = ROOT / rel
        if not path.is_file():
            continue
        count = len(path.read_text(encoding="utf-8-sig").splitlines())
        if count < minimum:
            errors.append(f"{rel}: instruction depth regressed to {count} lines; minimum is {minimum}")

    execution_records = (ROOT / "references/artifacts/execution-records.md").read_text(encoding="utf-8-sig")
    for required in ("registry/<spec_id>.yaml", "manifest.yaml", "tasks.md", "validation-evidence.md", "implementation-notes.md"):
        if required not in execution_records:
            errors.append(f"execution-records.md: missing canonical record `{required}`")
    if "Generated catalog and queue projections" not in execution_records:
        errors.append("execution-records.md: generated projection boundary is missing")

    return list(dict.fromkeys(errors))


def main() -> int:
    errors = collect_errors()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1
    print("OK: instruction contracts preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
