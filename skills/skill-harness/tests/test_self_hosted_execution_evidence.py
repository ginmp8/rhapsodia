from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_execution_evidence.py"
A, B, C, D, E, F = (x * 64 for x in "abcdef")


def payload(arm="candidate", target=F):
    return {
        "schema_version": 2,
        "run_id": "run-1",
        "arm": arm,
        "evidence_status": "executed",
        "target_identity_sha256": target,
        "evaluator_identity_sha256": A,
        "scenario_suite_sha256": B,
        "host_profile": "portable-test",
        "isolation_level": "workspace",
        "self_hosting": {
            "generation_id": "gen-1",
            "controller_identity_sha256": C,
            "baseline_identity_sha256": D,
            "candidate_identity_sha256": F,
            "controller_candidate_separated": True,
            "controller_read_only": True,
        },
        "candidate_visible_manifest_sha256": E,
        "evaluator_only_manifest_sha256": None,
        "trace": {"status": "not-required", "reference": None, "sha256": None},
        "leakage_check": {"status": "pass", "candidate_saw_evaluator_only_assets": False, "notes": ""},
        "scenarios": [{"id": "x"}],
    }


def run(data):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"evidence.json"
        p.write_text(json.dumps(data),encoding="utf-8")
        return subprocess.run([sys.executable,str(SCRIPT),str(p)],capture_output=True,text=True)


def test_self_hosted_candidate_passes():
    r=run(payload())
    assert r.returncode==0, r.stdout+r.stderr
    report=json.loads(r.stdout)
    assert report["checks"]["self_hosting_present"] is True
    assert report["checks"]["measured_claim_eligible"] is True


def test_same_controller_candidate_fails():
    d=payload()
    d["self_hosting"]["controller_identity_sha256"]=F
    d["self_hosting"]["controller_candidate_separated"]=False
    r=run(d)
    assert r.returncode!=0
    assert "must not share" in r.stdout


def test_candidate_identity_must_match_target():
    d=payload(target="1"*64)
    r=run(d)
    assert r.returncode!=0
    assert "must equal self_hosting.candidate_identity_sha256" in r.stdout


def test_mutable_controller_fails_measured_evidence():
    d=payload()
    d["self_hosting"]["controller_read_only"]=False
    r=run(d)
    assert r.returncode!=0
    assert "controller_read_only must be true" in r.stdout
