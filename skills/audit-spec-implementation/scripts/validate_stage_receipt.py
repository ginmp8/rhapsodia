#!/usr/bin/env python3
"""Validate audit-stage/v1 handoff hygiene, not underlying truth or skill execution."""
import argparse
import json
import sys
from pathlib import Path

STAGES = {"criteria", "implementation", "causal", "verification", "parity"}
PROOF_TYPES = {"source", "code", "test_defined", "executed_test", "runtime_observation", "static_proof", "inference"}
RESULTS = {"passed", "failed", "not_run", "inconclusive"}
STATUS = {"completed", "blocked", "not-run", "skipped"}


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def validate(receipt, expected_head=None, expected_source=None):
    errors = []
    if not isinstance(receipt, dict):
        return ["receipt must be a JSON object"]
    if receipt.get("schema_version") != "audit-stage/v1":
        errors.append("schema_version must equal audit-stage/v1")
    if receipt.get("stage") not in STAGES:
        errors.append("stage is unknown")
    if receipt.get("status") not in STATUS:
        errors.append("status is unknown")
    identity = receipt.get("identity") or {}
    if not isinstance(identity, dict):
        identity = {}
    for k in ("base_sha", "head_sha", "source_snapshot"):
        if not nonblank(identity.get(k)):
            errors.append("identity." + k + " must be nonblank")
    if expected_head and identity.get("head_sha") != expected_head:
        errors.append("head_sha disagrees with frozen candidate")
    if expected_source and identity.get("source_snapshot") != expected_source:
        errors.append("source_snapshot disagrees with frozen source")
    delegate = receipt.get("delegate") or {}
    if not isinstance(delegate, dict):
        delegate = {}
    if delegate.get("mode") not in {"external-skill", "local-adapter", "none"}:
        errors.append("delegate.mode is invalid")
    if not isinstance(delegate.get("invoked"), bool):
        errors.append("delegate.invoked must be boolean")
    if delegate.get("invoked") is True and (not nonblank(delegate.get("skill")) or not nonblank(delegate.get("invocation_evidence"))):
        errors.append("Invoked delegate requires skill and invocation_evidence")
    if receipt.get("status") == "completed" and not delegate.get("invoked"):
        errors.append("completed stage cannot claim uninvoked delegate")
    if receipt.get("status") in {"skipped", "not-run"} and delegate.get("invoked"):
        errors.append("skipped/not-run stage cannot claim invoked delegate")
    required_ids = receipt.get("requirement_ids")
    if not isinstance(required_ids, list) or any(not nonblank(x) or not x.startswith("REQ-") for x in required_ids):
        errors.append("requirement_ids must be a list of REQ-* strings")
        required_ids = []
    if len(set(required_ids)) != len(required_ids):
        errors.append("requirement_ids must be unique")
    evidence = receipt.get("evidence")
    if not isinstance(evidence, list):
        evidence = []
        errors.append("evidence must be a list")
    if receipt.get("status") == "completed" and not evidence:
        errors.append("completed stage requires evidence")
    for idx, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{idx}] must be object")
            continue
        if item.get("requirement_id") not in required_ids:
            errors.append(f"evidence[{idx}].requirement_id not declared")
        if item.get("kind") not in PROOF_TYPES or item.get("result") not in RESULTS:
            errors.append(f"evidence[{idx}] has invalid kind or result")
        if not nonblank(item.get("locator")) or not nonblank(item.get("candidate_sha")):
            errors.append(f"evidence[{idx}] requires locator and candidate_sha")
        if item.get("candidate_sha") != identity.get("head_sha"):
            errors.append(f"evidence[{idx}] uses stale/mismatched candidate SHA")
        if item.get("kind") == "test_defined" and item.get("result") == "passed":
            errors.append(f"evidence[{idx}] test_defined cannot prove passed")
        if item.get("kind") in {"executed_test", "runtime_observation"} and item.get("result") in {"passed", "failed"}:
            if any(not nonblank(item.get(k)) for k in ("command", "environment", "observed_at")):
                errors.append(f"evidence[{idx}] runtime proof needs command, environment, observed_at")
    if not isinstance(receipt.get("limitations"), list):
        errors.append("limitations must be a list")
    return errors


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("receipt")
    p.add_argument("--expected-head")
    p.add_argument("--expected-source")
    args = p.parse_args(argv)
    try:
        document = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as ex:
        print(str(ex), file=sys.stderr)
        return 2
    errors = validate(document, expected_head=args.expected_head, expected_source=args.expected_source)
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    print("audit-stage/v1 VALID" if not errors else "audit-stage/v1 INVALID")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
