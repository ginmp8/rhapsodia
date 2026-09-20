from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import (
    dump_json,
    evaluation_identity_matches,
    metric_value,
    request_signature,
    validate_transform_set,
)

VALID_CANDIDATE_STATUS = {"planned", "generated", "evaluating", "active", "rejected", "finalist", "terminal"}
VALID_SEARCH_STATUS = {"active", "terminated"}
VALID_ROLES = {"canonical", "evidence-driven", "focused", "novel-bounded", "merge", "backcross", "repair", "mutation", "other"}
VALID_GATE_VALUES = {"pass", "fail", "not-run", "blocked"}
VALID_EVIDENCE_TYPES = {"measured", "supplied", "derived", "planned", "unknown"}
VALID_HOLDOUT_STATUS = {"not-used", "blind-pass", "blind-fail", "revealed-development"}
LEVEL_ORDER = ["L0-structural", "L1-deterministic", "L2-focused", "L3-harness", "L4-benchmark", "L5-holdout"]
LEVEL_RANK = {level: index for index, level in enumerate(LEVEL_ORDER)}
VALID_TERMINATION_REASONS = {
    "sufficient-finalists",
    "candidate-budget-exhausted",
    "stagnation-threshold-reached",
    "no-compatible-requests",
    "all-strategies-eliminated",
    "evaluator-insufficient-discrimination",
    "continuation-invalidates-evidence",
}


def validate(contract: dict, state: dict) -> list[str]:
    errors: list[str] = []
    if state.get("state_version") != 4:
        if state.get("state_version") in {1, 2, 3}:
            errors.append("state_version:upgrade_required_v4")
        else:
            errors.append("state_version:unsupported")
    if state.get("search_id") != contract.get("search_id"):
        errors.append("search_id:mismatch")
    if state.get("status") not in VALID_SEARCH_STATUS:
        errors.append("status:invalid")
    if not isinstance(state.get("round"), int) or isinstance(state.get("round"), bool) or state.get("round", -1) < 0:
        errors.append("round:invalid")
    if not isinstance(state.get("stagnant_rounds"), int) or isinstance(state.get("stagnant_rounds"), bool) or state.get("stagnant_rounds", -1) < 0:
        errors.append("stagnant_rounds:invalid")

    budget = contract.get("budget", {})
    if state.get("status") == "active" and isinstance(state.get("stagnant_rounds"), int) and state["stagnant_rounds"] >= budget.get("stagnant_rounds", 10**9):
        errors.append("termination:stagnation_threshold_reached")
    termination_reason = state.get("termination_reason")
    if state.get("status") == "terminated":
        if not isinstance(termination_reason, str) or not termination_reason.strip():
            errors.append("termination_reason:required")
        elif termination_reason not in VALID_TERMINATION_REASONS:
            errors.append("termination_reason:invalid")
    if state.get("status") == "active" and termination_reason not in (None, ""):
        errors.append("termination_reason:must_be_empty_while_active")

    candidates = state.get("candidates")
    if not isinstance(candidates, list):
        return sorted(set(errors + ["candidates:invalid"]))
    if len(candidates) > budget.get("max_total_candidates", 0):
        errors.append("candidates:budget_exceeded")

    ids = [c.get("candidate_id") for c in candidates if isinstance(c, dict)]
    if len(ids) != len(candidates) or len(ids) != len(set(ids)) or any(not isinstance(x, str) or not x for x in ids):
        errors.append("candidate_id:invalid_or_duplicate")

    by_id = {c.get("candidate_id"): c for c in candidates if isinstance(c, dict) and isinstance(c.get("candidate_id"), str)}
    active = [c for c in candidates if isinstance(c, dict) and c.get("status") in {"active", "finalist"}]
    if len(active) > budget.get("max_active_candidates", 0):
        errors.append("candidates:active_budget_exceeded")

    hard_gate_names = list(contract.get("hard_gates", []))
    objective_names = [o.get("name") for o in contract.get("objectives", []) if isinstance(o, dict)]
    allowed_levels = set(contract.get("allowed_evaluation_levels", []))
    finalist_policy = contract.get("finalist_policy", {})
    finalist_minimum_level = finalist_policy.get("minimum_evaluation_level")
    finalist_holdout_policy = finalist_policy.get("holdout_policy")
    finalist_evidence_types = set(contract.get("selection_policy", {}).get("eligible_evidence_types", []))
    baseline_id = contract.get("baseline_candidate_id")
    seen_ids: set[str] = set()
    materialized_identities: set[str] = set()
    seen_request_signatures: dict[str, str] = {}

    for c in candidates:
        if not isinstance(c, dict):
            errors.append("candidate:invalid")
            continue
        cid = c.get("candidate_id")
        if not isinstance(cid, str) or not cid:
            continue
        status = c.get("status")
        if status not in VALID_CANDIDATE_STATUS:
            errors.append(f"candidate:{cid}:status_invalid")
        if c.get("role") not in VALID_ROLES:
            errors.append(f"candidate:{cid}:role_invalid")
        operator = c.get("operator")
        if operator not in contract.get("allowed_operators", []):
            errors.append(f"candidate:{cid}:operator_not_allowed")

        parents = c.get("parent_ids", [])
        if not isinstance(parents, list) or any(not isinstance(p, str) or not p for p in parents) or len(parents) != len(set(parents)):
            errors.append(f"candidate:{cid}:parent_ids_invalid")
            parents = []
        if cid in parents:
            errors.append(f"candidate:{cid}:self_parent")
        for p in parents:
            if p != baseline_id and p not in seen_ids:
                errors.append(f"candidate:{cid}:parent_not_prior:{p}")

        base = c.get("base_parent_id")
        if not isinstance(base, str) or not base:
            errors.append(f"candidate:{cid}:base_parent_id_invalid")
        elif base != baseline_id and base not in parents:
            errors.append(f"candidate:{cid}:base_parent_not_parent:{base}")

        donors = c.get("donor_parent_ids", [])
        if not isinstance(donors, list) or any(not isinstance(d, str) or not d for d in donors) or len(donors) != len(set(donors)):
            errors.append(f"candidate:{cid}:donor_parent_ids_invalid")
            donors = []
        else:
            for donor in donors:
                if donor not in parents:
                    errors.append(f"candidate:{cid}:donor_not_parent:{donor}")
                if donor == base:
                    errors.append(f"candidate:{cid}:donor_equals_base:{donor}")

        transforms = c.get("transformation_ids", [])
        for transform_error in validate_transform_set(transforms, contract):
            errors.append(f"candidate:{cid}:{transform_error}")

        effects = c.get("expected_capability_effects", [])
        if not isinstance(effects, list) or any(not isinstance(x, str) or not x for x in effects) or len(effects) != len(set(effects)):
            errors.append(f"candidate:{cid}:expected_capability_effects_invalid")

        if isinstance(base, str) and isinstance(transforms, list):
            signature = request_signature(base, transforms)
            if signature in seen_request_signatures:
                errors.append(f"candidate:{cid}:duplicate_strategy:{seen_request_signatures[signature]}")
            else:
                seen_request_signatures[signature] = cid

        generated_or_later = status in {"generated", "evaluating", "active", "rejected", "finalist", "terminal"}
        identity = c.get("candidate_identity")
        if generated_or_later and (not isinstance(identity, str) or not identity.strip()):
            errors.append(f"candidate:{cid}:candidate_identity_required")
        elif generated_or_later:
            if identity in materialized_identities:
                errors.append("candidate_identity:duplicate")
            else:
                materialized_identities.add(identity)

        receipt = c.get("generation_receipt")
        if generated_or_later:
            if not isinstance(receipt, dict):
                errors.append(f"candidate:{cid}:generation_receipt_required")
            else:
                if not isinstance(receipt.get("receipt_identity"), str) or not receipt["receipt_identity"].strip():
                    errors.append(f"candidate:{cid}:generation_receipt_identity_invalid")
                if receipt.get("candidate_identity") != identity:
                    errors.append(f"candidate:{cid}:generation_receipt_candidate_mismatch")
                if receipt.get("base_parent_id") != base:
                    errors.append(f"candidate:{cid}:generation_receipt_base_mismatch")
                if sorted(receipt.get("donor_parent_ids", [])) != sorted(donors):
                    errors.append(f"candidate:{cid}:generation_receipt_donors_mismatch")
                if receipt.get("operator") != operator:
                    errors.append(f"candidate:{cid}:generation_receipt_operator_mismatch")
                if sorted(receipt.get("transformation_ids", [])) != sorted(transforms):
                    errors.append(f"candidate:{cid}:generation_receipt_transformations_mismatch")

        evaluation = c.get("evaluation")
        needs_complete_evaluation = status in {"active", "finalist"}
        has_evaluation = isinstance(evaluation, dict)
        if needs_complete_evaluation and not has_evaluation:
            errors.append(f"candidate:{cid}:evaluation_required")
        if has_evaluation:
            if not isinstance(evaluation.get("evaluation_ref"), str) or not evaluation["evaluation_ref"].strip():
                errors.append(f"candidate:{cid}:evaluation_ref_required")
            if not evaluation_identity_matches(c, contract):
                errors.append(f"candidate:{cid}:evaluation_identity_mismatch")
            if evaluation.get("level") not in allowed_levels:
                errors.append(f"candidate:{cid}:evaluation_level_invalid")
            if evaluation.get("evidence_type") not in VALID_EVIDENCE_TYPES:
                errors.append(f"candidate:{cid}:evaluation_evidence_type_invalid")
            if evaluation.get("holdout_status", "not-used") not in VALID_HOLDOUT_STATUS:
                errors.append(f"candidate:{cid}:holdout_status_invalid")
            if evaluation.get("level") == "L5-holdout" and evaluation.get("holdout_status") == "not-used":
                errors.append(f"candidate:{cid}:holdout_status_required")

            gates = evaluation.get("hard_gates", {})
            if not isinstance(gates, dict):
                errors.append(f"candidate:{cid}:hard_gates_invalid")
                gates = {}
            unknown_gates = set(gates) - set(hard_gate_names)
            if unknown_gates:
                errors.append(f"candidate:{cid}:unknown_gates:{','.join(sorted(unknown_gates))}")
            for gate, value in gates.items():
                if value not in VALID_GATE_VALUES:
                    errors.append(f"candidate:{cid}:gate_value_invalid:{gate}")
            if needs_complete_evaluation:
                missing_gates = set(hard_gate_names) - set(gates)
                if missing_gates:
                    errors.append(f"candidate:{cid}:missing_gates:{','.join(sorted(missing_gates))}")

            metrics = evaluation.get("metrics", {})
            if not isinstance(metrics, dict):
                errors.append(f"candidate:{cid}:metrics_invalid")
                metrics = {}
            unknown_metrics = set(metrics) - set(objective_names)
            if unknown_metrics:
                errors.append(f"candidate:{cid}:unknown_metrics:{','.join(sorted(unknown_metrics))}")
            for name, raw in metrics.items():
                if metric_value(raw) is None:
                    errors.append(f"candidate:{cid}:metric_invalid:{name}")
            if needs_complete_evaluation:
                missing_metrics = set(objective_names) - set(metrics)
                if missing_metrics:
                    errors.append(f"candidate:{cid}:missing_metrics:{','.join(sorted(missing_metrics))}")

            if status == "finalist":
                level = evaluation.get("level")
                if level in LEVEL_RANK and finalist_minimum_level in LEVEL_RANK:
                    if LEVEL_RANK[level] < LEVEL_RANK[finalist_minimum_level]:
                        errors.append(f"candidate:{cid}:finalist_evaluation_level_below_minimum")
                if evaluation.get("evidence_type") not in finalist_evidence_types:
                    errors.append(f"candidate:{cid}:finalist_evidence_type_ineligible")
                if not isinstance(gates, dict) or any(gates.get(gate) != "pass" for gate in hard_gate_names):
                    errors.append(f"candidate:{cid}:finalist_hard_gates_not_pass")
                holdout_status = evaluation.get("holdout_status", "not-used")
                if holdout_status == "blind-fail":
                    errors.append(f"candidate:{cid}:finalist_holdout_failed")
                if finalist_holdout_policy == "blind-pass-required":
                    if level != "L5-holdout" or holdout_status != "blind-pass":
                        errors.append(f"candidate:{cid}:finalist_blind_holdout_required")

        seen_ids.add(cid)

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> None:
        if node in visiting:
            errors.append(f"lineage:cycle:{node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for p in by_id[node].get("parent_ids", []):
            if p in by_id:
                dfs(p)
        visiting.remove(node)
        visited.add(node)

    for cid in by_id:
        dfs(cid)

    pareto_archive = state.get("pareto_archive", [])
    if not isinstance(pareto_archive, list) or len(pareto_archive) != len(set(pareto_archive)):
        errors.append("pareto_archive:invalid")
    else:
        for cid in pareto_archive:
            if cid not in by_id:
                errors.append(f"pareto_archive:unknown:{cid}")

    finalists = state.get("finalists", [])
    if not isinstance(finalists, list) or len(finalists) != len(set(finalists)):
        errors.append("finalists:invalid")
    else:
        if len(finalists) > budget.get("finalists", 0):
            errors.append("finalists:budget_exceeded")
        for cid in finalists:
            if cid not in by_id:
                errors.append(f"finalists:unknown:{cid}")
            elif by_id[cid].get("status") != "finalist":
                errors.append(f"finalists:status_mismatch:{cid}")
        declared_finalists = {
            cid for cid, candidate in by_id.items()
            if candidate.get("status") == "finalist"
        }
        for cid in sorted(declared_finalists - set(finalists)):
            errors.append(f"finalists:missing:{cid}")
        if state.get("status") == "terminated" and termination_reason == "sufficient-finalists":
            required_finalists = budget.get("finalists", 0)
            if len(finalists) < required_finalists:
                errors.append("termination:sufficient_finalists_not_reached")

    return sorted(set(errors))


def _diagnostics(errors: list[str]) -> list[dict]:
    return [{"code": e.replace(":", "."), "subject": e.split(":", 1)[0], "evidence": e} for e in errors]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        errors = validate(contract, state)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"state:unreadable:{exc.__class__.__name__}"]
    result = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "diagnostics": _diagnostics(errors),
    }
    rendered = dump_json(result)
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
