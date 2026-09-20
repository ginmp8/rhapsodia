import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mod = load("selection", ROOT / "scripts/select_survivors.py")

def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def test_failed_gate_eliminated_and_tradeoffs_survive():
    c = template("search-contract.json.template")
    s = {"candidates": [
        {"candidate_id":"A","role":"canonical","status":"active","hard_gates":{g:"pass" for g in c["hard_gates"]},"metrics":{"quality":0.9,"token_cost":1000},"novelty":0.1},
        {"candidate_id":"B","role":"focused","status":"active","hard_gates":{g:"pass" for g in c["hard_gates"]},"metrics":{"quality":0.95,"token_cost":1200},"novelty":0.8},
        {"candidate_id":"C","role":"novel-bounded","status":"active","hard_gates":{**{g:"pass" for g in c["hard_gates"]},"safety":"fail"},"metrics":{"quality":1.0,"token_cost":800},"novelty":1.0},
    ]}
    r = mod.select(c, s)
    assert r["eliminated_hard_gate"] == ["C"]
    assert set(r["pareto_frontier"]) == {"A", "B"}
