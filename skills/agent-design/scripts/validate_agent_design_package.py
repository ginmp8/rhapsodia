#!/usr/bin/env python3
"""Validate the reproducibility-critical structure of the agent-design skill package."""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

RECEIPT_VERSION = 1
REQUIRED_FILES = [
    "SKILL.md",
    "references/agent-contracts.md",
    "references/agent-design-rubric.md",
    "references/agent-governance-patterns.md",
    "references/agent-validation-scenarios.md",
    "references/routing-and-handoff-patterns.md",
    "assets/templates/agent-spec.md.template",
    "assets/templates/agent-review-report.md.template",
    "evals/agent-design-scenarios.json",
    "scripts/validate_agent_artifact.py",
    "scripts/validate_agent_design_package.py",
]
REQUIRED_GROUPS = {"activation", "non-activation", "ambiguous", "core", "edge", "regression", "adversarial", "holdout"}
EVIDENCE_STATUSES = {"planned", "executed", "supplied"}


def add(checks: list[dict[str, Any]], code: str, ok: bool, subject: str, evidence: dict[str, Any] | None = None) -> None:
    checks.append({"code": code, "status": "pass" if ok else "fail", "subject": subject, "evidence": evidence or {}})


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate_scenarios(root: Path, checks: list[dict[str, Any]]) -> None:
    path = root / "evals/agent-design-scenarios.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        add(checks, "evals/json-parse", True, str(path))
    except Exception as exc:
        add(checks, "evals/json-parse", False, str(path), {"error": str(exc)})
        return
    scenarios = data.get("scenarios", [])
    ids = [str(item.get("id", "")) for item in scenarios if isinstance(item, dict)]
    groups = {str(item.get("group", "")) for item in scenarios if isinstance(item, dict)}
    add(checks, "evals/unique-ids", len(ids) == len(set(ids)) and all(ids), "scenario ids", {"count": len(ids)})
    missing_groups = sorted(REQUIRED_GROUPS - groups)
    add(checks, "evals/group-coverage", not missing_groups, "scenario groups", {"missing": missing_groups, "present": sorted(groups)})
    bad_status = [item.get("id") for item in scenarios if item.get("evidence_status") not in EVIDENCE_STATUSES]
    add(checks, "evals/evidence-status", not bad_status, "scenario evidence", {"invalid": bad_status})
    malformed = []
    for item in scenarios:
        if not isinstance(item, dict):
            malformed.append("<non-object>")
            continue
        if not item.get("prompt") or not isinstance(item.get("must"), list) or not isinstance(item.get("must_not"), list):
            malformed.append(item.get("id", "<missing-id>"))
    add(checks, "evals/record-shape", not malformed, "scenario records", {"malformed": malformed})


def validate_python(root: Path, rel: str, checks: list[dict[str, Any]]) -> None:
    path = root / rel
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        add(checks, "python/parse", True, rel)
    except Exception as exc:
        add(checks, "python/parse", False, rel, {"error": str(exc)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    checks: list[dict[str, Any]] = []
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    add(checks, "package/required-files", not missing, str(root), {"missing": missing})

    if not missing:
        skill = read(root, "SKILL.md")
        contracts = read(root, "references/agent-contracts.md")
        rubric = read(root, "references/agent-design-rubric.md")
        validation = read(root, "references/agent-validation-scenarios.md")
        routing = read(root, "references/routing-and-handoff-patterns.md")
        spec_template = read(root, "assets/templates/agent-spec.md.template")
        review_template = read(root, "assets/templates/agent-review-report.md.template")

        required_skill_markers = [
            "## Activation Contract",
            "## Decision Rules",
            "## Multi-Agent State and Termination",
            "## Reproducibility and Evidence",
            "## Final Validation and Freeze",
            "scripts/validate_agent_artifact.py",
        ]
        missing_markers = [marker for marker in required_skill_markers if marker not in skill]
        add(checks, "skill/reproducibility-controls", not missing_markers, "SKILL.md", {"missing": missing_markers})
        add(checks, "contracts/version", "agent-design-contract/v1" in contracts and "handoff/v1" in contracts, "agent-contracts.md")
        add(checks, "rubric/version", "agent-design-rubric/v2" in rubric, "agent-design-rubric.md")
        add(checks, "rubric/critical-gates", "## Critical Gates" in rubric and "## Severity Taxonomy" in rubric, "agent-design-rubric.md")
        add(checks, "validation/evidence-separation", all(term in validation for term in ["planned", "executed", "supplied", "measured", "holdout"]), "agent-validation-scenarios.md")
        add(checks, "routing/deterministic-order", "## Routing Decision Order" in routing and "## Cycle and Re-entry Safety" in routing, "routing-and-handoff-patterns.md")
        add(checks, "template/spec-contract", "agent-design-contract/v1" in spec_template and "## 10. State and Termination" in spec_template, "agent-spec.md.template")
        add(checks, "template/review-gates", "agent-design-rubric/v2" in review_template and "## Critical Gates" in review_template, "agent-review-report.md.template")
        validate_scenarios(root, checks)
        validate_python(root, "scripts/validate_agent_artifact.py", checks)
        validate_python(root, "scripts/validate_agent_design_package.py", checks)

    errors = sum(1 for check in checks if check["status"] == "fail")
    payload = {
        "receipt_version": RECEIPT_VERSION,
        "status": "pass" if errors == 0 else "fail",
        "stage": "package-validation",
        "target": str(root),
        "checks": checks,
        "errors": errors,
        "warnings": 0,
        "limitations": ["This validator proves package invariants, not LLM behavioral quality."],
    }
    if args.json_path:
        atomic_json(Path(args.json_path), payload)
    else:
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        sys.stdout.flush()
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
