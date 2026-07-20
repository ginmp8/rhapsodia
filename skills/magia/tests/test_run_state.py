from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.validate_run_state import validate_state


def state_for(path: Path) -> dict:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema_version": 1,
        "run_id": "run-test",
        "profile": "standard",
        "mode": "adhoc",
        "status": "in_progress",
        "checkpoint": "execute",
        "pending_step": "validate",
        "scope": {"repo_root": ".", "task": None, "spec_id": None},
        "inspected_files": [{"path": path.name, "sha256": digest}],
        "dependency_fingerprint": None,
        "planned_writes": ["result.txt"],
        "completed_writes": [],
        "commands": [{"command": "python -m pytest", "status": "not_run"}],
        "validation_status": "not_run",
        "convergence_status": "unverified",
        "retry": {"count": 0, "max": 1, "last_reason": None},
        "cancellation": {"requested": False, "reason": None},
        "rollback_evidence": [],
        "handoff": {"target": "none", "reason": None},
        "atomicity": "single_repository",
        "repositories": [{
            "id": "primary", "path": ".", "dependency_order": 0, "status": "in_progress",
            "checkpoint": "execute", "compatibility_window": None, "rollback_status": "not_required"
        }],
    }


def test_valid_state_and_drift_verification(tmp_path: Path):
    source = tmp_path / "source.txt"
    source.write_text("stable", encoding="utf-8")
    data = state_for(source)
    assert validate_state(data, tmp_path, True) == []
    source.write_text("changed", encoding="utf-8")
    assert any("repository_drift" in error for error in validate_state(data, tmp_path, True))


def test_completed_state_requires_current_evidence(tmp_path: Path):
    source = tmp_path / "source.txt"
    source.write_text("stable", encoding="utf-8")
    data = state_for(source)
    data.update({"status": "completed", "checkpoint": "close", "pending_step": None})
    errors = validate_state(data)
    assert "completed run requires validation_status pass" in errors
    assert "completed run requires convergence_status satisfied" in errors
    data["validation_status"] = "pass"
    data["convergence_status"] = "satisfied"
    data["repositories"][0]["status"] = "completed"
    assert validate_state(data) == []


def test_multi_repository_never_implies_atomicity(tmp_path: Path):
    source = tmp_path / "source.txt"
    source.write_text("stable", encoding="utf-8")
    data = state_for(source)
    data["repositories"].append({
        "id": "consumer", "path": "../consumer", "dependency_order": 1, "status": "pending",
        "checkpoint": "inspect", "compatibility_window": "v1-v2", "rollback_status": "planned"
    })
    assert "multi-repository runs must set atomicity to not_guaranteed" in validate_state(data)
    data["atomicity"] = "not_guaranteed"
    assert validate_state(data) == []


def test_template_is_valid_json():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "assets/templates/run-state.json.template").read_text(encoding="utf-8"))
    assert validate_state(data) == []
