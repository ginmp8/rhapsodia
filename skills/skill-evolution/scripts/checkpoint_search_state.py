from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import dump_json, sha256_data, transformation_signature

RECEIPT_VERSION = 1


def _strategy_signatures(state: dict) -> list[str]:
    signatures = set()
    for candidate in state.get("candidates", []):
        if isinstance(candidate, dict) and isinstance(candidate.get("transformation_ids"), list):
            signatures.add(transformation_signature(candidate["transformation_ids"]))
    return sorted(signatures)


def build_receipt(contract: dict, state: dict, previous_receipt: dict | None = None) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if contract.get("search_id") != state.get("search_id"):
        errors.append("search_id:mismatch")
    previous_hash = sha256_data(previous_receipt) if previous_receipt is not None else None
    signatures = _strategy_signatures(state)
    pareto = sorted(state.get("pareto_archive", []))
    stagnant_round = False
    if previous_receipt is None:
        if state.get("stagnant_rounds") != 0:
            errors.append("stagnant_rounds:first_checkpoint_must_be_zero")
    else:
        previous_signatures = set(previous_receipt.get("strategy_signatures", []))
        new_signatures = set(signatures) - previous_signatures
        pareto_changed = pareto != sorted(previous_receipt.get("pareto_archive", []))
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
        "contract_sha256": sha256_data(contract),
        "state_sha256": sha256_data(state),
        "previous_receipt_sha256": previous_hash,
        "candidate_count": len(state.get("candidates", [])),
        "pareto_archive": pareto,
        "strategy_signatures": signatures,
        "stagnant_round": stagnant_round,
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
