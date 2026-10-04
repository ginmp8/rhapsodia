#!/usr/bin/env python3
"""Validate reproducibility-critical structure of the Agent Design skill package."""
from __future__ import annotations

import argparse
import ast
import json
import os
import tempfile
from pathlib import Path
from typing import Any

RECEIPT_VERSION = 2
REQUIRED_FILES = [
    "SKILL.md",
    "references/agent-contracts.md",
    "references/agent-design-rubric.md",
    "references/agent-governance-patterns.md",
    "references/agent-validation-scenarios.md",
    "references/routing-and-handoff-patterns.md",
    "references/context-state-and-concurrency.md",
    "references/host-adapters.md",
    "assets/templates/agent-spec.md.template",
    "assets/templates/agent-review-report.md.template",
    "evals/agent-design-scenarios.json",
    "scripts/validate_agent_artifact.py",
    "scripts/validate_agent_design_package.py",
]
REQUIRED_GROUPS = {"activation", "non-activation", "ambiguous", "core", "edge", "regression", "adversarial", "holdout"}
EVIDENCE_STATUSES = {"planned", "executed", "supplied"}
REQUIRED_SCENARIOS = {
    "regression-readonly-omitted-tools",
    "adversarial-delegation-authority-amplification",
    "regression-handoff-control-semantics",
    "edge-context-isolation-loss",
    "edge-resume-auth-scope",
    "regression-parallel-writer-collision",
    "core-multi-agent-admission",
}


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

    add(checks, "evals/version", data.get("suite_version") == 2 and data.get("evaluator_contract") == "agent-eval-contract/v2", "scenario suite")
    scenarios = data.get("scenarios", [])
    ids = [str(item.get("id", "")) for item in scenarios if isinstance(item, dict)]
    groups = {str(item.get("group", "")) for item in scenarios if isinstance(item, dict)}
    add(checks, "evals/unique-ids", len(ids) == len(set(ids)) and all(ids), "scenario ids", {"count": len(ids)})
    missing_groups = sorted(REQUIRED_GROUPS - groups)
    add(checks, "evals/group-coverage", not missing_groups, "scenario groups", {"missing": missing_groups, "present": sorted(groups)})
    missing_required = sorted(REQUIRED_SCENARIOS - set(ids))
    add(checks, "evals/v2-regressions", not missing_required, "required v2 scenarios", {"missing": missing_required})
    bad_status = [item.get("id") for item in scenarios if isinstance(item, dict) and item.get("evidence_status") not in EVIDENCE_STATUSES]
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
        governance = read(root, "references/agent-governance-patterns.md")
        validation = read(root, "references/agent-validation-scenarios.md")
        routing = read(root, "references/routing-and-handoff-patterns.md")
        context_state = read(root, "references/context-state-and-concurrency.md")
        hosts = read(root, "references/host-adapters.md")
        spec_template = read(root, "assets/templates/agent-spec.md.template")
        review_template = read(root, "assets/templates/agent-review-report.md.template")
        openai = read(root, "agents/openai.yaml") if (root / "agents/openai.yaml").is_file() else ""

        required_skill_markers = [
            "## Activation Contract",
            "## Multi-Agent Admission Gate",
            "## Effective Authority",
            "## Reproducibility and Evidence",
            "## Final Validation and Freeze",
            "agent-design-contract/v2",
            "agent-design-rubric/v3",
            "agent-eval-contract/v2",
            "scripts/validate_agent_artifact.py",
        ]
        missing_markers = [marker for marker in required_skill_markers if marker not in skill]
        add(checks, "skill/v2-controls", not missing_markers, "SKILL.md", {"missing": missing_markers})
        add(checks, "contracts/version", "agent-design-contract/v2" in contracts and "handoff/v2" in contracts, "agent-contracts.md")
        add(checks, "contracts/effective-authority", all(term in contracts.lower() for term in ["exposed capabilities", "downstream authority", "approval scope", "effective authority"]), "agent-contracts.md")
        add(checks, "contracts/context-state", "## 4. Context Contract" in contracts and "interrupted" in contracts and "resume" in contracts, "agent-contracts.md")
        add(checks, "rubric/version", "agent-design-rubric/v3" in rubric, "agent-design-rubric.md")
        add(checks, "rubric/critical-gates", "Effective authority" in rubric and "Multi-agent admission/concurrency" in rubric and "Containment/downstream auth" in rubric, "agent-design-rubric.md")
        add(checks, "governance/containment", all(term in governance.lower() for term in ["blast radius", "complete mediation", "downstream authorization", "containment"]), "agent-governance-patterns.md")
        add(checks, "validation/eval-v2", all(term in validation for term in ["agent-eval-contract/v2", "trial", "outcome", "trace", "holdout"]), "agent-validation-scenarios.md")
        add(checks, "routing/control-flow", "## Control-Flow Kinds" in routing and all(term in routing for term in ["delegate-return", "transfer-control", "suggested-transition", "parallel-child"]), "routing-and-handoff-patterns.md")
        add(checks, "routing/concurrency", "## Concurrency Safety" in routing, "routing-and-handoff-patterns.md")
        add(checks, "context/reference", all(marker in context_state for marker in ["## Context Contract", "## Resume Contract", "## Concurrent Mutation Contract"]), "context-state-and-concurrency.md")
        host_names = ["OpenAI", "Codex", "Claude", "Copilot", "VS Code", "Visual Studio", "Cursor"]
        add(checks, "hosts/adapter-matrix", all(name in hosts for name in host_names), "host-adapters.md", {"required": host_names})
        add(checks, "template/spec-contract", "agent-design-contract/v2" in spec_template and "## 7. Effective Authority" in spec_template and "agent-eval-contract/v2" in spec_template, "agent-spec.md.template")
        add(checks, "template/review-gates", "agent-design-rubric/v3" in review_template and "effective authority" in review_template.lower() and "containment/downstream auth" in review_template.lower(), "agent-review-report.md.template")
        add(checks, "openai/no-legacy-products", "products:" not in openai, "agents/openai.yaml")
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
        "limitations": ["This validator proves package/contract invariants, not LLM behavioral quality or host runtime permission enforcement."],
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
