from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _evidence_common import dump_json, expand_evidence_contract, sha256_data, transformation_signature, validate_evidence_profile_config
from validate_evidence_aware_search_state import validate as validate_state

RECEIPT_VERSION = 1


def _strategy_signatures(state: dict) -> list[str]:
    signatures = set()
    for candidate in state.get("candidates", []):
        if isinstance(candidate, dict) and isinstance(candidate.get("transformation_ids"), list):
            signatures.add(transformation_signature(candidate["transformation_ids"]))
    return sorted(signatures)


def _behavior_signatures(state: dict) -> list[str]:
    signatures: set[str] = set()
    for candidate in state.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        evaluation = candidate.get("evaluation")
        descriptor = evaluation.get("behavior_descriptor") if isinstance(evaluation, dict) else None
        if not isinstance(descriptor, dict):
            continue
        descriptor_id = descriptor.get("descriptor_id")
        labels = descriptor.get("labels")
        if isinstance(descriptor_id, str) and descriptor_id and isinstance(labels, list):
            signatures.add(sha256_data({
                "descriptor_id": descriptor_id,
                "labels": sorted(value for value in labels if isinstance(value, str)),
            }))
    return sorted(signatures)


def _deficit_coverage(state: dict) -> list[str]:
    deficits: set[str] = set()
    for candidate in state.get("candidates", []):
        if isinstance(candidate, dict) and isinstance(candidate.get("deficit_ids"), list):
            deficits.update(value for value in candidate["deficit_ids"] if isinstance(value, str) and value)
    return sorted(deficits)


def _stagnation_policy(contract: dict) -> dict:
    policy = contract.get("stagnation_policy")
    if isinstance(policy, dict):
        return policy
    return {"id": "transformation-signature-v1"}


def build_receipt(contract: dict, state: dict, previous_receipt: dict | None = None) -> tuple[dict, list[str]]:
    source_contract = contract
    errors: list[str] = list(validate_evidence_profile_config(source_contract))
    errors.extend(validate_state(source_contract, state))
    contract = expand_evidence_contract(source_contract)
    if contract.get("search_id") != state.get("search_id"):
        errors.append("search_id:mismatch")
    previous_hash = sha256_data(previous_receipt) if previous_receipt is not None else None
    signatures = _strategy_signatures(state)
    behavior_signatures = _behavior_signatures(state)
    deficit_coverage = _deficit_coverage(state)
    stagnation_policy = _stagnation_policy(contract)
    stagnation_policy_id = stagnation_policy.get("id")
    pareto = sorted(state.get("pareto_archive", []))
    stagnant_round = False
    semantic_stagnation = False
    if previous_receipt is None:
        if state.get("stagnant_rounds") != 0:
            errors.append("stagnant_rounds:first_checkpoint_must_be_zero")
    else:
        previous_signatures = set(previous_receipt.get("strategy_signatures", []))
        new_signatures = set(signatures) - previous_signatures
        pareto_changed = pareto != sorted(previous_receipt.get("pareto_archive", []))
        if stagnation_policy_id == "pareto-plus-semantic-signatures-v1":
            semantic_progress = False
            if stagnation_policy.get("include_behavior_descriptors") is True:
                previous_behavior = set(previous_receipt.get("behavior_signatures", []))
                semantic_progress = semantic_progress or bool(set(behavior_signatures) - previous_behavior)
            if stagnation_policy.get("include_deficit_coverage") is True:
                previous_deficits = set(previous_receipt.get("deficit_coverage", []))
                semantic_progress = semantic_progress or bool(set(deficit_coverage) - previous_deficits)
            stagnant_round = (not pareto_changed) and (not semantic_progress)
            semantic_stagnation = stagnant_round
        else:
            stagnant_round = (not pareto_changed) and (not new_signatures)
        expected = int(previous_receipt.get("stagnant_rounds", 0)) + 1 if stagnant_round else 0
        if state.get("stagnant_rounds") != expected:
            errors.append(f"stagnant_rounds:expected:{expected}")
        previous_round = previous_receipt.get("round")
        if isinstance(previous_round, int) and state.get("round") != previous_round + 1:
            errors.append(f"round:expected:{previous_round + 1}")
        if previous_receipt.get("search_id") != state.get("search_id"):
            errors.append("previous_receipt:search_id_mismatch")

    receipt = {
        "receipt_version": RECEIPT_VERSION,
        "search_id": state.get("search_id"),
        "round": state.get("round"),
        "contract_sha256": sha256_data(source_contract),
        "state_sha256": sha256_data(state),
        "previous_receipt_sha256": previous_hash,
        "candidate_count": len(state.get("candidates", [])),
        "pareto_archive": pareto,
        "strategy_signatures": signatures,
        "behavior_signatures": behavior_signatures,
        "deficit_coverage": deficit_coverage,
        "stagnation_policy_id": stagnation_policy_id,
        "stagnant_round": stagnant_round,
        "semantic_stagnation": semantic_stagnation,
        "stagnant_rounds": state.get("stagnant_rounds"),
        "search_status": state.get("status"),
    }
    return receipt, sorted(set(errors))


def verify_receipt(contract: dict, state: dict, receipt: dict, previous_receipt: dict | None = None) -> list[str]:
    expected, errors = build_receipt(contract, state, previous_receipt)
    for key, value in expected.items():
        if receipt.get(key) != value:
            errors.append(f"receipt:{key}:mismatch")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--contract", required=True)
    create.add_argument("--state", required=True)
    create.add_argument("--out", required=True)
    create.add_argument("--previous-receipt")

    verify = sub.add_parser("verify")
    verify.add_argument("--contract", required=True)
    verify.add_argument("--state", required=True)
    verify.add_argument("--receipt", required=True)
    verify.add_argument("--previous-receipt")
    verify.add_argument("--json-output")

    args = parser.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    previous = json.loads(Path(args.previous_receipt).read_text(encoding="utf-8")) if args.previous_receipt else None

    if args.command == "create":
        receipt, errors = build_receipt(contract, state, previous)
        result = {"status": "pass" if not errors else "fail", "errors": errors, "receipt": receipt}
        if not errors:
            Path(args.out).write_text(dump_json(receipt), encoding="utf-8")
        print(dump_json(result), end="")
        return 0 if not errors else 2

    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    errors = verify_receipt(contract, state, receipt, previous)
    result = {"status": "pass" if not errors else "fail", "errors": errors}
    rendered = dump_json(result)
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
