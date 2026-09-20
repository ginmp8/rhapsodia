import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("benchmark_v4_reg", ROOT / "scripts" / "validate_candidate_set.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def row(cid):
    return {"candidate_id": cid, "candidate_identity": cid + "hash", "parent_id": "B", "baseline_id": "Bhash", "evaluator_id": "E", "scenario_set_id": "S", "policy_id": "P", "evaluation_level": "L4-benchmark", "metrics": {"q": {"value": 1, "uncertainty": 0.1}}}


def test_template_uses_v4():
    data = json.loads((ROOT / "assets" / "templates" / "multi-candidate-evidence.json.template").read_text())
    assert data["contract_version"] == 4


def test_v4_rejects_distinct_ids_with_same_candidate_identity():
    a, b = row("C1"), row("C2")
    b["candidate_identity"] = a["candidate_identity"]
    assert "candidate_identity:duplicate" in mod.validate({"contract_version": 4, "candidates": [a, b]})


def test_v3_keeps_legacy_identity_semantics():
    a, b = row("C1"), row("C2")
    b["candidate_identity"] = a["candidate_identity"]
    assert "candidate_identity:duplicate" not in mod.validate({"contract_version": 3, "candidates": [a, b]})
