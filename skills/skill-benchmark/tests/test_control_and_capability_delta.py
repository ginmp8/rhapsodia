from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARE = ROOT / "scripts" / "compare_benchmark_arms.py"
SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def envelope(arm: str, activation: bool, *, target: str | None = SHA_C, host: str = "host-1", self_meta: dict | None = None) -> dict:
    data = {
        "schema_version": 2,
        "evidence_origin": "executed",
        "arm_type": arm,
        "evaluator_identity_sha256": SHA_A,
        "scenario_suite_sha256": SHA_B,
        "host_profile": host,
        "evaluator_visibility": "hidden",
        "candidate_saw_evaluator_only_assets": False,
        "scenarios": [
            {
                "id": "A1",
                "category": "should_activate",
                "prompt": "do the task",
                "expected_activation": True,
                "actual_activation": activation,
                "output_conforms": activation,
                "quality_score": 5 if activation else 0,
                "needs_rework": not activation,
            },
            {
                "id": "E1",
                "category": "edge_case",
                "prompt": "bad input",
                "expected_activation": True,
                "actual_activation": activation,
                "output_conforms": activation,
                "quality_score": 5 if activation else 0,
                "needs_rework": not activation,
            },
        ],
    }
    if target:
        data["target_identity_sha256"] = target
    if self_meta is not None:
        data["self_improvement"] = self_meta
    return data


def run(*args: str):
    return subprocess.run([sys.executable, str(COMPARE), *args], capture_output=True, text=True)


def test_candidate_improves_over_baseline_and_control():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        paths = {}
        for arm, payload in {
            "candidate": envelope("candidate", True, target=SHA_C),
            "baseline": envelope("baseline", False, target="d" * 64),
            "control": envelope("without-skill", False, target=None),
        }.items():
            path = base / f"{arm}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            paths[arm] = path
        result = run("--candidate", str(paths["candidate"]), "--baseline", str(paths["baseline"]), "--without-skill", str(paths["control"]))
        assert result.returncode == 0, result.stderr or result.stdout
        report = json.loads(result.stdout)
        assert report["baseline_comparison"]["capability_delta"]["activation_recall"]["classification"] == "improved"
        assert report["without_skill_comparison"]["capability_delta"]["output_conformance"]["classification"] == "improved"


def test_host_mismatch_is_not_comparable():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        cand = base / "candidate.json"
        ctrl = base / "control.json"
        cand.write_text(json.dumps(envelope("candidate", True, host="host-1")), encoding="utf-8")
        ctrl.write_text(json.dumps(envelope("without-skill", False, target=None, host="host-2")), encoding="utf-8")
        result = run("--candidate", str(cand), "--without-skill", str(ctrl))
        assert result.returncode == 0
        report = json.loads(result.stdout)
        assert report["without_skill_comparison"]["comparable"] is False
        assert "host_profile" in report["without_skill_comparison"]["non_comparable_reasons"]


def test_hidden_evaluator_leak_rejected():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        cand_payload = envelope("candidate", True)
        cand_payload["candidate_saw_evaluator_only_assets"] = True
        cand = base / "candidate.json"
        ctrl = base / "control.json"
        cand.write_text(json.dumps(cand_payload), encoding="utf-8")
        ctrl.write_text(json.dumps(envelope("without-skill", False, target=None)), encoding="utf-8")
        result = run("--candidate", str(cand), "--without-skill", str(ctrl))
        assert result.returncode != 0


def self_meta(controller: str = "e" * 64, generation: str = "gen-1") -> dict:
    return {
        "generation_id": generation,
        "controller_identity_sha256": controller,
        "baseline_identity_sha256": "d" * 64,
        "candidate_identity_sha256": SHA_C,
    }


def test_self_improvement_same_generation_is_comparable():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        cand = base / "candidate.json"
        baseline = base / "baseline.json"
        meta = self_meta()
        cand.write_text(json.dumps(envelope("candidate", True, target=SHA_C, self_meta=meta)), encoding="utf-8")
        baseline.write_text(json.dumps(envelope("baseline", False, target="d" * 64, self_meta=meta)), encoding="utf-8")
        result = run("--candidate", str(cand), "--baseline", str(baseline))
        assert result.returncode == 0, result.stdout + result.stderr
        report = json.loads(result.stdout)
        assert report["baseline_comparison"]["comparable"] is True


def test_self_improvement_controller_mismatch_is_not_comparable():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        cand = base / "candidate.json"
        baseline = base / "baseline.json"
        cand.write_text(json.dumps(envelope("candidate", True, target=SHA_C, self_meta=self_meta(controller="e" * 64))), encoding="utf-8")
        baseline.write_text(json.dumps(envelope("baseline", False, target="d" * 64, self_meta=self_meta(controller="f" * 64))), encoding="utf-8")
        result = run("--candidate", str(cand), "--baseline", str(baseline))
        assert result.returncode == 0
        report = json.loads(result.stdout)
        assert report["baseline_comparison"]["comparable"] is False
        assert "self_improvement.controller_identity_sha256" in report["baseline_comparison"]["non_comparable_reasons"]
