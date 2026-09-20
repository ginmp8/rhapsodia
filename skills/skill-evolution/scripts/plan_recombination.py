from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import (
    capability_effects,
    dump_json,
    expand_dependencies,
    metric_value,
    request_signature,
    transformation_map,
    validate_transform_set,
)


def distance(a: dict, b: dict) -> float:
    sa, sb = set(a.get("transformation_ids", [])), set(b.get("transformation_ids", []))
    if not sa and not sb:
        return 0.0
    return 1.0 - (len(sa & sb) / len(sa | sb))


def uncertainty(candidate: dict, contract: dict) -> float:
    evaluation = candidate.get("evaluation", {})
    metrics = evaluation.get("metrics", {}) if isinstance(evaluation, dict) else {}
    total = 0.0
    for objective in contract.get("objectives", []):
        parsed = metric_value(metrics.get(objective.get("name")))
        if parsed is None:
            return float("inf")
        total += parsed[1]
    return total


def next_ids(state: dict, count: int) -> list[str]:
    nums = []
    for c in state.get("candidates", []):
        m = re.fullmatch(r"C(\d+)", str(c.get("candidate_id", "")))
        if m:
            nums.append(int(m.group(1)))
    start = max(nums, default=0) + 1
    return [f"C{n:03d}" for n in range(start, start + count)]


def _choose_base(a: dict, b: dict, contract: dict) -> tuple[dict, dict]:
    canonical_id = contract.get("canonical_candidate_id")
    if a.get("candidate_id") == canonical_id:
        return a, b
    if b.get("candidate_id") == canonical_id:
        return b, a
    ordered = sorted((a, b), key=lambda c: (uncertainty(c, contract), c.get("candidate_id", "")))
    return ordered[0], ordered[1]


def _request(
    cid: str,
    operator: str,
    base: str,
    donors: list[str],
    transformations: list[str],
    reason: str,
    contract: dict,
) -> dict:
    return {
        "request_version": 2,
        "candidate_id": cid,
        "operator": operator,
        "base_parent_id": base,
        "donor_parent_ids": donors,
        "transformation_ids": transformations,
        "expected_capability_effects": capability_effects(transformations, contract),
        "reason": reason,
        "request_signature": request_signature(base, transformations),
    }


def _existing_signatures(state: dict) -> set[str]:
    result: set[str] = set()
    for candidate in state.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        base = candidate.get("base_parent_id")
        transformations = candidate.get("transformation_ids")
        if isinstance(base, str) and isinstance(transformations, list):
            result.add(request_signature(base, transformations))
    return result


def _compatible(ids: list[str], contract: dict) -> tuple[list[str] | None, list[str]]:
    registry = transformation_map(contract)
    try:
        expanded = expand_dependencies(ids, registry)
    except ValueError as exc:
        return None, [str(exc)]
    errors = validate_transform_set(expanded, contract)
    return (expanded if not errors else None), errors


def plan(contract: dict, state: dict, survivors: list[str]) -> dict:
    by_id = {c["candidate_id"]: c for c in state.get("candidates", []) if isinstance(c, dict) and c.get("candidate_id")}
    chosen = sorted((by_id[c] for c in survivors if c in by_id), key=lambda c: c["candidate_id"])
    max_props = contract["budget"].get("max_recombination_proposals_per_round", 3)
    current_total = len(state.get("candidates", []))
    remaining_budget = max(0, contract["budget"].get("max_total_candidates", 0) - current_total)
    limit = min(max_props, remaining_budget)
    if limit <= 0:
        return {"status": "pass", "proposals": [], "skipped": [{"reason": "candidate budget exhausted"}]}

    existing_signatures = _existing_signatures(state)
    planned_signatures: set[str] = set()
    raw: list[tuple[str, str, list[str], list[str], str]] = []
    skipped: list[dict] = []

    pairs = sorted(
        itertools.combinations(chosen, 2),
        key=lambda p: (-distance(p[0], p[1]), p[0]["candidate_id"], p[1]["candidate_id"]),
    )
    for a, b in pairs:
        merged_raw = sorted(set(a.get("transformation_ids", [])) | set(b.get("transformation_ids", [])))
        if not merged_raw or set(a.get("transformation_ids", [])) == set(b.get("transformation_ids", [])):
            continue
        merged, errors = _compatible(merged_raw, contract)
        if merged is None:
            skipped.append({"operator": "transformation-merge", "parents": [a["candidate_id"], b["candidate_id"]], "errors": errors})
            continue
        base_candidate, donor_candidate = _choose_base(a, b, contract)
        sig = request_signature(base_candidate["candidate_id"], merged)
        if sig in existing_signatures or sig in planned_signatures:
            skipped.append({"operator": "transformation-merge", "parents": [a["candidate_id"], b["candidate_id"]], "reason": "duplicate strategy"})
            continue
        planned_signatures.add(sig)
        raw.append((
            "transformation-merge",
            base_candidate["candidate_id"],
            [donor_candidate["candidate_id"]],
            merged,
            "combine complementary survivor transformations after dependency/conflict/invariant validation",
        ))
        if len(raw) >= limit:
            break

    canonical_id = contract.get("canonical_candidate_id")
    if len(raw) < limit and canonical_id in by_id:
        canonical = by_id[canonical_id]
        canon_t = set(canonical.get("transformation_ids", []))
        donors = sorted(
            (c for c in chosen if c["candidate_id"] != canonical_id),
            key=lambda c: (-distance(canonical, c), uncertainty(c, contract), c["candidate_id"]),
        )
        for donor in donors:
            unique = set(donor.get("transformation_ids", [])) - canon_t
            if not unique:
                continue
            merged, errors = _compatible(sorted(canon_t | unique), contract)
            if merged is None:
                skipped.append({"operator": "backcross", "parents": [canonical_id, donor["candidate_id"]], "errors": errors})
                continue
            sig = request_signature(canonical_id, merged)
            if sig in existing_signatures or sig in planned_signatures:
                continue
            planned_signatures.add(sig)
            raw.append((
                "backcross",
                canonical_id,
                [donor["candidate_id"]],
                merged,
                "retain donor transformations on the canonical base after compatibility validation",
            ))
            if len(raw) >= limit:
                break

    if len(raw) < limit:
        registry = transformation_map(contract)
        for candidate in chosen:
            evaluation = candidate.get("evaluation", {})
            deficits = set(evaluation.get("deficits", [])) if isinstance(evaluation, dict) else set()
            if not deficits:
                continue
            for tid, item in sorted(registry.items()):
                if tid in candidate.get("transformation_ids", []):
                    continue
                if not deficits.intersection(item.get("addresses", [])):
                    continue
                merged, errors = _compatible(sorted(set(candidate.get("transformation_ids", [])) | {tid}), contract)
                if merged is None:
                    skipped.append({"operator": "repair-crossover", "parent": candidate["candidate_id"], "transformation": tid, "errors": errors})
                    continue
                sig = request_signature(candidate["candidate_id"], merged)
                if sig in existing_signatures or sig in planned_signatures:
                    continue
                planned_signatures.add(sig)
                raw.append((
                    "repair-crossover",
                    candidate["candidate_id"],
                    [],
                    merged,
                    "apply a registry transformation that explicitly addresses a recorded non-blocking deficit",
                ))
                break
            if len(raw) >= limit:
                break

    ids = next_ids(state, len(raw))
    proposals = [_request(cid, *item, contract) for cid, item in zip(ids, raw)]
    return {"status": "pass", "proposals": proposals, "skipped": skipped}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--survivors", required=True, help="comma-separated candidate ids")
    parser.add_argument("--json-output")
    args = parser.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    survivors = [x for x in args.survivors.split(",") if x]
    result = plan(contract, state, survivors)
    rendered = dump_json(result)
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
