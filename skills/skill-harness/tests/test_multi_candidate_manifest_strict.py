import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_multi_candidate_manifest_strict.py"
TEMPLATE = ROOT / "assets" / "templates" / "multi-candidate-manifest-strict.json.template"


def load_module():
    assert SCRIPT.is_file(), "strict multi-candidate validator is missing"
    spec = importlib.util.spec_from_file_location("strict_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(cid, identity, n):
    return {
        "candidate_id": cid,
        "candidate_identity": identity,
        "run_id": f"run-{n}",
        "trace_id": f"trace-{n}",
        "trace_manifest_id": f"trace-manifest-{n}",
        "trace_manifest_sha256": f"{n:064x}",
        "work_dir": f"work-{n}",
        "evaluator_id": "evaluator-1",
        "scenario_set_id": "scenarios-1",
        "evaluation_policy_id": "policy-1",
        "holdout_blind": True,
        "candidate_saw_evaluator_only_assets": False,
    }


def test_strict_template_is_valid():
    module = load_module()
    assert TEMPLATE.is_file(), "strict manifest template is missing"
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert module.validate(data) == []


def test_distinct_candidate_ids_cannot_share_candidate_identity():
    module = load_module()
    data = {
        "contract_version": 1,
        "runs": [run("C1", "sha-A", 1), run("C2", "sha-A", 2)],
    }
    assert "candidate_identity:shared_by_distinct_candidates" in module.validate(data)


def test_repeated_runs_of_same_candidate_are_supported():
    module = load_module()
    data = {
        "contract_version": 1,
        "runs": [run("C1", "sha-A", 1), run("C1", "sha-A", 2)],
    }
    assert module.validate(data) == []


def test_repeated_candidate_id_cannot_change_identity():
    module = load_module()
    data = {
        "contract_version": 1,
        "runs": [run("C1", "sha-A", 1), run("C1", "sha-B", 2)],
    }
    assert "candidate_id:identity_mismatch:C1" in module.validate(data)


def test_trace_manifest_identity_is_required():
    module = load_module()
    row = run("C1", "sha-A", 1)
    row.pop("trace_manifest_id")
    row.pop("trace_manifest_sha256")
    errors = module.validate({"contract_version": 1, "runs": [row]})
    assert "run[0].trace_manifest_id:missing" in errors
    assert "run[0].trace_manifest_sha256:missing" in errors


def test_trace_manifest_sha256_must_be_sha256():
    module = load_module()
    row = run("C1", "sha-A", 1)
    row["trace_manifest_sha256"] = "invalid"
    assert "run[0].trace_manifest_sha256:invalid" in module.validate(
        {"contract_version": 1, "runs": [row]}
    )


def test_trace_manifest_ids_and_hashes_are_unique_per_run():
    module = load_module()
    first = run("C1", "sha-A", 1)
    second = run("C2", "sha-B", 2)
    second["trace_manifest_id"] = first["trace_manifest_id"]
    second["trace_manifest_sha256"] = first["trace_manifest_sha256"]
    errors = module.validate({"contract_version": 1, "runs": [first, second]})
    assert "trace_manifest_id:duplicate" in errors
    assert "trace_manifest_sha256:duplicate" in errors


def test_run_trace_and_workdir_are_unique():
    module = load_module()
    first = run("C1", "sha-A", 1)
    second = run("C2", "sha-B", 2)
    second["run_id"] = first["run_id"]
    second["trace_id"] = first["trace_id"]
    second["work_dir"] = first["work_dir"]
    errors = module.validate({"contract_version": 1, "runs": [first, second]})
    assert "run_id:duplicate" in errors
    assert "trace_id:duplicate" in errors
    assert "work_dir:shared" in errors


def test_comparability_inputs_must_match():
    module = load_module()
    first = run("C1", "sha-A", 1)
    second = run("C2", "sha-B", 2)
    second["evaluation_policy_id"] = "policy-2"
    assert "comparability:evaluation_policy_id:mismatch" in module.validate(
        {"contract_version": 1, "runs": [first, second]}
    )
