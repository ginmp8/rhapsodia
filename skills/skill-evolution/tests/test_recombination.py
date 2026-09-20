import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mod = load("recomb", ROOT / "scripts/plan_recombination.py")

def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def test_recombination_returns_merge_or_backcross():
    c = template("search-contract.json.template")
    s = {"candidates": [
        {"candidate_id":"C_CANONICAL","role":"canonical","transformation_ids":["T1"]},
        {"candidate_id":"C2","role":"focused","transformation_ids":["T2"]},
    ]}
    r = mod.plan(c, s, ["C_CANONICAL", "C2"])
    assert r["proposals"]
    assert r["proposals"][0]["operator"] == "transformation-merge"
    assert r["proposals"][0]["request_version"] == 1
    assert r["proposals"][0]["candidate_id"].startswith("C")
    assert any(p["operator"] == "backcross" for p in r["proposals"])
