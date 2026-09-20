from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


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
