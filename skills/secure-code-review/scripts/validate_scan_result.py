#!/usr/bin/env python3
"""Validate Secure Code Review scanner JSON using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEVERITIES = ("critical", "high", "medium", "low")
SEVERITY_ORDER = {value: index for index, value in enumerate(SEVERITIES)}
CONFIDENCES = {"confirmed", "likely", "possible"}
SKIP_REASONS = {"symlink", "unsupported-type", "too-large", "read-error"}
REQUIRED_TOP = {"schema_version", "status", "target", "summary", "scan_stats", "skipped", "findings"}
REQUIRED_FINDING = {"id", "path", "line", "severity", "confidence", "rule", "evidence"}
REQUIRED_STATS = {"files_considered", "files_scanned", "files_skipped", "findings"}

RAW_SECRET_PATTERNS = [
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"),
    re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-+/=]{8,}"),
    re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql|amqp)://[^\s:@/]+:[^\s@/]+@"),
]


def add(checks: list[dict], code: str, ok: bool, subject: str, evidence: object) -> None:
    checks.append({
        "code": code,
        "status": "pass" if ok else "fail",
        "subject": subject,
        "evidence": evidence,
        "supported_fixes": [],
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result")
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args()

    source = Path(args.result)
    checks: list[dict] = []

    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
        add(checks, "json/parse", True, str(source), {})
    except Exception as exc:
        add(checks, "json/parse", False, str(source), {"error": str(exc)})
        payload = None

    if isinstance(payload, dict):
        add(checks, "schema/top-fields", REQUIRED_TOP <= set(payload), str(source), {"missing": sorted(REQUIRED_TOP - set(payload))})
        add(checks, "schema/version", payload.get("schema_version") == 1, "schema_version", {"actual": payload.get("schema_version")})
        add(checks, "schema/status", payload.get("status") in {"complete", "partial"}, "status", {"actual": payload.get("status")})

        findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
        skipped = payload.get("skipped") if isinstance(payload.get("skipped"), list) else []
        summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
        stats = payload.get("scan_stats") if isinstance(payload.get("scan_stats"), dict) else {}

        missing_fields = [
            {"index": i, "missing": sorted(REQUIRED_FINDING - set(item))}
            for i, item in enumerate(findings)
            if not isinstance(item, dict) or not REQUIRED_FINDING <= set(item)
        ]
        add(checks, "finding/fields", not missing_fields, "findings", missing_fields[:20])

        bad_enums = [
            {"index": i, "severity": item.get("severity"), "confidence": item.get("confidence")}
            for i, item in enumerate(findings)
            if isinstance(item, dict)
            and (item.get("severity") not in SEVERITY_ORDER or item.get("confidence") not in CONFIDENCES)
        ]
        add(checks, "finding/enums", not bad_enums, "findings", bad_enums[:20])

        ids = [item.get("id") for item in findings if isinstance(item, dict)]
        id_ok = len(ids) == len(set(ids)) and all(isinstance(value, str) and value.startswith("scr-") for value in ids)
        add(checks, "finding/ids", id_ok, "findings", {"count": len(ids), "unique": len(set(ids))})

        canonical = [
            (
                SEVERITY_ORDER.get(item.get("severity"), 99),
                str(item.get("path", "")),
                int(item.get("line", 0) or 0),
                str(item.get("rule", "")),
                str(item.get("id", "")),
            )
            for item in findings if isinstance(item, dict)
        ]
        add(checks, "finding/canonical-order", canonical == sorted(canonical), "findings", {})

        raw_matches = []
        for i, item in enumerate(findings):
            if not isinstance(item, dict):
                continue
            evidence = str(item.get("evidence", ""))
            for pattern in RAW_SECRET_PATTERNS:
                if pattern.search(evidence):
                    raw_matches.append({"index": i, "rule": item.get("rule"), "pattern": pattern.pattern})
        add(checks, "evidence/no-raw-secret-shape", not raw_matches, "findings[].evidence", raw_matches[:20])

        expected_summary = {
            severity: sum(1 for item in findings if isinstance(item, dict) and item.get("severity") == severity)
            for severity in SEVERITIES
        }
        add(checks, "summary/counts", summary == expected_summary, "summary", {"actual": summary, "expected": expected_summary})

        add(checks, "stats/fields", REQUIRED_STATS <= set(stats), "scan_stats", {"missing": sorted(REQUIRED_STATS - set(stats))})
        stats_consistent = (
            isinstance(stats.get("files_considered"), int)
            and isinstance(stats.get("files_scanned"), int)
            and isinstance(stats.get("files_skipped"), int)
            and isinstance(stats.get("findings"), int)
            and stats.get("files_skipped") == len(skipped)
            and stats.get("findings") == len(findings)
            and stats.get("files_considered") == stats.get("files_scanned") + stats.get("files_skipped")
        )
        add(checks, "stats/consistent", stats_consistent, "scan_stats", stats)

        bad_skips = [
            item for item in skipped
            if not isinstance(item, dict)
            or not isinstance(item.get("path"), str)
            or item.get("reason") not in SKIP_REASONS
        ]
        add(checks, "skipped/shape", not bad_skips, "skipped", bad_skips[:20])

        expected_status = "partial" if skipped else "complete"
        add(checks, "status/coverage-consistent", payload.get("status") == expected_status, "status", {"actual": payload.get("status"), "expected": expected_status})

    errors = sum(1 for check in checks if check["status"] == "fail")
    report = {
        "receipt_version": 1,
        "status": "pass" if errors == 0 else "fail",
        "stage": "validation",
        "checks": checks,
        "errors": errors,
        "warnings": 0,
        "metrics": {"checks": len(checks)},
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        Path(args.json_out).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
