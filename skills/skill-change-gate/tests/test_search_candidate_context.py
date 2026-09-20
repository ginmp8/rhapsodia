from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

# Importing the validator during tests must not create generated package artifacts.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_search_candidate_context.py"
TEMPLATE = ROOT / "assets" / "templates" / "search-candidate-context.json.template"

spec = importlib.util.spec_from_file_location("search_candidate_context_validator", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def data() -> dict:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def test_template_valid() -> None:
    assert module.validate(data()) == []


def test_missing_policy() -> None:
    candidate = data()
    candidate["evaluation_identity"].pop("policy_id")
    assert "evaluation_identity.policy_id:invalid" in module.validate(candidate)


def test_v1_rejected() -> None:
    candidate = data()
    candidate["context_version"] = 1
    assert "context_version:unsupported" in module.validate(candidate)


def test_v3_is_current_contract() -> None:
    assert data()["context_version"] == 3


def test_rejects_candidate_as_base_parent() -> None:
    candidate = data()
    candidate["candidate_id"] = candidate["base_parent_id"]
    assert "candidate:self_parent" in module.validate(candidate)


def test_rejects_candidate_as_donor_parent() -> None:
    candidate = data()
    candidate["donor_parent_ids"] = [candidate["candidate_id"]]
    assert "candidate:self_parent" in module.validate(candidate)


def test_rejects_base_parent_as_donor_parent() -> None:
    candidate = data()
    candidate["donor_parent_ids"] = [candidate["base_parent_id"]]
    assert "donor_parent_ids:contains_base" in module.validate(candidate)


def test_rejects_tampered_request_signature() -> None:
    candidate = data()
    candidate["request_signature"] = "tampered-but-nonempty"
    assert "request_signature:mismatch" in module.validate(candidate)


if __name__ == "__main__":
    tests = [
        test_template_valid,
        test_missing_policy,
        test_v1_rejected,
        test_v3_is_current_contract,
        test_rejects_candidate_as_base_parent,
        test_rejects_candidate_as_donor_parent,
        test_rejects_base_parent_as_donor_parent,
        test_rejects_tampered_request_signature,
    ]
    for test in tests:
        test()
    print(f"ok: {len(tests)} tests")
