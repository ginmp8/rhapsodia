#!/usr/bin/env python3
"""Validate identity-bound execution evidence without depending on a host runner."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ARMS = {"without-skill", "baseline", "candidate", "single"}
STATUSES = {"executed", "supplied", "planned", "blocked"}
ISOLATION = {"workspace", "process", "container", "external-host"}
TRACE_STATUS = {"available", "unavailable", "not-required"}


def _sha(value: Any, *, nullable: bool = False) -> bool:
    if value is None:
        return nullable
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["execution evidence must be a JSON object"], "warnings": [], "checks": {}}

    schema_version = data.get("schema_version")
    if schema_version not in {1, 2}:
        errors.append("schema_version must be 1 or 2")
    if not isinstance(data.get("run_id"), str) or not data.get("run_id", "").strip():
        errors.append("run_id must be a non-empty string")
    arm = data.get("arm")
    if arm not in ARMS:
        errors.append(f"arm must be one of {sorted(ARMS)}")
    status = data.get("evidence_status")
    if status not in STATUSES:
        errors.append(f"evidence_status must be one of {sorted(STATUSES)}")

    target = data.get("target_identity_sha256")
    if arm == "without-skill":
        if target not in (None, ""):
            errors.append("without-skill arm must not declare target_identity_sha256")
    elif not _sha(target):
        errors.append("target_identity_sha256 must be lowercase 64-hex for skill-bearing arms")

    for field in ("evaluator_identity_sha256", "scenario_suite_sha256", "candidate_visible_manifest_sha256"):
        if not _sha(data.get(field)):
            errors.append(f"{field} must be lowercase 64-hex")
    if not _sha(data.get("evaluator_only_manifest_sha256"), nullable=True):
        errors.append("evaluator_only_manifest_sha256 must be lowercase 64-hex or null")

    if not isinstance(data.get("host_profile"), str) or not data.get("host_profile", "").strip():
        errors.append("host_profile must be a non-empty string")
    if data.get("isolation_level") not in ISOLATION:
        errors.append(f"isolation_level must be one of {sorted(ISOLATION)}")

    self_hosting = data.get("self_hosting")
    if self_hosting is not None:
        if not isinstance(self_hosting, dict):
            errors.append("self_hosting must be an object when present")
            self_hosting = {}
        generation_id = self_hosting.get("generation_id")
        if not isinstance(generation_id, str) or not generation_id.strip():
            errors.append("self_hosting.generation_id must be a non-empty string")
        for field in ("controller_identity_sha256", "baseline_identity_sha256", "candidate_identity_sha256"):
            if not _sha(self_hosting.get(field)):
                errors.append(f"self_hosting.{field} must be lowercase 64-hex")
        separated = self_hosting.get("controller_candidate_separated")
        read_only = self_hosting.get("controller_read_only")
        if not isinstance(separated, bool):
            errors.append("self_hosting.controller_candidate_separated must be boolean")
        if not isinstance(read_only, bool):
            errors.append("self_hosting.controller_read_only must be boolean")
        controller = self_hosting.get("controller_identity_sha256")
        candidate = self_hosting.get("candidate_identity_sha256")
        baseline = self_hosting.get("baseline_identity_sha256")
        if _sha(controller) and _sha(candidate):
            actual_separated = controller != candidate
            if separated is not actual_separated:
                errors.append("self_hosting.controller_candidate_separated does not match controller/candidate identities")
            if not actual_separated:
                errors.append("self-hosted candidate must not share the controller identity")
        if arm == "candidate" and _sha(candidate) and _sha(target) and candidate != target:
            errors.append("candidate arm target_identity_sha256 must equal self_hosting.candidate_identity_sha256")
        if arm == "baseline" and _sha(baseline) and _sha(target) and baseline != target:
            errors.append("baseline arm target_identity_sha256 must equal self_hosting.baseline_identity_sha256")
        if read_only is False:
            errors.append("self_hosting.controller_read_only must be true for measured self-hosted evidence")

    trace = data.get("trace")
    if not isinstance(trace, dict):
        errors.append("trace must be an object")
        trace = {}
    if trace.get("status") not in TRACE_STATUS:
        errors.append(f"trace.status must be one of {sorted(TRACE_STATUS)}")
    if trace.get("sha256") not in (None, "") and not _sha(trace.get("sha256")):
        errors.append("trace.sha256 must be lowercase 64-hex or null")
    if trace.get("status") == "available" and not (trace.get("reference") or trace.get("sha256")):
        errors.append("available trace requires reference or sha256")

    leakage = data.get("leakage_check")
    if not isinstance(leakage, dict):
        errors.append("leakage_check must be an object")
        leakage = {}
    leak_status = leakage.get("status")
    saw_hidden = leakage.get("candidate_saw_evaluator_only_assets")
    if leak_status not in {"pass", "fail", "not-applicable", "unknown"}:
        errors.append("leakage_check.status must be pass, fail, not-applicable, or unknown")
    if not isinstance(saw_hidden, bool):
        errors.append("leakage_check.candidate_saw_evaluator_only_assets must be boolean")
    if saw_hidden and leak_status != "fail":
        errors.append("leakage_check.status must be fail when candidate saw evaluator-only assets")
    if data.get("evaluator_only_manifest_sha256") and leak_status == "not-applicable":
        warnings.append("evaluator-only manifest exists but leakage check is marked not-applicable")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        errors.append("scenarios must be an array")
    elif status in {"executed", "supplied"} and not scenarios:
        warnings.append("executed/supplied evidence contains no scenario rows")

    self_hosting_ok = True
    if isinstance(self_hosting, dict) and self_hosting:
        self_hosting_ok = (
            self_hosting.get("controller_candidate_separated") is True
            and self_hosting.get("controller_read_only") is True
        )
    measured_eligible = (
        not errors
        and status == "executed"
        and leak_status in {"pass", "not-applicable"}
        and saw_hidden is False
        and self_hosting_ok
    )
    checks = {
        "arm": arm,
        "evidence_status": status,
        "isolation_level": data.get("isolation_level"),
        "hidden_evaluator_present": bool(data.get("evaluator_only_manifest_sha256")),
        "leakage_status": leak_status,
        "trace_status": trace.get("status"),
        "self_hosting_present": isinstance(self_hosting, dict) and bool(self_hosting),
        "self_hosting_generation_id": self_hosting.get("generation_id") if isinstance(self_hosting, dict) else None,
        "controller_read_only": self_hosting.get("controller_read_only") if isinstance(self_hosting, dict) else None,
        "measured_claim_eligible": measured_eligible,
    }
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", help="Execution evidence JSON")
    parser.add_argument("--json", help="Optional output report")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)], "warnings": [], "checks": {}}
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        Path(getattr(args, "json")).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
