from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import capability_effects, dump_json, request_signature, validate_transform_set


def validate(contract: dict, state: dict, request: dict) -> list[str]:
    errors: list[str] = []
    required = ("request_version", "candidate_id", "operator", "base_parent_id", "donor_parent_ids", "transformation_ids", "expected_capability_effects", "reason")
    for key in required:
        if key not in request:
            errors.append(f"missing:{key}")
    if errors:
        return sorted(set(errors))
    if request.get("request_version") != 2:
        errors.append("request_version:unsupported")
    if request.get("operator") not in contract.get("allowed_operators", []):
        errors.append("operator:not_allowed")
    cid = request.get("candidate_id")
    if not isinstance(cid, str) or not cid:
        errors.append("candidate_id:invalid")
    existing = {c.get("candidate_id") for c in state.get("candidates", []) if isinstance(c, dict)}
    if cid in existing:
        errors.append("candidate_id:already_exists")

    baseline = contract.get("baseline_candidate_id")
    base = request.get("base_parent_id")
    if base != baseline and base not in existing:
        errors.append("base_parent_id:unknown")
    donors = request.get("donor_parent_ids")
    if not isinstance(donors, list) or any(not isinstance(x, str) or not x for x in donors) or len(donors) != len(set(donors)):
        errors.append("donor_parent_ids:invalid")
        donors = []
    for donor in donors:
        if donor not in existing:
            errors.append(f"donor_parent_id:unknown:{donor}")
        if donor == base:
            errors.append(f"donor_parent_id:equals_base:{donor}")

    transforms = request.get("transformation_ids")
    for transform_error in validate_transform_set(transforms, contract):
        errors.append(transform_error)

    if isinstance(transforms, list):
        expected = capability_effects(transforms, contract)
        supplied = request.get("expected_capability_effects")
        if not isinstance(supplied, list) or sorted(supplied) != expected:
            errors.append("expected_capability_effects:mismatch")

    if not isinstance(request.get("reason"), str) or not request["reason"].strip():
        errors.append("reason:invalid")

    if isinstance(base, str) and isinstance(transforms, list):
        sig = request_signature(base, transforms)
        for candidate in state.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            cbase = candidate.get("base_parent_id")
            ct = candidate.get("transformation_ids", [])
            if isinstance(cbase, str) and isinstance(ct, list) and request_signature(cbase, ct) == sig:
                errors.append(f"strategy:duplicate:{candidate.get('candidate_id')}")
                break
        declared_signature = request.get("request_signature")
        if declared_signature is not None and declared_signature != sig:
            errors.append("request_signature:mismatch")

    total_after = len(state.get("candidates", [])) + 1
    if total_after > contract.get("budget", {}).get("max_total_candidates", 0):
        errors.append("budget:max_total_candidates_exceeded")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    errors = validate(contract, state, request)
    result = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "diagnostics": [{"code": e.replace(":", "."), "subject": e.split(":", 1)[0], "evidence": e} for e in errors],
    }
    rendered = dump_json(result)
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
