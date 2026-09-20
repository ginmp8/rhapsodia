import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_v3_reg", ROOT / "scripts" / "build_evolution_contract.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def write_inputs(tmp_path, evaluation_plan):
    target = "sha256:test"
    cap = {"schema_version": 1, "target": {"name": "x", "identity": target, "class": "orchestration-meta"}, "capabilities": []}
    tr = {"schema_version": 1, "target_identity": target, "transformations": []}
    hyp = {"schema_version": "2.0", "target": {"name": "x", "identity": target}, "items": []}
    for name, data in [("cap.json", cap), ("tr.json", tr), ("ev.json", evaluation_plan), ("hyp.json", hyp)]:
        (tmp_path / name).write_text(json.dumps(data))
    handoff = json.loads((ROOT / "assets" / "templates" / "evolution-handoff.json.template").read_text())
    handoff["target_identity"] = target
    handoff["artifact_refs"] = {"capability_map": "cap.json", "hypothesis_pool": "hyp.json", "transformation_registry": "tr.json", "evaluation_plan": "ev.json"}
    return handoff


def test_handoff_template_is_v3_and_freezes_selection_eligibility():
    handoff = json.loads((ROOT / "assets" / "templates" / "evolution-handoff.json.template").read_text())
    assert handoff["handoff_version"] == 3
    assert handoff["contract_version"] == 3
    assert handoff["selection_policy"]["eligible_evidence_types"] == ["measured", "supplied"]
    assert handoff["selection_policy"]["comparison_level_policy"] == "same-level"
    assert handoff["selection_policy"]["holdout_failure_policy"] == "eliminate-blind-fail"


def test_evaluation_plan_identity_changes_compiled_contract(tmp_path):
    target = "sha256:test"
    ev_a = {"schema_version": 1, "target_identity": target, "levels": [], "promotion": {}, "checks": ["a"]}
    handoff = write_inputs(tmp_path, ev_a)
    first = mod.build(handoff, tmp_path)
    assert first["contract_version"] == 3
    assert "evaluation_plan_id" in first["input_identities"]
    ev_b = copy.deepcopy(ev_a)
    ev_b["checks"] = ["different"]
    (tmp_path / "ev.json").write_text(json.dumps(ev_b))
    second = mod.build(handoff, tmp_path)
    assert first["input_identities"]["evaluation_plan_id"] != second["input_identities"]["evaluation_plan_id"]
