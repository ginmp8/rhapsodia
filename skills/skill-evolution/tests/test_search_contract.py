import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

contract_mod = load("contract", ROOT / "scripts/validate_search_contract.py")
state_mod = load("state", ROOT / "scripts/validate_search_state.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def test_contract_template_valid():
    assert contract_mod.validate(template("search-contract.json.template")) == []


def test_contract_rejects_budget_above_20():
    c = template("search-contract.json.template")
    c["budget"]["max_total_candidates"] = 21
    assert "budget:max_total_candidates_exceeds_20" in contract_mod.validate(c)


def test_state_template_valid():
    c = template("search-contract.json.template")
    s = template("search-state.json.template")
    assert state_mod.validate(c, s) == []


def test_state_rejects_cycle():
    c = template("search-contract.json.template")
    s = template("search-state.json.template")
    s["candidates"].append({"candidate_id":"C2","role":"mutation","status":"active","parent_ids":["C_CANONICAL"],"operator":"bounded-mutation","transformation_ids":[]})
    s["candidates"][0]["parent_ids"] = ["C2"]
    assert any(e.startswith("lineage:cycle") for e in state_mod.validate(c, s))
