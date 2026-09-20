from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_SHA256_REF_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
_REQUIRED_RUN_FIELDS = (
    "candidate_id",
    "candidate_identity",
    "run_id",
    "trace_id",
    "trace_manifest_id",
    "trace_manifest_sha256",
    "work_dir",
    "evaluator_id",
    "scenario_set_id",
    "evaluation_policy_id",
)
_COMPARABLE_FIELDS = ("evaluator_id", "scenario_set_id", "evaluation_policy_id")


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data):
    errors = []
    version = data.get("contract_version")
    if version not in {1, 2}:
        errors.append("contract_version:unsupported")

    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        return sorted(set(errors + ["runs:invalid"]))

    candidate_identities = {}
    identity_owners = {}
    run_ids = set()
    work_dirs = set()
    trace_ids = set()
    trace_manifest_ids = set()
    trace_manifest_hashes = set()
    comparable_refs = {}

    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            errors.append(f"run[{index}]:invalid")
            continue

        for field in _REQUIRED_RUN_FIELDS:
            if not _nonempty(run.get(field)):
                errors.append(f"run[{index}].{field}:missing")

        candidate_id = run.get("candidate_id")
        candidate_identity = run.get("candidate_identity")
        if _nonempty(candidate_id) and _nonempty(candidate_identity):
            previous_identity = candidate_identities.get(candidate_id)
            if previous_identity is not None and previous_identity != candidate_identity:
                errors.append(f"candidate_id:identity_mismatch:{candidate_id}")
            else:
                candidate_identities[candidate_id] = candidate_identity

            previous_owner = identity_owners.get(candidate_identity)
            if previous_owner is not None and previous_owner != candidate_id:
                errors.append("candidate_identity:shared_by_distinct_candidates")
            else:
                identity_owners[candidate_identity] = candidate_id

        run_id = run.get("run_id")
        if _nonempty(run_id):
            if run_id in run_ids:
                errors.append("run_id:duplicate")
            run_ids.add(run_id)

        work_dir = run.get("work_dir")
        if _nonempty(work_dir):
            if work_dir in work_dirs:
                errors.append("work_dir:shared")
            work_dirs.add(work_dir)

        trace_id = run.get("trace_id")
        if _nonempty(trace_id):
            if trace_id in trace_ids:
                errors.append("trace_id:duplicate")
            trace_ids.add(trace_id)

        trace_manifest_id = run.get("trace_manifest_id")
        if _nonempty(trace_manifest_id):
            if trace_manifest_id in trace_manifest_ids:
                errors.append("trace_manifest_id:duplicate")
            trace_manifest_ids.add(trace_manifest_id)

        trace_manifest_sha256 = run.get("trace_manifest_sha256")
        if _nonempty(trace_manifest_sha256):
            normalized_hash = trace_manifest_sha256.lower()
            valid_hash = _SHA256_RE.fullmatch(trace_manifest_sha256) if version == 1 else _SHA256_REF_RE.fullmatch(trace_manifest_sha256)
            if not valid_hash:
                errors.append(f"run[{index}].trace_manifest_sha256:invalid")
            elif normalized_hash in trace_manifest_hashes:
                errors.append("trace_manifest_sha256:duplicate")
            else:
                trace_manifest_hashes.add(normalized_hash)

        for field in _COMPARABLE_FIELDS:
            value = run.get(field)
            if _nonempty(value) and field not in comparable_refs:
                comparable_refs[field] = value
            elif _nonempty(value) and comparable_refs[field] != value:
                errors.append(f"comparability:{field}:mismatch")

        if (
            run.get("holdout_blind") is True
            and run.get("candidate_saw_evaluator_only_assets") is not False
        ):
            errors.append(f"run[{index}]:holdout_leakage")

    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors = validate(data)
    print(
        json.dumps(
            {
                "status": "pass" if not errors else "fail",
                "contract_version": data.get("contract_version"),
                "errors": errors,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
