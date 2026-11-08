#!/usr/bin/env python3
"""Validate a spec-audit/v1 receipt's structure and internal consistency.

This checks report hygiene, not the truth of source-code claims or test results.
Standard-library only. Does not execute target code or access the network.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

STATUSES = {"PASS", "PARTIAL", "FAIL", "UNVERIFIED", "NOT_APPLICABLE"}
VERDICTS = {"COMPLIANT", "PARTIALLY_COMPLIANT", "NON_COMPLIANT", "INCONCLUSIVE"}
PROOF_KINDS = {"executed_test", "runtime_observation", "static_proof", "test_defined"}
PROOF_RESULTS = {"passed", "failed", "not_run", "inconclusive"}
SEVERITIES = {"critical", "high", "medium", "low"}


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def validate(document):
    errors = []
    if not isinstance(document, dict):
        return ["Root must be a JSON object."], {}
    if document.get("schema_version") != "spec-audit/v1":
        errors.append("schema_version must be spec-audit/v1.")
    scope = document.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope must be an object.")
        scope = {}
    for key in ("repository", "target", "base_sha", "head_sha", "snapshot_time_utc"):
        if not nonblank(scope.get(key)):
            errors.append(f"scope.{key} must be a nonempty string.")
    if not isinstance(scope.get("partial"), bool):
        errors.append("scope.partial must be a boolean.")

    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty list.")
        sources = []
    for i, source in enumerate(sources):
        if not isinstance(source, dict) or not nonblank(source.get("locator")):
            errors.append(f"sources[{i}].locator must be a nonempty string.")
            continue
        if not isinstance(source.get("available"), bool):
            errors.append(f"sources[{i}].available must be boolean.")
        if not nonblank(source.get("revision")):
            errors.append(f"sources[{i}].revision must identify a version or retrieval time.")

    requirements = document.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must be a nonempty list.")
        requirements = []
    findings = document.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be a list.")
        findings = []
    if not isinstance(document.get("limitations"), list):
        errors.append("limitations must be a list.")
    verdict = document.get("verdict")
    if verdict not in VERDICTS:
        errors.append("verdict must be a recognized conformance verdict.")

    finding_ids = set()
    high_or_critical = False
    for i, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"findings[{i}] must be an object.")
            continue
        fid = finding.get("id")
        if not nonblank(fid):
            errors.append(f"findings[{i}].id must be nonempty.")
        elif fid in finding_ids:
            errors.append(f"Duplicate finding ID: {fid}.")
        else:
            finding_ids.add(fid)
        severity = finding.get("severity")
        if severity not in SEVERITIES:
            errors.append(f"findings[{i}].severity must be critical/high/medium/low.")
        if severity in ("critical", "high"):
            high_or_critical = True
        for key in ("expected", "actual", "recommendation", "verification"):
            if not nonblank(finding.get(key)):
                errors.append(f"findings[{i}].{key} must be nonempty.")
        if not isinstance(finding.get("evidence"), list) or not finding["evidence"]:
            errors.append(f"findings[{i}].evidence must be a nonempty list.")
        if not isinstance(finding.get("requirement_ids"), list):
            errors.append(f"findings[{i}].requirement_ids must be a list.")

    seen = set()
    counts = Counter()
    for i, req in enumerate(requirements):
        if not isinstance(req, dict):
            errors.append(f"requirements[{i}] must be an object.")
            continue
        rid = req.get("id")
        if not nonblank(rid):
            errors.append(f"requirements[{i}].id must be nonempty.")
        elif rid in seen:
            errors.append(f"Duplicate requirement ID: {rid}.")
        else:
            seen.add(rid)
        for key in ("criterion", "source_locator"):
            if not nonblank(req.get(key)):
                errors.append(f"{rid or i}.{key} must be nonempty.")
        status = req.get("status")
        if status not in STATUSES:
            errors.append(f"{rid or i}.status is invalid.")
        else:
            counts[status] += 1
        evidence = req.get("implementation_evidence")
        if not isinstance(evidence, list):
            errors.append(f"{rid or i}.implementation_evidence must be a list.")
            evidence = []
        for j, item in enumerate(evidence):
            if not isinstance(item, dict) or not nonblank(item.get("locator")) or not nonblank(item.get("claim")):
                errors.append(f"{rid or i}.implementation_evidence[{j}] needs locator and claim.")
        proof = req.get("proof")
        if not isinstance(proof, list):
            errors.append(f"{rid or i}.proof must be a list.")
            proof = []
        has_passing_proof = False
        for j, item in enumerate(proof):
            if not isinstance(item, dict):
                errors.append(f"{rid or i}.proof[{j}] must be an object.")
                continue
            kind, outcome = item.get("kind"), item.get("result")
            if kind not in PROOF_KINDS or outcome not in PROOF_RESULTS or not nonblank(item.get("locator")):
                errors.append(f"{rid or i}.proof[{j}] needs recognized kind/result and locator.")
            if kind in ("executed_test", "runtime_observation", "static_proof") and outcome == "passed" and nonblank(item.get("locator")):
                has_passing_proof = True
        explanation = req.get("explanation")
        if status in ("PARTIAL", "FAIL", "UNVERIFIED", "NOT_APPLICABLE") and not nonblank(explanation):
            errors.append(f"{rid or i}.explanation is required for status {status}.")
        if status == "PASS" and (not evidence or not has_passing_proof):
            errors.append(f"{rid or i} marked PASS without implementation evidence and independent passing proof.")
        refs = req.get("finding_ids")
        if not isinstance(refs, list):
            errors.append(f"{rid or i}.finding_ids must be a list.")
        else:
            for fid in refs:
                if fid not in finding_ids:
                    errors.append(f"{rid or i} references unknown finding: {fid}.")
            if status in ("PARTIAL", "FAIL") and not refs:
                errors.append(f"{rid or i} marked {status} without an actionable finding.")

    for i, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        for rid in finding.get("requirement_ids", []):
            if rid not in seen:
                errors.append(f"findings[{i}] references unknown requirement: {rid}.")

    if verdict == "COMPLIANT":
        if scope.get("partial") is True:
            errors.append("COMPLIANT cannot be issued for a partial scope.")
        if any(req.get("status") not in ("PASS", "NOT_APPLICABLE") for req in requirements if isinstance(req, dict)):
            errors.append("COMPLIANT cannot coexist with PARTIAL, FAIL, or UNVERIFIED requirements.")
        if any(source.get("available") is False for source in sources if isinstance(source, dict)):
            errors.append("COMPLIANT cannot coexist with an unavailable source.")
        if high_or_critical:
            errors.append("COMPLIANT cannot coexist with high or critical unresolved findings.")
    if verdict == "NON_COMPLIANT" and counts["FAIL"] == 0 and not high_or_critical:
        errors.append("NON_COMPLIANT needs a failed requirement or high/critical finding.")

    stats = {
        "applicable": sum(counts[s] for s in ("PASS", "PARTIAL", "FAIL", "UNVERIFIED")),
        "pass": counts["PASS"], "partial": counts["PARTIAL"],
        "fail": counts["FAIL"], "unverified": counts["UNVERIFIED"],
        "not_applicable": counts["NOT_APPLICABLE"],
    }
    return errors, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Path to a spec-audit/v1 JSON receipt")
    args = parser.parse_args()
    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Cannot read report: {exc}", file=sys.stderr)
        return 2
    errors, stats = validate(data)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(json.dumps({"valid": True, "counts": stats}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
