import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


recomb = load("recomb_v2", SCRIPTS / "plan_recombination.py")
request_validator = load("request_validator_v2", SCRIPTS / "validate_candidate_request.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def seed_candidate(base, cid, role, transforms, effects):
    c = copy.deepcopy(base)
    c["candidate_id"] = cid
    c["role"] = role
    c["candidate_identity"] = f"bytes-{cid}"
    c["transformation_ids"] = transforms
    c["expected_capability_effects"] = effects
    c["generation_receipt"]["receipt_identity"] = f"receipt-{cid}"
    c["generation_receipt"]["candidate_identity"] = f"bytes-{cid}"
    c["generation_receipt"]["transformation_ids"] = transforms
    return c


def test_recombination_returns_validated_merge():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    canonical = seed_candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"])
    focused = seed_candidate(base, "C002", "focused", ["T002"], ["activation"])
    state = {"candidates": [canonical, focused]}
    result = recomb.plan(contract, state, ["C_CANONICAL", "C002"])
    assert result["proposals"]
    proposal = result["proposals"][0]
    assert proposal["request_version"] == 2
    assert proposal["operator"] == "transformation-merge"
    assert proposal["base_parent_id"] == "C_CANONICAL"
    assert proposal["transformation_ids"] == ["T001", "T002"]
    assert proposal["expected_capability_effects"] == ["activation", "canonical-baseline"]
    assert request_validator.validate(contract, state, proposal) == []


def test_recombination_rejects_declared_conflict():
    contract = template("search-contract.json.template")
    for item in contract["transformation_registry"]:
        if item["id"] == "T002":
            item["conflicts_with"] = ["T003"]
    base = template("search-state.json.template")["candidates"][0]
    a = seed_candidate(base, "C002", "focused", ["T002"], ["activation"])
    b = seed_candidate(base, "C003", "novel-bounded", ["T003"], ["lineage-integrity"])
    result = recomb.plan(contract, {"candidates": [a, b]}, ["C002", "C003"])
    assert result["proposals"] == []
    assert any("transformation_conflict:T002:T003" in error for skip in result["skipped"] for error in skip.get("errors", []))


def test_recombination_closes_dependencies_before_request():
    contract = template("search-contract.json.template")
    for item in contract["transformation_registry"]:
        if item["id"] == "T003":
            item["depends_on"] = ["T002"]
    base = template("search-state.json.template")["candidates"][0]
    canonical = seed_candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"])
    donor = seed_candidate(base, "C003", "novel-bounded", ["T003"], ["lineage-integrity"])
    result = recomb.plan(contract, {"candidates": [canonical, donor]}, ["C_CANONICAL", "C003"])
    assert result["proposals"][0]["transformation_ids"] == ["T001", "T002", "T003"]


def test_request_validator_rejects_capability_invariant_violation():
    contract = template("search-contract.json.template")
    contract["transformation_registry"].append({
        "id":"T004",
        "status":"proposed",
        "depends_on":[],
        "conflicts_with":[],
        "capability_effects":["authority"],
        "violates_invariants":["authority-boundary"],
        "addresses":[]
    })
    state = template("search-state.json.template")
    request = {
        "request_version": 2,
        "candidate_id": "C004",
        "operator": "bounded-mutation",
        "base_parent_id": "C_CANONICAL",
        "donor_parent_ids": [],
        "transformation_ids": ["T001", "T004"],
        "expected_capability_effects": ["authority", "canonical-baseline"],
        "reason": "test invariant gate"
    }
    errors = request_validator.validate(contract, state, request)
    assert "transformation:T004:violates_invariant:authority-boundary" in errors


def test_request_validator_rejects_duplicate_base_and_transform_set():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    request = {
        "request_version": 2,
        "candidate_id": "C004",
        "operator": "bounded-mutation",
        "base_parent_id": "BASELINE",
        "donor_parent_ids": [],
        "transformation_ids": ["T001"],
        "expected_capability_effects": ["canonical-baseline"],
        "reason": "duplicate canonical strategy"
    }
    errors = request_validator.validate(contract, state, request)
    assert "strategy:duplicate:C_CANONICAL" in errors
