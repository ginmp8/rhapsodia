#!/usr/bin/env python3
"""Validate Skill Booster strategy escalation, budgets, and stop rules."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

INTENTS = {"repair", "optimization", "experiment"}
STRATEGIES = {"direct-repair", "single-candidate", "evolutionary-search"}
IDENTITY_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def validate(data: Any) -> dict:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["[ROOT] decision must be an object"]}
    if data.get("schema_version") != 1:
        errors.append("[SCHEMA] schema_version must be 1")
    if not isinstance(data.get("target_identity"), str) or not IDENTITY_RE.fullmatch(data["target_identity"]):
        errors.append("[TARGET_ID] target_identity must be sha256:<64hex>")
    if not isinstance(data.get("change_id"), str) or not data["change_id"].strip():
        errors.append("[CHANGE_ID] change_id is required")
    intent = data.get("change_intent")
    strategy = data.get("selected_strategy")
    if intent not in INTENTS:
        errors.append("[INTENT] change_intent is invalid")
    if strategy not in STRATEGIES:
        errors.append("[STRATEGY] selected_strategy is invalid")
    if not isinstance(data.get("evaluator_identity"), str) or not IDENTITY_RE.fullmatch(data["evaluator_identity"]):
        errors.append("[EVALUATOR] evaluator_identity must be sha256:<64hex>")
    if not isinstance(data.get("acceptance_rule"), str) or not data["acceptance_rule"].strip():
        errors.append("[ACCEPTANCE] acceptance_rule is required")
    simpler = data.get("simpler_strategy_considered")
    reason = data.get("escalation_reason")
    if strategy == "direct-repair":
        if intent != "repair":
            errors.append("[DIRECT_REPAIR] direct-repair requires change_intent=repair")
    elif strategy == "single-candidate":
        if simpler != "direct-repair":
            errors.append("[ESCALATION] single-candidate must explicitly consider direct-repair")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("[ESCALATION] single-candidate requires escalation_reason")
    elif strategy == "evolutionary-search":
        if simpler not in {"single-candidate", "direct-repair"}:
            errors.append("[ESCALATION] evolutionary-search must record the simpler strategy considered")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("[ESCALATION] evolutionary-search requires escalation_reason")
        if data.get("evolution_explicit_authorization") is not True:
            errors.append("[EVOLUTION_AUTH] evolutionary-search requires explicit authorization")
    budget = data.get("budget")
    if not isinstance(budget, dict):
        errors.append("[BUDGET] budget must be an object")
        budget = {}
    for field in ("max_transform_cycles", "max_candidates", "max_expensive_evals"):
        value = budget.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"[BUDGET] {field} must be a non-negative integer")
    if strategy == "single-candidate" and isinstance(budget.get("max_candidates"), int) and budget.get("max_candidates") != 1:
        errors.append("[BUDGET] single-candidate requires max_candidates=1")
    if strategy == "evolutionary-search" and isinstance(budget.get("max_candidates"), int) and budget.get("max_candidates") < 2:
        errors.append("[BUDGET] evolutionary-search requires max_candidates>=2")
    stops = data.get("stop_conditions")
    if not isinstance(stops, list) or not stops or any(not isinstance(x, str) or not x.strip() for x in stops):
        errors.append("[STOP] stop_conditions must contain at least one non-empty rule")
    return {"status": "pass" if not errors else "fail", "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Skill Booster strategy decision.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()
    try:
        report = validate(json.loads(Path(args.input).read_text(encoding="utf-8")))
    except Exception as exc:
        report = {"status": "fail", "errors": [f"[EXCEPTION] {exc}"]}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        Path(args.json).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
