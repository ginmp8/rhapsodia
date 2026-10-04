#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EVIDENCE_VERSION = 2
EXECUTION_KINDS = {"host-routing", "static-contract", "static-adjudication", "runtime"}
EVIDENCE_STATUSES = {"executed", "supplied", "planned", "blocked"}
VISIBILITY = {"hidden", "candidate-visible", "not-applicable"}
INVOCATION_MODES = {"explicit", "implicit", "contextual"}
DISCOVERY_MODES = {"automatic", "explicit-only", "hybrid", "unknown"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def routing_fingerprint(profile: dict[str, Any]) -> str:
    material = {
        "host": profile.get("host"),
        "host_version": profile.get("host_version"),
        "model_provider": profile.get("model_provider"),
        "model_name": profile.get("model_name"),
        "model_snapshot": profile.get("model_snapshot"),
        "discovery_mode": profile.get("discovery_mode"),
        "skill_catalog_sha256": profile.get("skill_catalog_sha256"),
        "skill_catalog_size": profile.get("skill_catalog_size"),
        "metadata_extensions": profile.get("metadata_extensions", []),
    }
    return canonical_hash(material)


def _error(errors: list[dict[str, Any]], code: str, subject: str, **evidence: Any) -> None:
    errors.append({"code": code, "subject": subject, "evidence": evidence})


def _valid_iso8601(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _validate_profile(profile: Any, errors: list[dict[str, Any]]) -> str | None:
    if not isinstance(profile, dict):
        _error(errors, "evidence/routing-profile", "routing_profile")
        return None
    required_strings = ["host", "host_version", "model_provider", "model_name", "model_snapshot"]
    for field in required_strings:
        if not isinstance(profile.get(field), str) or not profile[field].strip():
            _error(errors, "evidence/routing-profile-field", f"routing_profile.{field}", value=profile.get(field))
    if profile.get("discovery_mode") not in DISCOVERY_MODES:
        _error(errors, "evidence/discovery-mode", "routing_profile.discovery_mode", value=profile.get("discovery_mode"))
    catalog_hash = profile.get("skill_catalog_sha256")
    if not isinstance(catalog_hash, str) or not SHA256_RE.fullmatch(catalog_hash):
        _error(errors, "evidence/catalog-hash", "routing_profile.skill_catalog_sha256", value=catalog_hash)
    catalog_size = profile.get("skill_catalog_size")
    if not isinstance(catalog_size, int) or isinstance(catalog_size, bool) or catalog_size < 1:
        _error(errors, "evidence/catalog-size", "routing_profile.skill_catalog_size", value=catalog_size)
    extensions = profile.get("metadata_extensions", [])
    if not isinstance(extensions, list) or any(not isinstance(v, str) or not v.strip() for v in extensions):
        _error(errors, "evidence/metadata-extensions", "routing_profile.metadata_extensions", value=extensions)
    return routing_fingerprint(profile)


def validate_evidence(data: dict[str, Any], suite: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    if data.get("evidence_version") != EVIDENCE_VERSION:
        _error(errors, "evidence/version", "evidence_version", expected=EVIDENCE_VERSION, actual=data.get("evidence_version"))

    for field in ("suite_sha256", "evaluator_sha256"):
        value = data.get(field)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            _error(errors, "evidence/hash", field, value=value)

    execution_kind = data.get("execution_kind")
    if execution_kind not in EXECUTION_KINDS:
        _error(errors, "evidence/execution-kind", "execution_kind", value=execution_kind)
    evidence_status = data.get("evidence_status")
    if evidence_status not in EVIDENCE_STATUSES:
        _error(errors, "evidence/status", "evidence_status", value=evidence_status)
    if evidence_status in {"executed", "supplied"} and not _valid_iso8601(data.get("executed_at")):
        _error(errors, "evidence/executed-at", "executed_at", value=data.get("executed_at"))

    visibility = data.get("evaluator_visibility")
    if visibility not in VISIBILITY:
        _error(errors, "evidence/evaluator-visibility", "evaluator_visibility", value=visibility)
    if visibility == "hidden" and data.get("candidate_saw_evaluator_only_assets") is not False:
        _error(
            errors,
            "evidence/evaluator-leakage",
            "candidate_saw_evaluator_only_assets",
            evaluator_visibility=visibility,
            actual=data.get("candidate_saw_evaluator_only_assets"),
        )

    derived_fingerprint = _validate_profile(data.get("routing_profile"), errors)
    supplied_fingerprint = data.get("routing_fingerprint_sha256")
    if derived_fingerprint is not None and supplied_fingerprint != derived_fingerprint:
        _error(
            errors,
            "evidence/routing-fingerprint",
            "routing_fingerprint_sha256",
            expected=derived_fingerprint,
            actual=supplied_fingerprint,
        )

    trial_policy = data.get("trial_policy")
    trials_per_case = None
    if not isinstance(trial_policy, dict):
        _error(errors, "evidence/trial-policy", "trial_policy")
    else:
        if trial_policy.get("mode") != "fixed-trials":
            _error(errors, "evidence/trial-mode", "trial_policy.mode", value=trial_policy.get("mode"))
        trials_per_case = trial_policy.get("trials_per_case")
        if not isinstance(trials_per_case, int) or isinstance(trials_per_case, bool) or trials_per_case < 1:
            _error(errors, "evidence/trial-count", "trial_policy.trials_per_case", value=trials_per_case)

    cases = data.get("cases")
    if not isinstance(cases, list):
        _error(errors, "evidence/cases", "cases")
        cases = []
    seen: set[str] = set()
    normalized_cases: list[dict[str, Any]] = []
    suite_map = {}
    if suite is not None:
        suite_map = {s.get("id"): s for s in suite.get("scenarios", []) if isinstance(s, dict)}

    for index, case in enumerate(cases):
        subject = f"case[{index}]"
        if not isinstance(case, dict):
            _error(errors, "evidence/case-object", subject)
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            _error(errors, "evidence/case-id", subject, value=case_id)
            continue
        if case_id in seen:
            _error(errors, "evidence/case-duplicate", case_id)
        seen.add(case_id)
        invocation_mode = case.get("invocation_mode")
        if invocation_mode not in INVOCATION_MODES:
            _error(errors, "evidence/invocation-mode", case_id, value=invocation_mode)
        if case_id in suite_map and invocation_mode != suite_map[case_id].get("invocation_mode"):
            _error(
                errors,
                "evidence/invocation-mode-mismatch",
                case_id,
                expected=suite_map[case_id].get("invocation_mode"),
                actual=invocation_mode,
            )
        trials = case.get("trials")
        if not isinstance(trials, list):
            _error(errors, "evidence/trials", case_id)
            trials = []
        if isinstance(trials_per_case, int) and len(trials) != trials_per_case:
            _error(errors, "evidence/trial-count-mismatch", case_id, expected=trials_per_case, actual=len(trials))
        activations = 0
        route_counts: dict[str, int] = {}
        for t_index, trial in enumerate(trials):
            t_subject = f"{case_id}.trial[{t_index}]"
            if not isinstance(trial, dict):
                _error(errors, "evidence/trial-object", t_subject)
                continue
            if not isinstance(trial.get("activated"), bool):
                _error(errors, "evidence/trial-activated", t_subject, value=trial.get("activated"))
            elif trial["activated"]:
                activations += 1
            route = trial.get("observed_route")
            if not isinstance(route, str) or not route.strip():
                _error(errors, "evidence/trial-route", t_subject, value=route)
            else:
                route_counts[route] = route_counts.get(route, 0) + 1
        normalized_cases.append(
            {
                "id": case_id,
                "invocation_mode": invocation_mode,
                "trial_count": len(trials),
                "activation_count": activations,
                "trigger_rate": (activations / len(trials)) if trials else None,
                "route_counts": dict(sorted(route_counts.items())),
            }
        )

    if suite is not None:
        expected_ids = set(suite_map)
        if seen != expected_ids:
            _error(errors, "evidence/case-set", "cases", missing=sorted(expected_ids - seen), extra=sorted(seen - expected_ids))

    return {
        "status": "fail" if errors else "pass",
        "evidence_version": data.get("evidence_version"),
        "routing_fingerprint_sha256": derived_fingerprint,
        "trial_policy": trial_policy,
        "cases": normalized_cases,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate v2 activation-routing execution evidence and derive its routing fingerprint.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--suite")
    parser.add_argument("--json")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    suite = json.loads(Path(args.suite).read_text(encoding="utf-8")) if args.suite else None
    report = validate_evidence(data, suite)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        Path(args.json).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
