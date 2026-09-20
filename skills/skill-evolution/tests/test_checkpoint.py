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


mod = load("checkpoint_v2", SCRIPTS / "checkpoint_search_state.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def test_first_checkpoint_requires_zero_stagnation():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    receipt, errors = mod.build_receipt(contract, state)
    assert errors == []
    assert receipt["stagnant_rounds"] == 0
    state["stagnant_rounds"] = 1
    _, errors = mod.build_receipt(contract, state)
    assert "stagnant_rounds:first_checkpoint_must_be_zero" in errors


def test_unchanged_round_increments_stagnation_deterministically():
    contract = template("search-contract.json.template")
    state0 = template("search-state.json.template")
    receipt0, errors = mod.build_receipt(contract, state0)
    assert errors == []
    state1 = copy.deepcopy(state0)
    state1["round"] = 1
    state1["stagnant_rounds"] = 1
    receipt1, errors = mod.build_receipt(contract, state1, receipt0)
    assert errors == []
    assert receipt1["stagnant_round"] is True


def test_new_transformation_signature_resets_stagnation():
    contract = template("search-contract.json.template")
    state0 = template("search-state.json.template")
    receipt0, _ = mod.build_receipt(contract, state0)
    state1 = copy.deepcopy(state0)
    state1["round"] = 1
    state1["stagnant_rounds"] = 0
    extra = copy.deepcopy(state1["candidates"][0])
    extra["candidate_id"] = "C002"
    extra["candidate_identity"] = "candidate-C002-bytes"
    extra["transformation_ids"] = ["T002"]
    extra["expected_capability_effects"] = ["activation"]
    extra["generation_receipt"]["receipt_identity"] = "receipt-C002"
    extra["generation_receipt"]["candidate_identity"] = "candidate-C002-bytes"
    extra["generation_receipt"]["transformation_ids"] = ["T002"]
    state1["candidates"].append(extra)
    receipt1, errors = mod.build_receipt(contract, state1, receipt0)
    assert errors == []
    assert receipt1["stagnant_round"] is False
    assert receipt1["stagnant_rounds"] == 0


def test_verify_detects_state_tampering():
    contract = template("search-contract.json.template")
    state = template("search-state.json.template")
    receipt, errors = mod.build_receipt(contract, state)
    assert errors == []
    tampered = copy.deepcopy(state)
    tampered["candidates"][0]["candidate_identity"] = "tampered-bytes"
    errors = mod.verify_receipt(contract, tampered, receipt)
    assert "receipt:state_sha256:mismatch" in errors
