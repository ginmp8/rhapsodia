#!/usr/bin/env python3
"""Validate resumable Skill Booster run state and stale candidate-bound evidence."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PHASES = ["establish", "diagnose", "select", "transform", "evaluate", "prove"]
PHASE_STATES = {"not-started", "active", "pass", "fail", "blocked"}
MODES = {"audit-only", "plan-only", "apply-optimization", "evolutionary-optimization", "validation-only", "package"}
EVIDENCE_STATES = {"pass", "pass-with-warnings", "fail", "blocked", "historical"}
IDENTITY_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def valid_identity(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTITY_RE.fullmatch(value))


def load_manifest_identity(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    digest = data.get("candidate_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError(f"manifest lacks candidate_sha256: {path}")
    return f"sha256:{digest}"


def validate(data: Any, baseline_manifest: Path | None = None, candidate_manifest: Path | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["[ROOT] state must be an object"], "warnings": []}
    if data.get("schema_version") != 1:
        errors.append("[SCHEMA] schema_version must be 1")
    if not isinstance(data.get("run_id"), str) or not data["run_id"].strip():
        errors.append("[RUN_ID] run_id is required")
    if data.get("mode") not in MODES:
        errors.append("[MODE] mode is invalid")
    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("[TARGET] target must be an object")
        target = {}
    for field in ("baseline_identity", "current_candidate_identity"):
        if not valid_identity(target.get(field)):
            errors.append(f"[IDENTITY] target.{field} must be sha256:<64hex>")
    if baseline_manifest:
        expected = load_manifest_identity(baseline_manifest)
        if target.get("baseline_identity") != expected:
            errors.append("[BASELINE_DRIFT] stored baseline identity differs from supplied baseline manifest")
    if candidate_manifest:
        expected = load_manifest_identity(candidate_manifest)
        if target.get("current_candidate_identity") != expected:
            errors.append("[CANDIDATE_DRIFT] stored candidate identity differs from supplied candidate manifest")

    current_phase = data.get("current_phase")
    if current_phase not in PHASES:
        errors.append("[PHASE] current_phase is invalid")
    phase_status = data.get("phase_status")
    if not isinstance(phase_status, dict):
        errors.append("[PHASE_STATUS] phase_status must be an object")
        phase_status = {}
    active = []
    for phase in PHASES:
        state = phase_status.get(phase)
        if state not in PHASE_STATES:
            errors.append(f"[PHASE_STATUS] {phase} has invalid state")
        if state == "active":
            active.append(phase)
    if len(active) > 1:
        errors.append("[PHASE_ACTIVE] at most one phase may be active")
    if current_phase in PHASES and phase_status.get(current_phase) not in {"active", "pass"}:
        errors.append("[PHASE_CURRENT] current_phase must be active or pass")
    if current_phase in PHASES:
        idx = PHASES.index(current_phase)
        for earlier in PHASES[:idx]:
            if phase_status.get(earlier) not in {"pass"}:
                errors.append(f"[PHASE_ORDER] earlier phase {earlier} must pass before {current_phase}")

    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("[EVIDENCE] evidence must be an object")
        evidence = {}
    for field in ("evaluator_set_identity", "source_set_identity"):
        if not valid_identity(evidence.get(field)):
            errors.append(f"[EVIDENCE_ID] evidence.{field} must be sha256:<64hex>")
    invalidated = data.get("invalidated_evidence_ids")
    if not isinstance(invalidated, list) or any(not isinstance(x, str) or not x for x in invalidated):
        errors.append("[INVALIDATED] invalidated_evidence_ids must be a list of non-empty strings")
        invalidated = []
    current_candidate = target.get("current_candidate_identity")
    candidate_bound = evidence.get("candidate_bound")
    if not isinstance(candidate_bound, list):
        errors.append("[CANDIDATE_EVIDENCE] evidence.candidate_bound must be a list")
        candidate_bound = []
    seen_ids: set[str] = set()
    for i, item in enumerate(candidate_bound):
        if not isinstance(item, dict):
            errors.append(f"[CANDIDATE_EVIDENCE] candidate_bound[{i}] must be an object")
            continue
        eid = item.get("id")
        if not isinstance(eid, str) or not eid:
            errors.append(f"[CANDIDATE_EVIDENCE] candidate_bound[{i}].id is required")
            continue
        if eid in seen_ids:
            errors.append(f"[CANDIDATE_EVIDENCE] duplicate evidence id {eid}")
        seen_ids.add(eid)
        status = item.get("status")
        if status not in EVIDENCE_STATES:
            errors.append(f"[CANDIDATE_EVIDENCE] {eid} status is invalid")
        identity = item.get("candidate_identity")
        if not valid_identity(identity):
            errors.append(f"[CANDIDATE_EVIDENCE] {eid} candidate_identity is invalid")
        elif identity != current_candidate and status != "historical" and eid not in invalidated:
            errors.append(f"[STALE_EVIDENCE] {eid} is bound to a different candidate and is not invalidated")

    budget = data.get("budget")
    if not isinstance(budget, dict):
        errors.append("[BUDGET] budget must be an object")
        budget = {}
    pairs = [
        ("max_transform_cycles", "used_transform_cycles"),
        ("max_expensive_evals", "used_expensive_evals"),
        ("max_candidates", "used_candidates"),
    ]
    exhausted: list[str] = []
    for maximum, used in pairs:
        mx, us = budget.get(maximum), budget.get(used)
        if not isinstance(mx, int) or isinstance(mx, bool) or mx < 0:
            errors.append(f"[BUDGET] {maximum} must be a non-negative integer")
            continue
        if not isinstance(us, int) or isinstance(us, bool) or us < 0:
            errors.append(f"[BUDGET] {used} must be a non-negative integer")
            continue
        if us > mx:
            errors.append(f"[BUDGET_EXCEEDED] {used} exceeds {maximum}")
        elif mx > 0 and us == mx:
            exhausted.append(maximum)

    resume = data.get("resume")
    if not isinstance(resume, dict):
        errors.append("[RESUME] resume must be an object")
        resume = {}
    for field in ("checkpoint_id", "last_completed_action"):
        if not isinstance(resume.get(field), str) or not resume[field].strip():
            errors.append(f"[RESUME] resume.{field} is required")
    for field in ("next_legal_actions", "blockers"):
        value = resume.get(field)
        if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
            errors.append(f"[RESUME] resume.{field} must be a list of non-empty strings")
    if exhausted:
        warnings.append("budget exhausted: " + ", ".join(exhausted))
    resume_allowed = not errors and not resume.get("blockers") and not exhausted
    return {"status": "pass" if not errors else "fail", "resume_allowed": resume_allowed, "errors": errors, "warnings": warnings, "exhausted": exhausted}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate resumable Skill Booster run state.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--baseline-manifest")
    parser.add_argument("--candidate-manifest")
    parser.add_argument("--json")
    args = parser.parse_args()
    try:
        report = validate(
            json.loads(Path(args.state).read_text(encoding="utf-8")),
            Path(args.baseline_manifest) if args.baseline_manifest else None,
            Path(args.candidate_manifest) if args.candidate_manifest else None,
        )
    except Exception as exc:
        report = {"status": "fail", "resume_allowed": False, "errors": [f"[EXCEPTION] {exc}"], "warnings": []}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        Path(args.json).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
