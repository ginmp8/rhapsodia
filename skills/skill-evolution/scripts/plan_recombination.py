from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

def distance(a: dict, b: dict) -> float:
    sa, sb = set(a.get("transformation_ids", [])), set(b.get("transformation_ids", []))
    if not sa and not sb:
        return 0.0
    return 1.0 - (len(sa & sb) / len(sa | sb))

def next_ids(state: dict, count: int) -> list[str]:
    nums = []
    for c in state.get("candidates", []):
        m = re.fullmatch(r"C(\d+)", str(c.get("candidate_id", "")))
        if m:
            nums.append(int(m.group(1)))
    start = max(nums, default=0) + 1
    return [f"C{n:03d}" for n in range(start, start + count)]

def request(cid: str, operator: str, base: str, donors: list[str], transformations: list[str], reason: str) -> dict:
    return {
        "request_version": 1,
        "candidate_id": cid,
        "operator": operator,
        "base_parent_id": base,
        "donor_parent_ids": donors,
        "transformation_ids": transformations,
        "reason": reason,
    }

def plan(contract: dict, state: dict, survivors: list[str]) -> dict:
    by_id = {c["candidate_id"]: c for c in state.get("candidates", [])}
    chosen = [by_id[c] for c in survivors if c in by_id]
    max_props = contract["budget"].get("max_recombination_proposals_per_round", 3)
    raw: list[dict] = []
    canonical_id = contract.get("canonical_candidate_id")
    pairs = sorted(
        itertools.combinations(chosen, 2),
        key=lambda p: (-distance(p[0], p[1]), p[0]["candidate_id"], p[1]["candidate_id"]),
    )
    for a, b in pairs:
        merged = sorted(set(a.get("transformation_ids", [])) | set(b.get("transformation_ids", [])))
        if not merged or set(a.get("transformation_ids", [])) == set(b.get("transformation_ids", [])):
            continue
        raw.append(("transformation-merge", a["candidate_id"], [b["candidate_id"]], merged, "complementary transformation sets among survivors"))
        if len(raw) >= max_props:
            break
    if len(raw) < max_props and canonical_id in by_id:
        canonical = by_id[canonical_id]
        canon_t = set(canonical.get("transformation_ids", []))
        for c in chosen:
            if c["candidate_id"] == canonical_id:
                continue
            unique = sorted(set(c.get("transformation_ids", [])) - canon_t)
            if unique:
                raw.append(("backcross", canonical_id, [c["candidate_id"]], sorted(canon_t | set(unique)), "retain survivor novelty while restoring canonical base"))
                break
    ids = next_ids(state, min(len(raw), max_props))
    proposals = [request(cid, *item) for cid, item in zip(ids, raw[:max_props])]
    return {"status": "pass", "proposals": proposals}

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
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        Path(args.json_output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0

if __name__ == "__main__":
    sys.exit(main())
