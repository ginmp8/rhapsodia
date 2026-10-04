#!/usr/bin/env python3
"""Validate the stable core of Skill Change Gate Result v1."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STATUSES = {"pass", "pass-with-warnings", "fail", "insufficient-evidence"}
DECISIONS = {"accept", "reject", "repair-before-accept", "gather-evidence", "advisory-only"}
DELTAS = {"introduced", "worsened", "preexisting-unchanged", "improved", "resolved", "unknown"}


def validate(data: object, expected_candidate_sha256: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["result:not-object"]
    if data.get("result_version") != 1:
        errors.append("result_version:unsupported")
    subject = data.get("subject")
    if not isinstance(subject, dict):
        errors.append("subject:invalid")
    else:
        candidate = subject.get("candidate_tree_sha256")
        if not isinstance(candidate, str) or not SHA256_RE.fullmatch(candidate):
            errors.append("subject.candidate_tree_sha256:invalid")
        elif expected_candidate_sha256 and candidate != expected_candidate_sha256.lower():
            errors.append("subject.candidate_tree_sha256:mismatch")
    gate = data.get("gate")
    if not isinstance(gate, dict):
        errors.append("gate:invalid")
    else:
        for key in ("mode", "policy", "portability_profile"):
            if not isinstance(gate.get(key), str) or not gate.get(key):
                errors.append(f"gate.{key}:invalid")
    if data.get("status") not in STATUSES:
        errors.append("status:invalid")
    if data.get("decision_for_caller") not in DECISIONS:
        errors.append("decision_for_caller:invalid")
    if not isinstance(data.get("evidence"), list):
        errors.append("evidence:invalid")
    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("findings:invalid")
    else:
        for i, finding in enumerate(findings):
            if not isinstance(finding, dict):
                errors.append(f"findings[{i}]:invalid")
                continue
            for key in ("severity", "area", "origin", "rule_origin", "finding", "decision_impact"):
                if not isinstance(finding.get(key), str) or not finding.get(key):
                    errors.append(f"findings[{i}].{key}:invalid")
            if finding.get("regression_delta") not in DELTAS:
                errors.append(f"findings[{i}].regression_delta:invalid")
    if not isinstance(data.get("portability"), dict):
        errors.append("portability:invalid")
    return sorted(set(errors))


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Validate Skill Change Gate Result v1")
    p.add_argument("result")
    p.add_argument("--expected-candidate-sha256")
    p.add_argument("--json", dest="json_out")
    a = p.parse_args(argv)
    try:
        data = json.loads(Path(a.result).read_text(encoding="utf-8"))
        errors = validate(data, a.expected_candidate_sha256)
    except Exception as exc:
        errors = [f"result:unreadable:{exc}"]
    report = {"result_version": 1, "status": "pass" if not errors else "fail", "errors": errors}
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if a.json_out:
        Path(a.json_out).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
