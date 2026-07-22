from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from board_contract import validate_priority_semantics


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def canonical():
    return {
        "business_priority": {"level": "urgent", "owner": "nomia", "source": "nomia/ops", "observed_at": "2026-07-21T10:00:00Z"},
        "technical_criticality": {"level": "high", "owner": "mago", "rationale": "cross-service contract"},
        "execution_sequence": {"rank": 20, "lane": "fixed_date", "owner": "mago", "rationale": ["regulatory deadline after prerequisite"]},
    }


def test_canonical_priority_contract_is_accepted():
    assert validate_priority_semantics(canonical(), "registry.yaml") == []


def test_generic_priority_field_is_rejected():
    payload = canonical()
    payload["priority"] = "high"
    assert any("unsupported generic field" in error for error in validate_priority_semantics(payload, "registry.yaml"))


def test_non_unknown_business_priority_requires_provenance():
    payload = canonical()
    payload["business_priority"]["source"] = None
    assert any("requires source" in error for error in validate_priority_semantics(payload, "registry.yaml"))


def test_generic_priority_only_contract_is_rejected():
    errors = validate_priority_semantics({"priority": "normal", "order_hint": None}, "registry.yaml")
    assert any("unsupported generic field" in error for error in errors)


def test_local_priority_contract_validator_passes():
    module = load_script("validate_priority_contract.py")
    assert module.collect_errors(ROOT) == []
