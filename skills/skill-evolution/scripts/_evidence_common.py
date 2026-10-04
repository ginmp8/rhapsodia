from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EVALUATION_SLICE_STATUSES = {"pass", "fail", "not-run", "blocked"}
UNCERTAINTY_KINDS = {
    "none",
    "standard-error",
    "standard-deviation",
    "confidence-interval-half-width",
    "bootstrap-ci-half-width",
    "external-bound",
}



def validate_evidence_profile_config(contract: dict) -> list[str]:
    profile = contract.get("evidence_aware")
    if not isinstance(profile, dict):
        return ["evidence_aware:required"]
    errors: list[str] = []
    if profile.get("profile_version") != 1:
        errors.append("evidence_aware.profile_version:unsupported")
    return errors


def expand_evidence_contract(contract: dict) -> dict:
    """Map evidence-profile v1 controls onto the additive internal validation shape."""
    expanded = copy.deepcopy(contract)
    profile = contract.get("evidence_aware")
    if not isinstance(profile, dict):
        return expanded
    policy = expanded.setdefault("selection_policy", {})
    for key in ("uncertainty_metadata_required", "stability_policy", "frontier_policy", "novelty_policy"):
        if key in profile:
            policy[key] = copy.deepcopy(profile[key])
    if "required_evaluation_slices" in profile:
        expanded["required_evaluation_slices"] = copy.deepcopy(profile["required_evaluation_slices"])
    if "complexity_policy" in profile:
        expanded["complexity_policy"] = copy.deepcopy(profile["complexity_policy"])
    if "stagnation_policy" in profile:
        expanded["stagnation_policy"] = copy.deepcopy(profile["stagnation_policy"])
    return expanded

def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_data(data: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()


def fail(message: str) -> None:
    raise ValueError(message)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def transformation_map(contract: dict) -> dict[str, dict]:
    registry = contract.get("transformation_registry", [])
    if not isinstance(registry, list):
        return {}
    result: dict[str, dict] = {}
    for item in registry:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def expand_dependencies(ids: list[str], registry: dict[str, dict]) -> list[str]:
    selected = set(ids)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(tid: str) -> None:
        if tid in visited:
            return
        if tid in visiting:
            raise ValueError(f"transformation_dependency_cycle:{tid}")
        item = registry.get(tid)
        if item is None:
            raise ValueError(f"unknown_transformation:{tid}")
        visiting.add(tid)
        for dep in item.get("depends_on", []):
            selected.add(dep)
            visit(dep)
        visiting.remove(tid)
        visited.add(tid)

    for tid in list(selected):
        visit(tid)
    return sorted(selected)


def validate_transform_set(ids: list[str], contract: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(ids, list) or any(not isinstance(x, str) or not x for x in ids):
        return ["transformation_ids:invalid"]
    if len(ids) != len(set(ids)):
        errors.append("transformation_ids:duplicate")
    registry = transformation_map(contract)
    invariants = set(contract.get("capability_invariants", []))
    selected = set(ids)
    for tid in ids:
        item = registry.get(tid)
        if item is None:
            errors.append(f"transformation:{tid}:unknown")
            continue
        if item.get("status") in {"rejected", "deprecated"}:
            errors.append(f"transformation:{tid}:status_not_eligible")
        for dep in item.get("depends_on", []):
            if dep not in selected:
                errors.append(f"transformation:{tid}:missing_dependency:{dep}")
        for conflict in item.get("conflicts_with", []):
            if conflict in selected:
                pair = ":".join(sorted((tid, conflict)))
                errors.append(f"transformation_conflict:{pair}")
        violated = sorted(set(item.get("violates_invariants", [])) & invariants)
        for invariant in violated:
            errors.append(f"transformation:{tid}:violates_invariant:{invariant}")
    return sorted(set(errors))


def capability_effects(ids: list[str], contract: dict) -> list[str]:
    registry = transformation_map(contract)
    effects: set[str] = set()
    for tid in ids:
        item = registry.get(tid, {})
        effects.update(x for x in item.get("capability_effects", []) if isinstance(x, str))
    return sorted(effects)


def addressed_deficits(ids: list[str], contract: dict) -> set[str]:
    registry = transformation_map(contract)
    values: set[str] = set()
    for tid in ids:
        item = registry.get(tid, {})
        values.update(x for x in item.get("addresses", []) if isinstance(x, str) and x)
    return values


def validate_provenance_fields(record: dict, transformation_ids: list[str], contract: dict) -> list[str]:
    """Validate optional hypothesis/deficit provenance without widening controller authority."""
    errors: list[str] = []
    for field in ("hypothesis_ids", "deficit_ids"):
        if field not in record:
            continue
        values = record.get(field)
        if not isinstance(values, list) or any(not _nonempty_string(value) for value in values) or len(values) != len(set(values)):
            errors.append(f"{field}:invalid")

    deficits = record.get("deficit_ids")
    if isinstance(deficits, list) and isinstance(transformation_ids, list):
        addressed = addressed_deficits(transformation_ids, contract)
        for deficit in sorted(value for value in deficits if _nonempty_string(value) and value not in addressed):
            errors.append(f"deficit_ids:not_addressed:{deficit}")
    return sorted(set(errors))


def request_signature(base_parent_id: str, transformation_ids: list[str]) -> str:
    return sha256_data({
        "base_parent_id": base_parent_id,
        "transformation_ids": sorted(transformation_ids),
    })


def transformation_signature(transformation_ids: list[str]) -> str:
    return sha256_data({"transformation_ids": sorted(transformation_ids)})


def metric_value(raw: Any) -> tuple[float, float] | None:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        value = float(raw)
        if math.isfinite(value):
            return value, 0.0
        return None
    if isinstance(raw, dict):
        value = raw.get("value")
        uncertainty = raw.get("uncertainty", 0.0)
        if isinstance(value, bool) or isinstance(uncertainty, bool):
            return None
        if isinstance(value, (int, float)) and isinstance(uncertainty, (int, float)):
            value_f = float(value)
            uncertainty_f = float(uncertainty)
            if math.isfinite(value_f) and math.isfinite(uncertainty_f) and uncertainty_f >= 0:
                return value_f, uncertainty_f
    return None


def evaluation_identity_matches(candidate: dict, contract: dict) -> bool:
    evaluation = candidate.get("evaluation")
    if not isinstance(evaluation, dict):
        return False
    identity = evaluation.get("identity")
    expected = contract.get("evaluation_identity")
    return isinstance(identity, dict) and identity == expected


def validate_evaluation_extensions(contract: dict, evaluation: dict) -> list[str]:
    """Validate optional additive evidence metadata for v4/v2 compatibility."""
    errors: list[str] = []
    policy = contract.get("selection_policy", {}) if isinstance(contract.get("selection_policy"), dict) else {}

    statistics = evaluation.get("statistics")
    if statistics is not None:
        if not isinstance(statistics, dict):
            errors.append("statistics:invalid")
        else:
            if not _positive_int(statistics.get("case_count")):
                errors.append("statistics.case_count:invalid")
            if not _positive_int(statistics.get("trial_count")):
                errors.append("statistics.trial_count:invalid")
            kind = statistics.get("uncertainty_kind")
            if kind not in UNCERTAINTY_KINDS:
                errors.append("statistics.uncertainty_kind:invalid")
            confidence = statistics.get("confidence_level")
            if confidence is not None:
                if not _finite_number(confidence) or not 0 < float(confidence) < 1:
                    errors.append("statistics.confidence_level:invalid")
            if kind in {"confidence-interval-half-width", "bootstrap-ci-half-width"} and confidence is None:
                errors.append("statistics.confidence_level:required")
            for key in ("paired_evaluation_group_id", "scenario_results_ref"):
                value = statistics.get(key)
                if value is not None and not _nonempty_string(value):
                    errors.append(f"statistics.{key}:invalid")
    elif policy.get("uncertainty_metadata_required") is True:
        errors.append("statistics:required")

    if policy.get("uncertainty_metadata_required") is True and isinstance(statistics, dict):
        any_uncertainty = False
        metrics = evaluation.get("metrics", {})
        if isinstance(metrics, dict):
            for raw in metrics.values():
                parsed = metric_value(raw)
                if parsed is not None and parsed[1] > 0:
                    any_uncertainty = True
                    break
        if any_uncertainty and statistics.get("uncertainty_kind") == "none":
            errors.append("statistics.uncertainty_kind:cannot_be_none")

    slices = evaluation.get("slices")
    if slices is not None:
        if not isinstance(slices, dict) or any(not _nonempty_string(k) for k in slices):
            errors.append("slices:invalid")
        elif any(value not in EVALUATION_SLICE_STATUSES for value in slices.values()):
            errors.append("slices:status_invalid")
    required_slices = contract.get("required_evaluation_slices", [])
    if isinstance(required_slices, list) and required_slices:
        if not isinstance(slices, dict):
            errors.append("slices:required")
        else:
            missing = sorted(set(required_slices) - set(slices))
            if missing:
                errors.append("slices:missing:" + ",".join(missing))

    stability_policy = policy.get("stability_policy")
    stability = evaluation.get("stability")
    if stability is not None:
        if not isinstance(stability, dict):
            errors.append("stability:invalid")
        else:
            if not _nonempty_string(stability.get("method_id")):
                errors.append("stability.method_id:invalid")
            win_rate = stability.get("win_rate")
            if not _finite_number(win_rate) or not 0 <= float(win_rate) <= 1:
                errors.append("stability.win_rate:invalid")
            if not _positive_int(stability.get("resamples")):
                errors.append("stability.resamples:invalid")
    if isinstance(stability_policy, dict) and stability_policy.get("id") == "minimum-win-rate-v1":
        if not isinstance(stability, dict):
            errors.append("stability:required")
        else:
            if stability.get("method_id") != stability_policy.get("method_id"):
                errors.append("stability.method_id:mismatch")
            resamples = stability.get("resamples")
            minimum_resamples = stability_policy.get("minimum_resamples")
            if _positive_int(resamples) and _positive_int(minimum_resamples) and resamples < minimum_resamples:
                errors.append("stability.resamples:below_minimum")

    scenario_scores = evaluation.get("scenario_scores")
    if scenario_scores is not None:
        if not isinstance(scenario_scores, dict) or not scenario_scores:
            errors.append("scenario_scores:invalid")
        else:
            for key, value in scenario_scores.items():
                if not _nonempty_string(key) or not _finite_number(value):
                    errors.append("scenario_scores:invalid")
                    break
    frontier_policy = policy.get("frontier_policy")
    if isinstance(frontier_policy, dict) and frontier_policy.get("id") == "aggregate-plus-scenario-elites-v1":
        if not isinstance(scenario_scores, dict) or not scenario_scores:
            errors.append("scenario_scores:required")

    descriptor = evaluation.get("behavior_descriptor")
    if descriptor is not None:
        if not isinstance(descriptor, dict):
            errors.append("behavior_descriptor:invalid")
        else:
            if not _nonempty_string(descriptor.get("descriptor_id")):
                errors.append("behavior_descriptor.descriptor_id:invalid")
            labels = descriptor.get("labels")
            if not isinstance(labels, list) or any(not _nonempty_string(x) for x in labels) or len(labels) != len(set(labels)):
                errors.append("behavior_descriptor.labels:invalid")
    novelty_policy = policy.get("novelty_policy")
    if isinstance(novelty_policy, dict) and novelty_policy.get("id") == "behavior-label-jaccard-v1":
        if not isinstance(descriptor, dict):
            errors.append("behavior_descriptor:required")
        elif descriptor.get("descriptor_id") != novelty_policy.get("descriptor_id"):
            errors.append("behavior_descriptor.descriptor_id:mismatch")

    return sorted(set(errors))
