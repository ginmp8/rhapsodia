from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_gate_context.py"
TEMPLATE = ROOT / "assets" / "templates" / "gate-context.json.template"
STATIC = ROOT / "scripts" / "static_change_gate.py"

spec = importlib.util.spec_from_file_location("gate_context_validator", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ZERO = "0" * 64
ONE = "1" * 64
TWO = "2" * 64


def data() -> dict:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def strict_data() -> dict:
    d = data()
    d["policy"] = {"policy_id": "skill-change-gate.strict", "policy_version": "1", "policy_digest": ONE}
    d["verifier"] = {"verifier_id": "skill-change-gate", "version": "1", "implementation_digest": TWO}
    return d


def codes(result: dict) -> set[str]:
    return {x["code"] for x in result["errors"]}


def write_skill(root: Path, description: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(f"---\nname: {root.name}\ndescription: {description}\n---\n\n# Demo\n", encoding="utf-8")


def static(*args: str) -> dict:
    p = subprocess.run([sys.executable, str(STATIC), *args], capture_output=True, text=True)
    assert p.stdout.strip(), p.stderr
    return json.loads(p.stdout)


def test_template_passes_normal_policy() -> None:
    r = module.validate(data(), policy="normal", expected_candidate_sha256=ZERO)
    assert r["status"] == "pass"


def test_strict_requires_policy_and_verifier_digests() -> None:
    r = module.validate(data(), policy="strict", expected_candidate_sha256=ZERO)
    assert {"policy/digest-required", "verifier/digest-required"} <= codes(r)


def test_strict_context_with_digests_passes() -> None:
    r = module.validate(strict_data(), policy="strict", expected_candidate_sha256=ZERO)
    assert r["status"] == "pass"


def test_evidence_subject_mismatch_is_blocking() -> None:
    d = strict_data()
    d["evidence"] = [{
        "evidence_id": "validation-1",
        "evidence_type": "validator",
        "required": True,
        "status": "pass",
        "subject_candidate_tree_sha256": ONE,
        "producer_id": "validator",
        "producer_version": "1",
        "policy_digest": ONE,
        "notes": ""
    }]
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert "evidence/subject-mismatch" in codes(r)


def test_required_evidence_not_pass_is_blocking() -> None:
    d = strict_data()
    d["evidence"] = [{
        "evidence_id": "validation-1",
        "evidence_type": "validator",
        "required": True,
        "status": "not-run",
        "subject_candidate_tree_sha256": ZERO,
        "producer_id": "validator",
        "producer_version": "1",
        "policy_digest": ONE,
        "notes": ""
    }]
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert "evidence/required-not-pass" in codes(r)


def test_declared_holdout_cannot_be_contaminated() -> None:
    d = strict_data()
    d["evaluator"].update({"role": "holdout", "candidate_had_access": False, "selection_informed_by_results": True, "exposure_generation_count": 1})
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert "evaluator/holdout-contaminated" in codes(r)


def test_evaluation_contract_enforces_trials_and_replication() -> None:
    d = strict_data()
    d["evaluation_contract"].update({
        "required_trials": 5,
        "completed_trials": 3,
        "independent_replication_required": True,
        "independent_replication_completed": False,
    })
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert {"evaluation/trials-insufficient", "evaluation/replication-missing"} <= codes(r)


def test_destination_identity_mismatch_is_stale() -> None:
    d = strict_data()
    d["destination"] = {"required": True, "expected_identity": "main@abc", "observed_identity": "main@def"}
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert "freshness/destination-stale" in codes(r)


def test_authority_expansion_warns_normal_and_fails_strict() -> None:
    d = data()
    d["authority"] = {"expanded": True, "authorized": False, "added_surfaces": ["shell"]}
    normal = module.validate(d, policy="normal", expected_candidate_sha256=ZERO)
    assert normal["status"] == "pass-with-warnings"
    s = strict_data()
    s["authority"] = deepcopy(d["authority"])
    strict = module.validate(s, policy="strict", expected_candidate_sha256=ZERO)
    assert "authority/expansion-unapproved" in codes(strict)


def test_non_waivable_finding_cannot_be_waived() -> None:
    d = strict_data()
    d["waivers"] = [{
        "waiver_id": "W-1",
        "candidate_tree_sha256": ZERO,
        "policy_digest": ONE,
        "finding_codes": ["delivery/receipt-candidate-mismatch"],
        "authorized_by": "risk-owner",
        "reason": "temporary",
        "expires_at": None,
        "single_use": True,
    }]
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert "waiver/non-waivable" in codes(r)


def test_ecosystem_safe_requires_complete_compatible_consumer_evidence() -> None:
    d = strict_data()
    d["claim_scope"] = "ecosystem-safe"
    d["known_consumers"] = [{"consumer_id": "peer", "contract_id": "x", "status": "unverified", "evidence_ref": ""}]
    r = module.validate(d, policy="strict", expected_candidate_sha256=ZERO)
    assert {"consumer/inventory-incomplete", "consumer/not-compatible"} <= codes(r)


def test_description_shortening_is_signal_not_strict_failure() -> None:
    with tempfile.TemporaryDirectory() as td:
        before = Path(td) / "before" / "demo-skill"
        after = Path(td) / "after" / "demo-skill"
        long_desc = "review existing Agent Skill candidate changes before acceptance with explicit evidence identity protected evaluator safety portability validation packaging recovery output contracts activation boundaries and compatibility across supported hosts"
        short_desc = "review Agent Skill candidate changes before acceptance with explicit evidence and portability checks"
        write_skill(before, long_desc)
        write_skill(after, short_desc)
        r = static("--target", str(after), "--before", str(before), "--policy", "strict")
        hits = [f for f in r["findings"] if f["code"] == "activation/description-sharply-shortened"]
        assert hits and hits[0]["severity"] == "non-blocking"
        assert r["status"] == "pass"


def test_static_helper_binds_gate_context_to_actual_candidate() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        write_skill(skill, "review existing Agent Skill candidate changes before acceptance using explicit evidence identity validation portability safety packaging recovery and activation boundaries across compatible hosts")
        first = static("--target", str(skill))
        d = data()
        d["candidate_tree_sha256"] = first["target_tree_sha256"]
        context = Path(td) / "gate-context.json"
        context.write_text(json.dumps(d), encoding="utf-8")
        r = static("--target", str(skill), "--gate-context", str(context))
        assert r["status"] == "pass"
        assert r["gate_context"]["status"] == "pass"
