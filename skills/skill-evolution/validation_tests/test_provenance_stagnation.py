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


contract_mod = load("contract_stagnation", SCRIPTS / "validate_evidence_aware_search_contract.py")
request_mod = load("request_provenance", SCRIPTS / "validate_evidence_aware_candidate_request.py")
state_mod = load("state_provenance", SCRIPTS / "validate_evidence_aware_search_state.py")
checkpoint_mod = load("checkpoint_semantic", SCRIPTS / "checkpoint_search_state_evidence_aware.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def test_contract_rejects_unknown_stagnation_policy():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["stagnation_policy"] = {"id": "unknown-policy"}
    assert "stagnation_policy:invalid" in contract_mod.validate(contract)


def test_candidate_request_rejects_deficit_not_addressed_by_transformations():
    contract = template("search-contract-evidence-aware.json.template")
    state = template("search-state-evidence-aware.json.template")
    request = {
        "request_version": 2,
        "candidate_id": "C002",
        "operator": "bounded-mutation",
        "base_parent_id": "C_CANONICAL",
        "donor_parent_ids": [],
        "transformation_ids": ["T003"],
        "expected_capability_effects": ["lineage-integrity"],
        "reason": "test deficit provenance",
        "hypothesis_ids": ["H004"],
        "deficit_ids": ["activation-ambiguity"],
    }
    errors = request_mod.validate(contract, state, request)
    assert "deficit_ids:not_addressed:activation-ambiguity" in errors


def test_search_state_rejects_unaddressed_deficit_provenance():
    contract = template("search-contract-evidence-aware.json.template")
    state = template("search-state-evidence-aware.json.template")
    candidate = state["candidates"][0]
    candidate["hypothesis_ids"] = ["H004"]
    candidate["deficit_ids"] = ["activation-ambiguity"]
    errors = state_mod.validate(contract, state)
    assert "candidate:C_CANONICAL:deficit_ids:not_addressed:activation-ambiguity" in errors


def test_semantic_stagnation_ignores_transformation_only_novelty():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["stagnation_policy"] = {
        "id": "pareto-plus-semantic-signatures-v1",
        "include_behavior_descriptors": True,
        "include_deficit_coverage": True,
    }
    state0 = template("search-state-evidence-aware.json.template")
    state0["candidates"][0]["evaluation"]["behavior_descriptor"] = {
        "descriptor_id": "skill-behavior-v1",
        "labels": ["activation"],
    }
    receipt0, errors = checkpoint_mod.build_receipt(contract, state0)
    assert errors == []

    state1 = copy.deepcopy(state0)
    state1["round"] = 1
    state1["stagnant_rounds"] = 1
    extra = copy.deepcopy(state1["candidates"][0])
    extra["candidate_id"] = "C002"
    extra["candidate_identity"] = "candidate-C002-bytes"
    extra["role"] = "novel-bounded"
    extra["status"] = "evaluating"
    extra["transformation_ids"] = ["T003"]
    extra["expected_capability_effects"] = ["lineage-integrity"]
    extra["generation_receipt"]["receipt_identity"] = "receipt-C002"
    extra["generation_receipt"]["candidate_identity"] = "candidate-C002-bytes"
    extra["generation_receipt"]["transformation_ids"] = ["T003"]
    state1["candidates"].append(extra)

    receipt1, errors = checkpoint_mod.build_receipt(contract, state1, receipt0)
    assert errors == []
    assert receipt1["stagnant_round"] is True
    assert receipt1["semantic_stagnation"] is True


def test_semantic_stagnation_resets_when_behavior_signature_changes():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["stagnation_policy"] = {
        "id": "pareto-plus-semantic-signatures-v1",
        "include_behavior_descriptors": True,
        "include_deficit_coverage": False,
    }
    state0 = template("search-state-evidence-aware.json.template")
    state0["candidates"][0]["evaluation"]["behavior_descriptor"] = {
        "descriptor_id": "skill-behavior-v1",
        "labels": ["activation"],
    }
    receipt0, errors = checkpoint_mod.build_receipt(contract, state0)
    assert errors == []

    state1 = copy.deepcopy(state0)
    state1["round"] = 1
    state1["stagnant_rounds"] = 0
    state1["candidates"][0]["evaluation"]["evaluation_ref"] = "evaluation-round-1"
    state1["candidates"][0]["evaluation"]["behavior_descriptor"]["labels"] = ["portability"]

    receipt1, errors = checkpoint_mod.build_receipt(contract, state1, receipt0)
    assert errors == []
    assert receipt1["stagnant_round"] is False
    assert receipt1["semantic_stagnation"] is False
