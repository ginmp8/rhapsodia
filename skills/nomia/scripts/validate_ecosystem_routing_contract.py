#!/usr/bin/env python3
"""Validate distributed routing, canonical scenario identities, and owner sequencing."""
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path
from typing import Any

CATEGORIES = {"single_owner", "multi_intent", "ambiguous", "non_activation", "adversarial", "edge_case"}
OWNERS = {"nomia", "mago", "magia", "none"}
STALE_PATTERNS = (
    re.compile(r"docs/boards/[^\s\"']+/v1(?:/|\b)", re.I),
    re.compile(r"\bcycle[ _-]?version\b", re.I),
    re.compile(r"\bcycle\s+\d{4}\.\d{2}\b", re.I),
    re.compile(r"\bspec\d{3,}\b", re.I),
    re.compile(r"\bcycle_id\s*[:=]?\s*v\d+\b", re.I),
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)


def legacy_allowed(blob: str) -> bool:
    text = blob.lower()
    return ("legacy" in text or "migration" in text) and ("adapt" in text or "migration" in text)


def validate_local_scenarios(root: Path) -> list[str]:
    errors = []
    paths = [root / "examples" / "activation-scenarios.json"] + sorted((root / "evals").glob("*.json"))
    for path in paths:
        if not path.is_file():
            continue
        try:
            data = load(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(root)} is invalid JSON: {exc}")
            continue
        items = data.get("scenarios", []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            blob = "\n".join(all_strings(item))
            if legacy_allowed(blob):
                continue
            for pattern in STALE_PATTERNS:
                match = pattern.search(blob)
                if match:
                    errors.append(f"{path.relative_to(root)} scenario {item.get('id', index)} uses retired current-path vocabulary: {match.group(0)}")
    return errors


def validate(root: Path) -> dict[str, Any]:
    errors, warnings = [], []
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    contract = load(root / "references/ecosystem-routing-contract.json")
    corpus = load(root / "evals/ecosystem-routing-scenarios.json")
    if contract.get("contract_id") != "nomia-mago-magia-routing-v1": errors.append("unexpected routing contract_id")
    if contract.get("ecosystem_release") != version: errors.append("routing contract release does not match VERSION")
    if corpus.get("contract_id") != contract.get("contract_id"): errors.append("routing corpus contract_id mismatch")
    if corpus.get("ecosystem_release") != version: errors.append("routing corpus release does not match VERSION")
    allowed = set(contract.get("allowed_handoffs", []))
    scenarios = corpus.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios: errors.append("routing corpus must have scenarios"); scenarios = []
    counts = Counter()
    seen = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict): errors.append(f"scenario {index} is not an object"); continue
        sid = scenario.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"ROUTE-[A-Z]-\d{3}", sid): errors.append(f"scenario {index} has invalid id {sid!r}")
        elif sid in seen: errors.append(f"duplicate routing scenario id {sid}")
        seen.add(sid)
        category = scenario.get("category")
        if category not in CATEGORIES: errors.append(f"{sid}: invalid category {category!r}")
        else: counts[category] += 1
        prompt = scenario.get("prompt")
        behavior = scenario.get("expected_behavior")
        first = scenario.get("expected_first_owner")
        sequence = scenario.get("owner_sequence")
        mutate = scenario.get("mutation_allowed_after_owner_resolution")
        if not isinstance(prompt, str) or len(prompt.split()) < 5: errors.append(f"{sid}: prompt is too short")
        if not isinstance(behavior, str) or len(behavior.split()) < 7: errors.append(f"{sid}: expected_behavior is too short")
        if first not in OWNERS: errors.append(f"{sid}: invalid first owner {first!r}")
        if not isinstance(sequence, list) or any(owner not in OWNERS - {"none"} for owner in sequence): errors.append(f"{sid}: invalid owner_sequence"); sequence = []
        if first == "none":
            if sequence: errors.append(f"{sid}: none first owner requires empty sequence")
            if mutate is not False: errors.append(f"{sid}: unresolved owner must prohibit mutation")
        else:
            if not sequence or sequence[0] != first: errors.append(f"{sid}: sequence must begin with expected_first_owner")
        if category == "multi_intent" and len(sequence) < 2: errors.append(f"{sid}: multi_intent requires at least two owner phases")
        for left, right in zip(sequence, sequence[1:]):
            direction = f"{left}_to_{right}"
            if direction not in allowed: errors.append(f"{sid}: unsupported owner transition {direction}")
        blob = "\n".join(all_strings(scenario))
        for pattern in STALE_PATTERNS:
            if pattern.search(blob): errors.append(f"{sid}: routing corpus uses retired vocabulary {pattern.search(blob).group(0)}")
    for category in CATEGORIES:
        if counts[category] < 4: errors.append(f"routing category {category} has {counts[category]}; expected at least 4")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    if "ecosystem-routing-contract.md" not in skill_text: errors.append("SKILL.md must reference the distributed routing contract")
    errors.extend(validate_local_scenarios(root))
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "scenario_count": len(scenarios), "counts": dict(counts), "measurement_kind": corpus.get("measurement_kind")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate(Path(args.target).resolve())
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status: {result['status']}")
    print(f"scenario_count: {result.get('scenario_count', 0)}")
    print(f"measurement_kind: {result.get('measurement_kind')}")
    for error in result["errors"]: print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1

if __name__ == "__main__": raise SystemExit(main())
