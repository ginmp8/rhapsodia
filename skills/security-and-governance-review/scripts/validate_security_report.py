#!/usr/bin/env python3
"""Validate the machine-readable security review contract using stdlib only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _security_common import CLASSIFICATIONS, CONFIDENCES, REPORT_VERSION, RUBRIC_VERSION, SEVERITIES, contains_secret_like

REQUIRED_TOP = {"report_version", "rubric_version", "target", "mode", "review_status", "evidence_snapshot", "critical_evidence_gaps", "findings", "commands", "evidence_layers", "limitations"}
REQUIRED_FINDING = {"id", "classification", "severity", "confidence", "location", "evidence", "risk", "recommendation", "validation", "residual_risk"}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP - set(data))
    if missing:
        errors.append("missing top-level fields: " + ", ".join(missing))
    if data.get("report_version") != REPORT_VERSION:
        errors.append(f"report_version must be {REPORT_VERSION}")
    if data.get("rubric_version") != RUBRIC_VERSION:
        errors.append(f"rubric_version must be {RUBRIC_VERSION}")
    if data.get("review_status") not in {"complete", "partial", "blocked-critical-evidence"}:
        errors.append("invalid review_status")
    gaps = data.get("critical_evidence_gaps", [])
    if gaps and data.get("review_status") != "blocked-critical-evidence":
        errors.append("critical evidence gaps require review_status=blocked-critical-evidence (fail-closed)")
    layers = data.get("evidence_layers", {})
    if set(layers) != {"structural", "behavioral", "runtime", "external_current"}:
        errors.append("evidence_layers must contain structural, behavioral, runtime, external_current")
    findings = data.get("findings", [])
    ids: set[str] = set()
    for i, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"findings[{i}] must be an object")
            continue
        fm = REQUIRED_FINDING - set(finding)
        if fm:
            errors.append(f"findings[{i}] missing: {', '.join(sorted(fm))}")
        if finding.get("classification") not in CLASSIFICATIONS:
            errors.append(f"findings[{i}] invalid classification")
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"findings[{i}] invalid severity")
        if finding.get("confidence") not in CONFIDENCES:
            errors.append(f"findings[{i}] invalid confidence")
        fid = finding.get("id")
        if fid in ids:
            errors.append(f"duplicate finding id: {fid}")
        ids.add(fid)
        evidence = finding.get("evidence")
        if not isinstance(evidence, dict) or not {"kind", "source", "summary", "source_identity"} <= set(evidence or {}):
            errors.append(f"findings[{i}] evidence must map kind/source/summary/source_identity")
    for text in strings(data):
        if contains_secret_like(text):
            errors.append("report contains an unredacted secret-like value")
            break
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--json")
    args = ap.parse_args()
    try:
        data = json.loads(Path(args.report).read_text(encoding="utf-8"))
    except Exception as exc:
        result = {"status": "fail", "errors": [f"invalid JSON: {exc}"]}
    else:
        errors = validate(data)
        result = {"status": "fail" if errors else "pass", "errors": errors}
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        Path(args.json).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
