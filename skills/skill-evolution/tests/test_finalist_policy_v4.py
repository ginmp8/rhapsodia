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


contract_mod = load("contract_v4_finalist", SCRIPTS / "validate_search_contract.py")
state_mod = load("state_v4_finalist", SCRIPTS / "validate_search_state.py")


def template(name):
    return json.loads((ROOT / "assets" / "templates" / name).read_text())


def finalist_state(contract, level="L4-benchmark", holdout_status="not-used"):
    state = template("search-state.json.template")
    cand = state["candidates"][0]
    cand["status"] = "finalist"
    cand["evaluation"]["level"] = level
    cand["evaluation"]["holdout_status"] = holdout_status
    state["finalists"] = [cand["candidate_id"]]
    return state


def test_search_contract_v4_requires_finalist_policy():
    contract = template("search-contract.json.template")
    assert contract["contract_version"] == 4
    assert contract["finalist_policy"] == {
        "minimum_evaluation_level": "L4-benchmark",
        "holdout_policy": "not-required",
    }
    assert contract_mod.validate(contract) == []


def test_state_v4_rejects_l2_finalist_when_minimum_is_l4():
    contract = template("search-contract.json.template")
    state = finalist_state(contract, level="L2-focused")
    errors = state_mod.validate(contract, state)
    assert "candidate:C_CANONICAL:finalist_evaluation_level_below_minimum" in errors


def test_state_v4_requires_blind_pass_when_policy_requires_holdout():
    contract = template("search-contract.json.template")
    contract["finalist_policy"] = {
        "minimum_evaluation_level": "L5-holdout",
        "holdout_policy": "blind-pass-required",
    }
    state = finalist_state(contract, level="L5-holdout", holdout_status="revealed-development")
    errors = state_mod.validate(contract, state)
    assert "candidate:C_CANONICAL:finalist_blind_holdout_required" in errors


def test_sufficient_finalists_termination_requires_full_finalist_quota():
    contract = template("search-contract.json.template")
    state = finalist_state(contract)
    state["status"] = "terminated"
    state["termination_reason"] = "sufficient-finalists"
    errors = state_mod.validate(contract, state)
    assert "termination:sufficient_finalists_not_reached" in errors


def test_finalist_status_must_be_reflected_in_finalists_list():
    contract = template("search-contract.json.template")
    state = finalist_state(contract)
    state["finalists"] = []
    errors = state_mod.validate(contract, state)
    assert "finalists:missing:C_CANONICAL" in errors
