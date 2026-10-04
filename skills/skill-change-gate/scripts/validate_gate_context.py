#!/usr/bin/env python3
"""Validate Skill Change Gate Context v1 using Python standard library only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
POLICIES = {"normal", "strict", "advisory"}
CLAIMS = {"local-acceptance", "promotion", "ecosystem-safe"}
ROLES = {"development", "selection", "holdout"}
EVIDENCE_STATUS = {"pass", "fail", "blocked", "not-run"}
CONSUMER_STATUS = {"compatible", "incompatible", "unverified"}
NON_WAIVABLE_PREFIXES = (
    "evidence/before-identity-mismatch",
    "evidence/target-identity-mismatch",
    "evidence/protected-path-changed",
    "delivery/receipt-candidate-mismatch",
    "delivery/receipt-inside-target",
    "safety/sensitive-path",
    "references/path-escape",
    "evaluator/frozen-evidence-changed",
    "evaluator/holdout-contaminated",
    "self-improvement/self-authorization",
)


def _s(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash(value: object) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value.strip().lower()))


def _add(items: list[dict[str, object]], code: str, message: str, **evidence: object) -> None:
    items.append({"code": code, "message": message, "evidence": evidence})


def validate(data: object, *, policy: str = "normal", expected_candidate_sha256: str | None = None) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    if policy not in POLICIES:
        _add(errors, "policy/invalid", "policy must be normal, strict, or advisory", policy=policy)
        policy = "normal"
    if not isinstance(data, dict):
        _add(errors, "context/not-object", "gate context must be a JSON object")
        return _result(errors, warnings)

    if data.get("context_version") != 1:
        _add(errors, "context/version", "context_version must be 1", observed=data.get("context_version"))
    claim = data.get("claim_scope")
    if claim not in CLAIMS:
        _add(errors, "claim/invalid", "claim_scope is invalid", observed=claim)

    candidate = data.get("candidate_tree_sha256")
    if not _hash(candidate):
        _add(errors, "candidate/hash-invalid", "candidate_tree_sha256 must be a lowercase SHA-256 hex digest")
        candidate_norm = None
    else:
        candidate_norm = str(candidate).lower()
    if expected_candidate_sha256 is not None:
        expected = expected_candidate_sha256.strip().lower()
        if not _hash(expected):
            _add(errors, "candidate/expected-hash-invalid", "--expected-candidate-sha256 is invalid")
        elif candidate_norm is not None and candidate_norm != expected:
            _add(errors, "candidate/hash-mismatch", "gate context candidate does not match the frozen candidate", expected=expected, observed=candidate_norm)

    policy_obj = data.get("policy")
    policy_digest = None
    if not isinstance(policy_obj, dict):
        _add(errors, "policy/missing", "policy object is required")
    else:
        for key in ("policy_id", "policy_version"):
            if not _s(policy_obj.get(key)):
                _add(errors, f"policy/{key}-invalid", f"{key} must be non-empty")
        raw = policy_obj.get("policy_digest")
        if raw is not None and not _hash(raw):
            _add(errors, "policy/digest-invalid", "policy_digest must be null or SHA-256")
        elif _hash(raw):
            policy_digest = str(raw).lower()
        if policy == "strict" and policy_digest is None:
            _add(errors, "policy/digest-required", "strict measured acceptance requires exact policy identity")

    verifier = data.get("verifier")
    if not isinstance(verifier, dict):
        _add(errors, "verifier/missing", "verifier object is required")
    else:
        for key in ("verifier_id", "version"):
            if not _s(verifier.get(key)):
                _add(errors, f"verifier/{key}-invalid", f"{key} must be non-empty")
        digest = verifier.get("implementation_digest")
        if digest is not None and not _hash(digest):
            _add(errors, "verifier/digest-invalid", "implementation_digest must be null or SHA-256")
        if policy == "strict" and not _hash(digest):
            _add(errors, "verifier/digest-required", "strict measured acceptance requires verifier implementation identity")

    evaluator = data.get("evaluator")
    eval_contract = data.get("evaluation_contract")
    if not isinstance(evaluator, dict):
        _add(errors, "evaluator/missing", "evaluator object is required")
        evaluator = {}
    role = evaluator.get("role")
    if role not in ROLES:
        _add(errors, "evaluator/role-invalid", "evaluator role is invalid", observed=role)
    for key in ("evaluator_id", "scenario_set_id"):
        if not _s(evaluator.get(key)):
            _add(errors, f"evaluator/{key}-invalid", f"{key} must be non-empty")
    ed = evaluator.get("evaluator_digest")
    if ed is not None and not _hash(ed):
        _add(errors, "evaluator/digest-invalid", "evaluator_digest must be null or SHA-256")
    if role == "holdout" and (
        evaluator.get("candidate_had_access") is True
        or evaluator.get("selection_informed_by_results") is True
        or (isinstance(evaluator.get("exposure_generation_count"), int) and evaluator.get("exposure_generation_count", 0) > 0)
    ):
        _add(errors, "evaluator/holdout-contaminated", "declared holdout was exposed to candidate construction or selection")

    if not isinstance(eval_contract, dict):
        _add(errors, "evaluation/contract-missing", "evaluation_contract object is required")
        eval_contract = {}
    required_trials = eval_contract.get("required_trials")
    completed_trials = eval_contract.get("completed_trials")
    if not isinstance(required_trials, int) or required_trials < 0:
        _add(errors, "evaluation/required-trials-invalid", "required_trials must be a non-negative integer")
    if not isinstance(completed_trials, int) or completed_trials < 0:
        _add(errors, "evaluation/completed-trials-invalid", "completed_trials must be a non-negative integer")
    if isinstance(required_trials, int) and isinstance(completed_trials, int) and completed_trials < required_trials:
        _add(errors, "evaluation/trials-insufficient", "completed trials do not satisfy the caller-declared evaluation contract", required=required_trials, completed=completed_trials)
    if eval_contract.get("independent_replication_required") is True and eval_contract.get("independent_replication_completed") is not True:
        _add(errors, "evaluation/replication-missing", "independent replication is required but not completed")
    if eval_contract.get("holdout_required") is True and role != "holdout":
        _add(errors, "evaluation/holdout-missing", "the caller-declared contract requires holdout evidence")

    destination = data.get("destination")
    if not isinstance(destination, dict):
        _add(errors, "freshness/destination-missing", "destination object is required")
    else:
        expected = destination.get("expected_identity")
        observed = destination.get("observed_identity")
        required = destination.get("required") is True
        if required and (not _s(expected) or not _s(observed)):
            _add(errors, "freshness/destination-evidence-missing", "destination identity is required for this decision")
        if _s(expected) and _s(observed) and str(expected) != str(observed):
            _add(errors, "freshness/destination-stale", "destination state changed after the decision context was frozen", expected=expected, observed=observed)

    authority = data.get("authority")
    if not isinstance(authority, dict):
        _add(errors, "authority/missing", "authority object is required")
    elif authority.get("expanded") is True and authority.get("authorized") is not True:
        sink = errors if policy == "strict" else warnings
        _add(sink, "authority/expansion-unapproved", "authority surface expanded without explicit authorization", added_surfaces=authority.get("added_surfaces", []))

    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        _add(errors, "evidence/not-array", "evidence must be an array")
        evidence = []
    seen_evidence: set[str] = set()
    for idx, item in enumerate(evidence):
        if not isinstance(item, dict):
            _add(errors, "evidence/item-invalid", "evidence item must be an object", index=idx)
            continue
        eid = item.get("evidence_id")
        if not _s(eid):
            _add(errors, "evidence/id-invalid", "evidence_id must be non-empty", index=idx)
        elif eid in seen_evidence:
            _add(errors, "evidence/id-duplicate", "evidence_id must be unique", evidence_id=eid)
        else:
            seen_evidence.add(str(eid))
        status = item.get("status")
        if status not in EVIDENCE_STATUS:
            _add(errors, "evidence/status-invalid", "evidence status is invalid", evidence_id=eid, status=status)
        if item.get("required") is True and status != "pass":
            _add(errors, "evidence/required-not-pass", "required evidence is not pass", evidence_id=eid, status=status)
        subject = item.get("subject_candidate_tree_sha256")
        if not _hash(subject):
            _add(errors, "evidence/subject-invalid", "evidence subject candidate hash is invalid", evidence_id=eid)
        elif candidate_norm is not None and str(subject).lower() != candidate_norm:
            _add(errors, "evidence/subject-mismatch", "evidence belongs to candidate bytes different from the current candidate", evidence_id=eid, expected=candidate_norm, observed=str(subject).lower())
        for key in ("producer_id", "producer_version"):
            if not _s(item.get(key)):
                _add(errors, f"evidence/{key}-invalid", f"{key} must be non-empty", evidence_id=eid)
        epd = item.get("policy_digest")
        if epd is not None and not _hash(epd):
            _add(errors, "evidence/policy-digest-invalid", "evidence policy_digest must be null or SHA-256", evidence_id=eid)
        if policy_digest is not None and _hash(epd) and str(epd).lower() != policy_digest:
            _add(errors, "evidence/policy-mismatch", "evidence was produced under a different policy identity", evidence_id=eid)

    waivers = data.get("waivers")
    if not isinstance(waivers, list):
        _add(errors, "waiver/not-array", "waivers must be an array")
        waivers = []
    seen_waivers: set[str] = set()
    for idx, waiver in enumerate(waivers):
        if not isinstance(waiver, dict):
            _add(errors, "waiver/item-invalid", "waiver must be an object", index=idx)
            continue
        wid = waiver.get("waiver_id")
        if not _s(wid):
            _add(errors, "waiver/id-invalid", "waiver_id must be non-empty", index=idx)
        elif wid in seen_waivers:
            _add(errors, "waiver/id-duplicate", "waiver_id must be unique", waiver_id=wid)
        else:
            seen_waivers.add(str(wid))
        wh = waiver.get("candidate_tree_sha256")
        if not _hash(wh) or (candidate_norm is not None and str(wh).lower() != candidate_norm):
            _add(errors, "waiver/candidate-mismatch", "waiver does not identify the current candidate", waiver_id=wid)
        wpd = waiver.get("policy_digest")
        if not _hash(wpd):
            _add(errors, "waiver/policy-invalid", "waiver policy_digest must be SHA-256", waiver_id=wid)
        elif policy_digest is not None and str(wpd).lower() != policy_digest:
            _add(errors, "waiver/policy-mismatch", "waiver was authorized under a different policy", waiver_id=wid)
        if not _s(waiver.get("authorized_by")) or not _s(waiver.get("reason")):
            _add(errors, "waiver/authorization-incomplete", "waiver requires authorized_by and reason", waiver_id=wid)
        codes = waiver.get("finding_codes")
        if not isinstance(codes, list) or not codes or not all(_s(c) for c in codes):
            _add(errors, "waiver/finding-codes-invalid", "waiver finding_codes must be a non-empty string array", waiver_id=wid)
            codes = []
        for code in codes:
            if any(str(code).startswith(prefix) for prefix in NON_WAIVABLE_PREFIXES):
                _add(errors, "waiver/non-waivable", "waiver attempts to bypass a non-waivable finding class", waiver_id=wid, finding_code=code)

    consumers = data.get("known_consumers")
    if not isinstance(consumers, list):
        _add(errors, "consumer/not-array", "known_consumers must be an array")
        consumers = []
    if claim == "ecosystem-safe" and data.get("consumer_inventory_complete") is not True:
        _add(errors, "consumer/inventory-incomplete", "ecosystem-safe claim requires a complete known-consumer inventory")
    for idx, consumer in enumerate(consumers):
        if not isinstance(consumer, dict):
            _add(errors, "consumer/item-invalid", "consumer entry must be an object", index=idx)
            continue
        status = consumer.get("status")
        if status not in CONSUMER_STATUS:
            _add(errors, "consumer/status-invalid", "consumer status is invalid", index=idx, status=status)
        if claim == "ecosystem-safe" and status != "compatible":
            _add(errors, "consumer/not-compatible", "ecosystem-safe claim requires compatibility evidence for every known consumer", consumer_id=consumer.get("consumer_id"), status=status)

    return _result(errors, warnings)


def _result(errors: list[dict[str, object]], warnings: list[dict[str, object]]) -> dict[str, object]:
    return {
        "context_version": 1,
        "status": "fail" if errors else ("pass-with-warnings" if warnings else "pass"),
        "errors": sorted(errors, key=lambda x: (str(x.get("code")), json.dumps(x.get("evidence", {}), sort_keys=True))),
        "warnings": sorted(warnings, key=lambda x: (str(x.get("code")), json.dumps(x.get("evidence", {}), sort_keys=True))),
        "error_count": len(errors),
        "warning_count": len(warnings),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate Skill Change Gate Context v1.")
    parser.add_argument("context", help="gate context JSON")
    parser.add_argument("--policy", choices=sorted(POLICIES), default="normal")
    parser.add_argument("--expected-candidate-sha256")
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.context).read_text(encoding="utf-8"))
        result = validate(data, policy=args.policy, expected_candidate_sha256=args.expected_candidate_sha256)
    except Exception as exc:
        result = _result([{"code": "context/unreadable", "message": str(exc), "evidence": {}}], [])
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        Path(args.json_out).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if result["status"] in {"pass", "pass-with-warnings"} else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
