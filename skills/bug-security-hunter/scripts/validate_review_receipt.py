#!/usr/bin/env python3
"""Validate machine-readable Bug Security Hunter review receipts."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

MODES = {
    "pr-risk-review",
    "flow-bug-hunt",
    "project-wide-audit",
    "security-threat-review",
    "stress-harness-design",
    "quick-triage",
}
SEVERITIES = ("BLOCKER", "MAJOR", "MINOR", "NIT", "QUESTION")
SEVERITY_RANK = {name: i for i, name in enumerate(SEVERITIES)}
CONFIDENCE = {"confirmed", "likely", "needs-verification", "not-applicable"}
EVIDENCE_STATUS = {"measured", "observed", "supplied", "inferred", "planned", "blocked", "out-of-scope"}
GAP_STATUS = {"planned", "blocked", "out-of-scope", "needs-verification"}
VALIDATION_STATUS = {"measured", "supplied", "planned", "blocked"}
VERDICTS = {"APPROVED", "APPROVED_WITH_COMMENTS", "CHANGES_REQUESTED", "NEEDS_MORE_CONTEXT", "NOT_APPLICABLE"}
TREATMENTS = {
    "Fix in this PR",
    "Already fixed by the author in this PR",
    "Accepted by the team without change",
    "Future issue opened for follow-up",
    "Not applicable",
    "Pending verification",
}
CATEGORY_RANK = {
    "authorization": 0,
    "data-exposure": 0,
    "security": 0,
    "data-loss": 1,
    "data-integrity": 1,
    "irreversible-side-effect": 2,
    "contract": 3,
    "migration": 3,
    "reliability": 4,
    "concurrency": 4,
    "performance": 5,
    "observability": 6,
    "maintainability": 7,
    "style": 8,
}
OBVIOUS_SECRET_PATTERNS = [
    re.compile(r"\bBearer\s+(?!\*{3}|[^\s]{0,4}\*{3})[A-Za-z0-9._~+/-]{12,}", re.I),
    re.compile(r"\b(?:AWS_SECRET_ACCESS_KEY|API_TOKEN|CLIENT_SECRET|PASSWORD)\s*[=:]\s*(?!\*{3}|[^\s]{0,4}\*{3})[^\s,;]{8,}", re.I),
]


def diagnostic(code: str, subject: str, evidence: str) -> dict[str, str]:
    return {"code": code, "subject": subject, "evidence": evidence}


def reject_extra_keys(obj: dict[str, Any], allowed: set[str], subject: str, errors: list[dict[str, str]]) -> None:
    for key in sorted(set(obj) - allowed):
        errors.append(diagnostic("schema/unexpected-field", f"{subject}.{key}" if subject else key, "field is not allowed by the closed receipt contract"))


def require_string(obj: dict[str, Any], key: str, subject: str, errors: list[dict[str, str]]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(diagnostic("schema/nonempty-string", f"{subject}.{key}", repr(value)))
        return None
    return value


def validate_evidence(item: Any, subject: str, errors: list[dict[str, str]]) -> None:
    if not isinstance(item, dict):
        errors.append(diagnostic("schema/evidence-object", subject, type(item).__name__))
        return
    reject_extra_keys(item, {"status", "subject", "detail", "sensitive", "redacted"}, subject, errors)
    status = item.get("status")
    if status not in EVIDENCE_STATUS:
        errors.append(diagnostic("enum/evidence-status", f"{subject}.status", repr(status)))
    require_string(item, "subject", subject, errors)
    detail = require_string(item, "detail", subject, errors)
    sensitive = item.get("sensitive")
    redacted = item.get("redacted")
    if not isinstance(sensitive, bool):
        errors.append(diagnostic("schema/evidence-sensitive", f"{subject}.sensitive", repr(sensitive)))
    if not isinstance(redacted, bool):
        errors.append(diagnostic("schema/evidence-redacted", f"{subject}.redacted", repr(redacted)))
    if sensitive is True and redacted is not True:
        errors.append(diagnostic("safety/sensitive-evidence-unredacted", subject, "sensitive=true requires redacted=true"))
    if detail:
        for pattern in OBVIOUS_SECRET_PATTERNS:
            if pattern.search(detail):
                errors.append(diagnostic("safety/probable-secret-in-evidence", f"{subject}.detail", "probable unmasked secret-like value"))
                break


def category_rank(category: str) -> int:
    normalized = category.strip().lower().replace("_", "-")
    for key, rank in CATEGORY_RANK.items():
        if key in normalized:
            return rank
    return 50


def finding_sort_key(finding: dict[str, Any]) -> tuple[Any, ...]:
    severity = finding.get("severity", "QUESTION")
    blocks = finding.get("blocks_merge") is True
    category = str(finding.get("category", ""))
    subject = str(finding.get("subject", "")).lower()
    fingerprint = str(finding.get("fingerprint", "")).lower()
    return (SEVERITY_RANK.get(severity, 99), 0 if blocks else 1, category_rank(category), subject, fingerprint)


def expected_pr_verdict(receipt: dict[str, Any]) -> str:
    findings = receipt.get("findings", [])
    gaps = receipt.get("validation_gaps", [])
    if any(isinstance(f, dict) and f.get("severity") == "BLOCKER" for f in findings):
        return "CHANGES_REQUESTED"
    if any(isinstance(f, dict) and f.get("severity") == "MAJOR" and f.get("blocks_merge") is True for f in findings):
        return "CHANGES_REQUESTED"
    if any(isinstance(f, dict) and f.get("severity") == "QUESTION" for f in findings):
        return "NEEDS_MORE_CONTEXT"
    essential_gap = any(
        isinstance(g, dict) and g.get("status") in {"blocked", "needs-verification"}
        for g in gaps
    )
    if essential_gap:
        return "NEEDS_MORE_CONTEXT"
    material = [f for f in findings if isinstance(f, dict) and f.get("severity") in {"MAJOR", "MINOR", "NIT"}]
    if material:
        return "APPROVED_WITH_COMMENTS"
    coverage = receipt.get("coverage", {})
    if isinstance(coverage, dict) and coverage.get("status") != "complete-for-scope":
        return "NEEDS_MORE_CONTEXT"
    return "APPROVED"


def validate_receipt(receipt: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(receipt, dict):
        return [diagnostic("schema/root-object", "$", type(receipt).__name__)]
    reject_extra_keys(receipt, {"receipt_version", "target", "mode", "scope", "findings", "validation_gaps", "validation", "coverage", "verdict"}, "", errors)

    if receipt.get("receipt_version") != 1:
        errors.append(diagnostic("schema/receipt-version", "receipt_version", repr(receipt.get("receipt_version"))))

    target = receipt.get("target")
    if not isinstance(target, dict):
        errors.append(diagnostic("schema/target-object", "target", type(target).__name__))
    else:
        reject_extra_keys(target, {"kind", "identity", "revision", "environment", "snapshot_sha256"}, "target", errors)
        require_string(target, "kind", "target", errors)
        require_string(target, "identity", "target", errors)
        for key in ("revision", "environment"):
            value = target.get(key)
            if value is not None and not isinstance(value, str):
                errors.append(diagnostic("schema/string-or-null", f"target.{key}", repr(value)))
        snapshot = target.get("snapshot_sha256")
        if snapshot is not None and (not isinstance(snapshot, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", snapshot)):
            errors.append(diagnostic("schema/sha256", "target.snapshot_sha256", repr(snapshot)))

    mode = receipt.get("mode")
    if mode not in MODES:
        errors.append(diagnostic("enum/mode", "mode", repr(mode)))

    scope = receipt.get("scope")
    if not isinstance(scope, dict):
        errors.append(diagnostic("schema/scope-object", "scope", type(scope).__name__))
    else:
        reject_extra_keys(scope, {"reviewed", "assumptions", "uninspected"}, "scope", errors)
        for key in ("reviewed", "assumptions", "uninspected"):
            value = scope.get(key)
            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                errors.append(diagnostic("schema/string-array", f"scope.{key}", repr(value)))

    findings = receipt.get("findings")
    if not isinstance(findings, list):
        errors.append(diagnostic("schema/findings-array", "findings", type(findings).__name__))
        findings = []

    seen_ids: set[str] = set()
    seen_fingerprints: set[str] = set()
    for i, finding in enumerate(findings):
        subject = f"findings[{i}]"
        if not isinstance(finding, dict):
            errors.append(diagnostic("schema/finding-object", subject, type(finding).__name__))
            continue
        reject_extra_keys(finding, {"finding_id", "category", "subject", "severity", "confidence", "evidence_status", "evidence", "trigger_or_condition", "problem", "impact", "severity_rationale", "smallest_fix", "validation", "blocks_merge", "expected_treatment", "fingerprint"}, subject, errors)
        finding_id = finding.get("finding_id")
        if not isinstance(finding_id, str) or not re.fullmatch(r"BSH-[0-9]{3}", finding_id):
            errors.append(diagnostic("schema/finding-id", f"{subject}.finding_id", repr(finding_id)))
        elif finding_id in seen_ids:
            errors.append(diagnostic("dedup/duplicate-finding-id", f"{subject}.finding_id", finding_id))
        else:
            seen_ids.add(finding_id)
        for field in ("category", "subject", "trigger_or_condition", "problem", "impact", "severity_rationale", "smallest_fix", "validation", "fingerprint"):
            require_string(finding, field, subject, errors)
        severity = finding.get("severity")
        if severity not in SEVERITIES:
            errors.append(diagnostic("enum/severity", f"{subject}.severity", repr(severity)))
        confidence = finding.get("confidence")
        if confidence not in CONFIDENCE:
            errors.append(diagnostic("enum/confidence", f"{subject}.confidence", repr(confidence)))
        evidence_status = finding.get("evidence_status")
        if evidence_status not in EVIDENCE_STATUS:
            errors.append(diagnostic("enum/evidence-status", f"{subject}.evidence_status", repr(evidence_status)))
        if severity != "QUESTION" and confidence == "needs-verification":
            errors.append(diagnostic("consistency/unverified-material-finding", subject, "needs-verification should normally be QUESTION or a gap"))
        evidence = finding.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(diagnostic("schema/evidence-array", f"{subject}.evidence", repr(evidence)))
        else:
            for j, item in enumerate(evidence):
                validate_evidence(item, f"{subject}.evidence[{j}]", errors)
            evidence_statuses = {item.get("status") for item in evidence if isinstance(item, dict)}
            if evidence_status not in evidence_statuses:
                errors.append(diagnostic("consistency/primary-evidence-status", subject, f"primary {evidence_status!r} not present in evidence statuses {sorted(map(str, evidence_statuses))}"))
        blocks = finding.get("blocks_merge")
        if blocks not in {True, False, None}:
            errors.append(diagnostic("schema/blocks-merge", f"{subject}.blocks_merge", repr(blocks)))
        treatment = finding.get("expected_treatment")
        if treatment not in TREATMENTS:
            errors.append(diagnostic("enum/expected-treatment", f"{subject}.expected_treatment", repr(treatment)))
        fingerprint = finding.get("fingerprint")
        if isinstance(fingerprint, str) and fingerprint.strip():
            norm = " ".join(fingerprint.lower().split())
            if norm in seen_fingerprints:
                errors.append(diagnostic("dedup/duplicate-fingerprint", f"{subject}.fingerprint", fingerprint))
            seen_fingerprints.add(norm)
        if severity == "NIT" and blocks is True:
            errors.append(diagnostic("consistency/nit-cannot-block", subject, "NIT cannot block merge"))
        if severity == "QUESTION" and confidence != "needs-verification":
            errors.append(diagnostic("consistency/question-needs-verification", subject, "QUESTION should use needs-verification confidence"))
        if severity == "MAJOR" and mode == "pr-risk-review" and blocks is False and treatment not in {"Accepted by the team without change", "Future issue opened for follow-up"}:
            errors.append(diagnostic("consistency/nonblocking-major-needs-acceptance", subject, "non-blocking MAJOR requires explicit acceptance or deferred follow-up"))
        if severity == "BLOCKER" and mode == "pr-risk-review" and blocks is not True:
            errors.append(diagnostic("consistency/blocker-must-block", subject, "BLOCKER in PR review must set blocks_merge=true"))

    expected_order = sorted(findings, key=finding_sort_key) if all(isinstance(f, dict) for f in findings) else findings
    if findings != expected_order:
        errors.append(diagnostic("ordering/findings", "findings", "findings are not in canonical severity/category/subject order"))
    for i, finding in enumerate(findings, start=1):
        if isinstance(finding, dict) and finding.get("finding_id") != f"BSH-{i:03d}":
            errors.append(diagnostic("ordering/finding-id-sequence", f"findings[{i-1}].finding_id", f"expected BSH-{i:03d}"))

    gaps = receipt.get("validation_gaps")
    if not isinstance(gaps, list):
        errors.append(diagnostic("schema/validation-gaps-array", "validation_gaps", type(gaps).__name__))
        gaps = []
    for i, gap in enumerate(gaps):
        subject = f"validation_gaps[{i}]"
        if not isinstance(gap, dict):
            errors.append(diagnostic("schema/gap-object", subject, type(gap).__name__))
            continue
        reject_extra_keys(gap, {"subject", "status", "why_it_matters", "next_evidence"}, subject, errors)
        for field in ("subject", "why_it_matters", "next_evidence"):
            require_string(gap, field, subject, errors)
        if gap.get("status") not in GAP_STATUS:
            errors.append(diagnostic("enum/gap-status", f"{subject}.status", repr(gap.get("status"))))

    validation = receipt.get("validation")
    if not isinstance(validation, list):
        errors.append(diagnostic("schema/validation-array", "validation", type(validation).__name__))
    else:
        for i, check in enumerate(validation):
            subject = f"validation[{i}]"
            if not isinstance(check, dict):
                errors.append(diagnostic("schema/validation-object", subject, type(check).__name__))
                continue
            reject_extra_keys(check, {"name", "status", "evidence"}, subject, errors)
            require_string(check, "name", subject, errors)
            require_string(check, "evidence", subject, errors)
            if check.get("status") not in VALIDATION_STATUS:
                errors.append(diagnostic("enum/validation-status", f"{subject}.status", repr(check.get("status"))))

    coverage = receipt.get("coverage")
    if not isinstance(coverage, dict):
        errors.append(diagnostic("schema/coverage-object", "coverage", type(coverage).__name__))
    else:
        reject_extra_keys(coverage, {"status", "notes"}, "coverage", errors)
        if coverage.get("status") not in {"complete-for-scope", "partial", "blocked"}:
            errors.append(diagnostic("enum/coverage-status", "coverage.status", repr(coverage.get("status"))))
        notes = coverage.get("notes")
        if not isinstance(notes, list) or not all(isinstance(x, str) for x in notes):
            errors.append(diagnostic("schema/string-array", "coverage.notes", repr(notes)))

    verdict = receipt.get("verdict")
    if verdict not in VERDICTS:
        errors.append(diagnostic("enum/verdict", "verdict", repr(verdict)))
    elif mode == "pr-risk-review":
        expected = expected_pr_verdict(receipt)
        if verdict != expected:
            errors.append(diagnostic("verdict/inconsistent", "verdict", f"expected {expected}, got {verdict}"))
    elif verdict == "APPROVED" and isinstance(coverage, dict) and coverage.get("status") != "complete-for-scope":
        errors.append(diagnostic("verdict/approval-requires-complete-scope", "verdict", repr(coverage.get("status"))))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", help="path to review receipt JSON")
    parser.add_argument("--json", dest="json_out", help="optional machine-readable validation receipt")
    args = parser.parse_args()

    path = Path(args.receipt).resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors = [diagnostic("parse/json", str(path), str(exc))]
    else:
        errors = validate_receipt(data)

    result = {
        "receipt_version": 1,
        "status": "pass" if not errors else "fail",
        "stage": "review-receipt-validation",
        "subject": str(path),
        "errors": errors,
        "error_count": len(errors),
    }
    if args.json_out:
        out = Path(args.json_out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
