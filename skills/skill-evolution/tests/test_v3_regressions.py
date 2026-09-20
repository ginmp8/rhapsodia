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


selection = load("selection_v3_reg", SCRIPTS / "select_survivors.py")
state_mod = load("state_v3_reg", SCRIPTS / "validate_search_state.py")
checkpoint = load("checkpoint_v3_reg", SCRIPTS / "checkpoint_search_state.py")


def template(name):
    return json.loads((ROOT / "assets" / "templates" / name).read_text())


def candidate(base, cid, level="L4-benchmark", evidence_type="measured", quality=0.90, token_cost=1000, transform="T001"):
    c = copy.deepcopy(base)
    c["candidate_id"] = cid
    c["candidate_identity"] = f"bytes-{cid}"
    c["generation_receipt"]["receipt_identity"] = f"receipt-{cid}"
    c["generation_receipt"]["candidate_identity"] = f"bytes-{cid}"
    c["transformation_ids"] = [transform]
    c["expected_capability_effects"] = ["canonical-baseline" if transform == "T001" else "activation"]
    c["generation_receipt"]["transformation_ids"] = [transform]
    c["evaluation"]["evaluation_ref"] = f"eval-{cid}"
    c["evaluation"]["level"] = level
    c["evaluation"]["evidence_type"] = evidence_type
    c["evaluation"]["metrics"] = {
        "quality": {"value": quality, "uncertainty": 0},
        "token_cost": {"value": token_cost, "uncertainty": 0},
    }
    return c


def test_templates_use_v3_search_contract_and_state():
    assert template("search-contract.json.template")["contract_version"] == 3
    assert template("search-state.json.template")["state_version"] == 3


def test_planned_evidence_is_not_selection_eligible():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    measured = candidate(base, "C_MEASURED", evidence_type="measured", quality=0.90, token_cost=1000)
    planned = candidate(base, "C_PLANNED", evidence_type="planned", quality=0.99, token_cost=800, transform="T002")
    result = selection.select(contract, {"state_version": 3, "search_id": contract["search_id"], "round": 0, "stagnant_rounds": 0, "status": "active", "candidates": [measured, planned], "pareto_archive": [], "finalists": [], "termination_reason": None})
    assert result["status"] == "pass"
    assert result["eligible"] == ["C_MEASURED"]
    assert result["ineligible_evidence"] == ["C_PLANNED"]


def test_blind_fail_is_never_selection_eligible():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    good = candidate(base, "C_GOOD", level="L4-benchmark", quality=0.90)
    failed = candidate(base, "C_FAIL", level="L5-holdout", quality=0.99, transform="T002")
    failed["evaluation"]["holdout_status"] = "blind-fail"
    result = selection.select(contract, {"state_version": 3, "search_id": contract["search_id"], "round": 0, "stagnant_rounds": 0, "status": "active", "candidates": [good, failed], "pareto_archive": [], "finalists": [], "termination_reason": None})
    assert result["status"] == "pass"
    assert "C_FAIL" not in result["eligible"]
    assert result["eliminated_holdout"] == ["C_FAIL"]


def test_different_evaluation_levels_do_not_dominate_each_other():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    l4 = candidate(base, "C_L4", level="L4-benchmark", quality=0.90, token_cost=1000)
    l2 = candidate(base, "C_L2", level="L2-focused", quality=0.99, token_cost=800, transform="T002")
    result = selection.select(contract, {"state_version": 3, "search_id": contract["search_id"], "round": 0, "stagnant_rounds": 0, "status": "active", "candidates": [l4, l2], "pareto_archive": [], "finalists": [], "termination_reason": None})
    assert set(result["pareto_frontier"]) == {"C_L2", "C_L4"}


def test_selection_refuses_invalid_search_state():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    state["candidates"][0].pop("generation_receipt")
    result = selection.select(contract, state)
    assert result["status"] == "fail"
    assert "candidate:C_CANONICAL:generation_receipt_required" in result["errors"]


def test_state_rejects_duplicate_materialized_candidate_identity():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    second = copy.deepcopy(state["candidates"][0])
    second["candidate_id"] = "C002"
    second["generation_receipt"]["receipt_identity"] = "receipt-C002"
    second["transformation_ids"] = ["T002"]
    second["expected_capability_effects"] = ["activation"]
    second["generation_receipt"]["transformation_ids"] = ["T002"]
    state["candidates"].append(second)
    errors = state_mod.validate(contract, state)
    assert "candidate_identity:duplicate" in errors


def test_active_candidate_requires_evaluation_ref():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    state["candidates"][0]["evaluation"].pop("evaluation_ref")
    assert "candidate:C_CANONICAL:evaluation_ref_required" in state_mod.validate(contract, state)


def test_checkpoint_refuses_invalid_state():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    state["candidates"][0].pop("generation_receipt")
    _, errors = checkpoint.build_receipt(contract, state)
    assert "candidate:C_CANONICAL:generation_receipt_required" in errors
