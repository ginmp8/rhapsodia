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


mod = load("selection_v2", SCRIPTS / "select_survivors.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def candidate(base, cid, role, transforms, effects, quality, token_cost, uncertainty=0.0):
    c = copy.deepcopy(base)
    c["candidate_id"] = cid
    c["role"] = role
    c["candidate_identity"] = f"bytes-{cid}"
    c["transformation_ids"] = transforms
    c["expected_capability_effects"] = effects
    c["generation_receipt"]["receipt_identity"] = f"receipt-{cid}"
    c["generation_receipt"]["candidate_identity"] = f"bytes-{cid}"
    c["generation_receipt"]["transformation_ids"] = transforms
    c["evaluation"]["metrics"] = {
        "quality": {"value": quality, "uncertainty": uncertainty},
        "token_cost": {"value": token_cost, "uncertainty": 0},
    }
    return c


def test_failed_gate_eliminated_and_tradeoffs_survive():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.95, 1200)
    c = candidate(base, "C003", "novel-bounded", ["T003"], ["lineage-integrity"], 1.0, 800)
    c["evaluation"]["hard_gates"]["safety"] = "fail"
    result = mod.select(contract, {"candidates": [a, b, c]})
    assert result["eliminated_hard_gate"] == ["C003"]
    assert set(result["pareto_frontier"]) == {"C002", "C_CANONICAL"}


def test_min_delta_prevents_noise_from_becoming_dominance():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.91, 1000)
    result = mod.select(contract, {"candidates": [a, b]})
    assert set(result["pareto_frontier"]) == {"C002", "C_CANONICAL"}


def test_uncertainty_expands_material_improvement_margin():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.94, 1000, uncertainty=0.03)
    result = mod.select(contract, {"candidates": [a, b]})
    assert set(result["pareto_frontier"]) == {"C002", "C_CANONICAL"}


def test_preserved_canonical_remains_selected_even_when_dominated():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.95, 900)
    result = mod.select(contract, {"candidates": [a, b]})
    assert result["pareto_frontier"] == ["C002"]
    assert "C_CANONICAL" in result["selected_survivors"]
    assert "C002" in result["selected_survivors"]


def test_mismatched_evaluator_is_not_compared():
    contract = template("search-contract.json.template")
    base = template("search-state.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 1.0, 500)
    b["evaluation"]["identity"]["policy_id"] = "different-policy"
    result = mod.select(contract, {"candidates": [a, b]})
    assert result["incompatible_evidence"] == ["C002"]
    assert result["pareto_frontier"] == ["C_CANONICAL"]
