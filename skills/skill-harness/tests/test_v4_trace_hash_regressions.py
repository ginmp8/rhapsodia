import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

base = load("validate_multi_candidate_manifest.py")
strict = load("validate_multi_candidate_manifest_strict.py")


def row(cid, n):
    return {"candidate_id": cid, "candidate_identity": cid + "hash", "run_id": f"R{n}", "trace_id": f"T{n}", "trace_manifest_id": f"TM{n}", "trace_manifest_sha256": f"sha256:{n:064x}", "work_dir": f"/tmp/w{n}", "evaluator_id": "E", "scenario_set_id": "S", "evaluation_policy_id": "P", "holdout_blind": True, "candidate_saw_evaluator_only_assets": False}


def test_base_template_uses_v4():
    data = json.loads((ROOT / "assets" / "templates" / "multi-candidate-manifest.json.template").read_text())
    assert data["contract_version"] == 4


def test_v4_rejects_invalid_trace_manifest_hash_shape():
    r = row("C1", 1)
    r["trace_manifest_sha256"] = "not-a-hash"
    assert "run[0].trace_manifest_sha256:invalid" in base.validate({"contract_version": 4, "runs": [r]})


def test_v3_keeps_legacy_hash_shape_semantics():
    r = row("C1", 1)
    r["trace_manifest_sha256"] = "not-a-hash"
    assert "run[0].trace_manifest_sha256:invalid" not in base.validate({"contract_version": 3, "runs": [r]})


def test_strict_template_uses_v2_and_prefixed_sha256():
    data = json.loads((ROOT / "assets" / "templates" / "multi-candidate-manifest-strict.json.template").read_text())
    assert data["contract_version"] == 2
    assert data["runs"][0]["trace_manifest_sha256"].startswith("sha256:")


def test_strict_v2_rejects_unprefixed_hash():
    r = row("C1", 1)
    r["trace_manifest_sha256"] = "a" * 64
    assert "run[0].trace_manifest_sha256:invalid" in strict.validate({"contract_version": 2, "runs": [r]})
