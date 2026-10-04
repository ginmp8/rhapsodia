#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

TARGET_SKILL = "skill-prompt-and-activation-review"
ALLOWED_STATUS = {"planned", "measured"}
ALLOWED_GROUPS = {"activation", "non-activation", "ambiguous", "boundary", "adversarial", "regression"}
ALLOWED_ROUTES = {
    "activate", "do-not-activate", "conditional", "activate-constrained", "split-handoff",
    "reject-scope-weakening", "reject-fabricated-evidence", "reject-ownership-expansion",
    "reject-activation-gaming",
}
ALLOWED_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
GROUP_TO_TYPE = {
    "activation": "should_activate",
    "non-activation": "should_not_activate",
    "ambiguous": "ambiguous",
    "boundary": "edge_case",
    "adversarial": "adversarial",
    "regression": "regression",
}
ALLOWED_TIERS = {"L2-focused", "L3-harness", "L5-holdout"}
ALLOWED_VISIBILITY = {"candidate-visible", "evaluator-only"}
INVOCATION_MODES = {"explicit", "implicit", "contextual"}
MEASUREMENT_SCOPES = {"direct-usage", "auto-routing", "boundary-routing", "policy-resistance", "regression"}
NEGATIVE_KINDS = {"alternative-owner", "abstain"}
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]+)?$")
CONTRACT_ID = re.compile(r"^[A-Z]{2,8}-\d{3}$")


def _error(errors: list[dict[str, Any]], code: str, subject: str, **evidence: Any) -> None:
    errors.append({"code": code, "subject": subject, "evidence": evidence})


def validate_suite(
    data: dict[str, Any],
    require_regression: bool = True,
    require_realistic_dimensions: bool = True,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    scenarios = data.get("scenarios")
    version = data.get("suite_version")
    if not isinstance(version, str) or not version.startswith("3."):
        _error(errors, "suite/version", "suite_version", expected_major="3", actual=version)
    if data.get("target_skill") != TARGET_SKILL:
        _error(errors, "suite/target-skill", "target_skill", target_skill=data.get("target_skill"))
    if data.get("status") not in ALLOWED_STATUS:
        _error(errors, "suite/status", "status", status=data.get("status"))
    if data.get("blind_holdout_policy") != "external-evaluator-only":
        _error(errors, "suite/blind-holdout-policy", "blind_holdout_policy", value=data.get("blind_holdout_policy"))
    if not isinstance(scenarios, list) or not scenarios:
        _error(errors, "suite/scenarios", "scenarios")
        scenarios = []

    ids: list[Any] = []
    groups: dict[Any, int] = {}
    types: dict[Any, int] = {}
    invocation_modes: dict[Any, int] = {}
    negative_kinds: dict[Any, int] = {}
    non_english = typo_or_noisy = long_context = multi_intent = 0

    for index, scenario in enumerate(scenarios):
        subject = scenario.get("id") if isinstance(scenario, dict) else f"index:{index}"
        if not isinstance(scenario, dict):
            _error(errors, "scenario/object", subject)
            continue
        scenario_id = scenario.get("id")
        ids.append(scenario_id)
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            _error(errors, "scenario/id", subject)

        group = scenario.get("group")
        groups[group] = groups.get(group, 0) + 1
        if group not in ALLOWED_GROUPS:
            _error(errors, "scenario/group", subject, group=group)
        prompt = scenario.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            _error(errors, "scenario/prompt", subject)
        route = scenario.get("expected_route")
        if route not in ALLOWED_ROUTES:
            _error(errors, "scenario/expected-route", subject, expected_route=route)
        contract_ids = scenario.get("contract_ids")
        if not isinstance(contract_ids, list) or not contract_ids:
            _error(errors, "scenario/contract-ids", subject)
        elif any(not isinstance(value, str) or not CONTRACT_ID.fullmatch(value) for value in contract_ids):
            _error(errors, "scenario/contract-id-format", subject, contract_ids=contract_ids)

        harness_type = scenario.get("type")
        types[harness_type] = types.get(harness_type, 0) + 1
        if harness_type not in ALLOWED_TYPES:
            _error(errors, "scenario/harness-type", subject, type=harness_type)
        category = scenario.get("category")
        if category != harness_type:
            _error(errors, "scenario/category-type-mismatch", subject, category=category, type=harness_type)
        expected_type = GROUP_TO_TYPE.get(group)
        if expected_type and harness_type != expected_type:
            _error(errors, "scenario/group-type-mismatch", subject, group=group, type=harness_type, expected_type=expected_type)

        expected_behavior = scenario.get("expected_behavior")
        if not isinstance(expected_behavior, str) or not expected_behavior.strip():
            _error(errors, "scenario/expected-behavior", subject)
        criteria = scenario.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria or any(not isinstance(v, str) or not v.strip() for v in criteria):
            _error(errors, "scenario/acceptance-criteria", subject)
        tier = scenario.get("evaluation_tier")
        if tier not in ALLOWED_TIERS:
            _error(errors, "scenario/evaluation-tier", subject, evaluation_tier=tier)
        visibility = scenario.get("visibility")
        if visibility not in ALLOWED_VISIBILITY:
            _error(errors, "scenario/visibility", subject, visibility=visibility)
        if visibility == "evaluator-only":
            _error(errors, "scenario/bundled-evaluator-only", subject, visibility=visibility)

        invocation_mode = scenario.get("invocation_mode")
        invocation_modes[invocation_mode] = invocation_modes.get(invocation_mode, 0) + 1
        if invocation_mode not in INVOCATION_MODES:
            _error(errors, "scenario/invocation-mode", subject, invocation_mode=invocation_mode)
        measurement_scope = scenario.get("measurement_scope")
        if measurement_scope not in MEASUREMENT_SCOPES:
            _error(errors, "scenario/measurement-scope", subject, measurement_scope=measurement_scope)
        if invocation_mode == "explicit" and measurement_scope == "auto-routing":
            _error(errors, "scenario/explicit-auto-routing", subject)

        negative_kind = scenario.get("negative_kind")
        if group == "non-activation":
            if negative_kind not in NEGATIVE_KINDS:
                _error(errors, "scenario/negative-kind", subject, negative_kind=negative_kind)
            else:
                negative_kinds[negative_kind] = negative_kinds.get(negative_kind, 0) + 1
            if negative_kind == "alternative-owner" and not isinstance(scenario.get("neighbor_owner"), str):
                _error(errors, "scenario/neighbor-owner", subject, neighbor_owner=scenario.get("neighbor_owner"))
        elif negative_kind is not None:
            _error(errors, "scenario/unexpected-negative-kind", subject, negative_kind=negative_kind)

        dimensions = scenario.get("dimensions")
        if not isinstance(dimensions, dict):
            _error(errors, "scenario/dimensions", subject)
            continue
        language = dimensions.get("language")
        if not isinstance(language, str) or not LANGUAGE_RE.fullmatch(language):
            _error(errors, "scenario/language", subject, language=language)
        elif language.lower() != "en":
            non_english += 1
        context_profile = dimensions.get("context_profile")
        if context_profile not in {"clean", "noisy", "long"}:
            _error(errors, "scenario/context-profile", subject, context_profile=context_profile)
        elif context_profile == "long":
            long_context += 1
        input_style = dimensions.get("input_style")
        if input_style not in {"terse", "conversational", "typo"}:
            _error(errors, "scenario/input-style", subject, input_style=input_style)
        elif input_style == "typo":
            typo_or_noisy += 1
        intent_profile = dimensions.get("intent_profile")
        if intent_profile not in {"single", "multi-intent"}:
            _error(errors, "scenario/intent-profile", subject, intent_profile=intent_profile)
        elif intent_profile == "multi-intent":
            multi_intent += 1
        if context_profile == "noisy":
            typo_or_noisy += 1

    clean_ids = [value for value in ids if isinstance(value, str) and value]
    if len(clean_ids) != len(set(clean_ids)):
        _error(errors, "suite/unique-ids", "scenarios", ids=clean_ids)

    required_groups = {"activation", "non-activation", "ambiguous", "boundary", "adversarial"}
    if require_regression:
        required_groups.add("regression")
    for group in sorted(required_groups):
        if groups.get(group, 0) == 0:
            _error(errors, "suite/missing-group", group)

    for invocation_mode in sorted(INVOCATION_MODES):
        if invocation_modes.get(invocation_mode, 0) == 0:
            _error(errors, "suite/missing-invocation-mode", invocation_mode)

    if negative_kinds.get("alternative-owner", 0) == 0:
        _error(errors, "suite/missing-negative-kind", "alternative-owner")
    if negative_kinds.get("abstain", 0) == 0:
        _error(errors, "suite/missing-negative-kind", "abstain")

    if require_realistic_dimensions:
        if non_english == 0:
            _error(errors, "suite/missing-realistic-dimension", "non-english")
        if typo_or_noisy == 0:
            _error(errors, "suite/missing-realistic-dimension", "typo-or-noisy")
        if long_context == 0:
            _error(errors, "suite/missing-realistic-dimension", "long-context")
        if multi_intent == 0:
            _error(errors, "suite/missing-realistic-dimension", "multi-intent")

    return {
        "status": "fail" if errors else "pass",
        "suite_version": data.get("suite_version"),
        "scenario_count": len(scenarios),
        "group_counts": {str(k): v for k, v in sorted(groups.items(), key=lambda item: str(item[0]))},
        "type_counts": {str(k): v for k, v in sorted(types.items(), key=lambda item: str(item[0]))},
        "invocation_mode_counts": {str(k): v for k, v in sorted(invocation_modes.items(), key=lambda item: str(item[0]))},
        "negative_kind_counts": {str(k): v for k, v in sorted(negative_kinds.items(), key=lambda item: str(item[0]))},
        "realistic_dimension_counts": {
            "non_english": non_english,
            "typo_or_noisy": typo_or_noisy,
            "long_context": long_context,
            "multi_intent": multi_intent,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the v3 portable activation scenario suite and routing semantics.")
    parser.add_argument("suite")
    parser.add_argument("--allow-no-regression", action="store_true")
    parser.add_argument("--allow-no-realistic-dimensions", action="store_true")
    parser.add_argument("--json")
    args = parser.parse_args()
    path = Path(args.suite)
    data = json.loads(path.read_text(encoding="utf-8"))
    report = validate_suite(
        data,
        require_regression=not args.allow_no_regression,
        require_realistic_dimensions=not args.allow_no_realistic_dimensions,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        Path(args.json).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
