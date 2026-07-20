#!/usr/bin/env python3
"""Select a minimum MAGIA execution profile and validation checks from change risk."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GOVERNED_SIGNALS = {
    "migration", "destructive", "public_contract", "authentication", "authorization",
    "secrets", "pii", "compliance", "security", "infrastructure", "multi_repository",
    "cross_service", "complex_rollback", "data_loss",
}
STANDARD_SIGNALS = {
    "persistence", "concurrency", "messaging", "performance", "observability",
    "shared_component", "stateful", "multi_step",
}

CHECKS_BY_RISK = {
    "localized": ["targeted_test_or_static_check"],
    "shared_component": ["targeted_tests", "build_or_type_check", "regression_check"],
    "public_contract": ["contract_tests", "compatibility_review", "consumer_impact_review", "smoke_check"],
    "persistence": ["integration_tests", "transaction_or_data_validation"],
    "migration": ["migration_validation", "expand_contract_review", "data_validation", "rollback_check"],
    "authentication": ["authorization_negative_tests", "security_review"],
    "authorization": ["authorization_negative_tests", "least_privilege_review"],
    "secrets": ["secret_scan", "sensitive_log_review"],
    "pii": ["privacy_data_handling_review", "sensitive_log_review"],
    "security": ["security_checks", "negative_tests"],
    "concurrency": ["concurrency_or_ordering_tests", "idempotency_review"],
    "messaging": ["delivery_retry_ordering_tests", "idempotency_review", "operational_signal_check"],
    "performance": ["representative_performance_check", "regression_comparison"],
    "observability": ["log_metric_trace_check", "operational_verification"],
    "infrastructure": ["configuration_validation", "deployment_smoke_check", "rollback_check"],
    "multi_repository": ["per_repository_checks", "compatibility_window_check", "cross_repository_smoke_check"],
    "destructive": ["data_loss_review", "rollback_check"],
    "complex_rollback": ["rollback_check", "forward_fix_plan"],
    "compliance": ["compliance_control_review", "audit_evidence_check"],
    "data_loss": ["data_loss_review", "backup_or_recovery_check"],
    "cross_service": ["contract_tests", "compatibility_window_check", "end_to_end_smoke_check"],
}

DOCS_BY_RISK = {
    "migration": "migration-execution-note.md",
    "public_contract": "contract-change-note.md",
    "security": "security-risk-note.md",
    "secrets": "security-risk-note.md",
    "pii": "security-risk-note.md",
    "observability": "observability-note.md",
    "infrastructure": "runbook.md",
    "complex_rollback": "runbook.md",
    "multi_repository": "implementation-notes.md",
}


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def infer_risks(payload: dict[str, Any]) -> list[str]:
    risks = [str(item).strip().lower() for item in payload.get("risk_signals", []) if str(item).strip()]
    files = [str(item).lower() for item in payload.get("changed_files", [])]
    for path in files:
        name = Path(path).name
        suffix = Path(path).suffix
        if "migration" in path or name in {"schema.sql", "database.sql"}:
            risks.append("migration")
        if suffix in {".sql"}:
            risks.append("persistence")
        if any(token in path for token in ("auth", "permission", "policy", "role")):
            risks.append("authorization")
        if any(token in path for token in ("secret", "credential", ".env")):
            risks.append("secrets")
        if any(token in path for token in ("contract", "openapi", "asyncapi", "proto", "schema")):
            risks.append("public_contract")
        if any(token in path for token in ("terraform", "helm", "kustomize", "dockerfile", "pipeline", "workflow")):
            risks.append("infrastructure")
        if any(token in path for token in ("message", "event", "consumer", "producer", "queue", "topic")):
            risks.append("messaging")
    boolean_signals = payload.get("signals", {})
    if isinstance(boolean_signals, dict):
        risks.extend(str(key).lower() for key, value in boolean_signals.items() if value)
    if len(files) > 1:
        risks.append("multi_step")
    if not risks:
        risks.append("localized")
    return _dedupe(risks)


def select(payload: dict[str, Any]) -> dict[str, Any]:
    requested = str(payload.get("requested_profile", "quick")).lower()
    if requested not in {"quick", "standard", "governed"}:
        raise ValueError("requested_profile must be quick, standard, or governed")
    risks = infer_risks(payload)
    escalation_reasons: list[str] = []
    minimum = "quick"
    if any(risk in STANDARD_SIGNALS for risk in risks) or len(payload.get("changed_files", [])) > 1:
        minimum = "standard"
    if any(risk in GOVERNED_SIGNALS for risk in risks):
        minimum = "governed"
    order = {"quick": 0, "standard": 1, "governed": 2}
    profile = requested if order[requested] >= order[minimum] else minimum
    if profile != requested:
        escalation_reasons.append(f"requested {requested} escalated to {profile} by detected risk")

    checks: list[str] = []
    for risk in risks:
        checks.extend(CHECKS_BY_RISK.get(risk, []))
    if profile in {"standard", "governed"}:
        checks.extend(["targeted_tests", "build_lint_or_type_checks_as_applicable", "regression_check"])
    if profile == "governed":
        checks.extend(["convergence_validation", "rollback_verification", "operational_verification_if_triggered"])

    documents = _dedupe([DOCS_BY_RISK[risk] for risk in risks if risk in DOCS_BY_RISK])
    result = {
        "profile": profile,
        "minimum_profile": minimum,
        "risk_classes": risks,
        "required_checks": _dedupe(checks),
        "required_documents": documents,
        "minimum_evidence": {
            "quick": ["inspected_target", "changed_files", "one_relevant_check"],
            "standard": ["context_map", "changed_file_check_mapping", "regression_evidence", "rollback_steps"],
            "governed": ["complete_traceability", "compatibility_evidence", "rollback_evidence", "operational_evidence_if_triggered"],
        }[profile],
        "run_state_required": profile == "governed" or bool(payload.get("resumable")) or len(payload.get("changed_files", [])) > 1,
        "escalation_reasons": escalation_reasons,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON change descriptor")
    parser.add_argument("--output", help="Optional JSON result path")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("input root must be an object")
        result = select(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
