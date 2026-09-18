#!/usr/bin/env python3
"""Validate the Skill Booster reproducibility-routing decision record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STATES = {"invoke-audit", "invoke-apply", "not-applicable", "blocked", "unavailable"}
MODES = {"audit-only", "apply", "none"}
SPECIALIST_STATUSES = {"invoked", "blocked", "unavailable", "not-applicable"}
OWNERS = {"skill-improver", "reproducibility-engineer", "none"}


def validate(data: object) -> dict:
    errors: list[dict] = []

    def add(code: str, subject: str, evidence: str, fix: str) -> None:
        errors.append({
            "code": code,
            "severity": "error",
            "subject": subject,
            "evidence": evidence,
            "supported_fixes": [fix],
        })

    if not isinstance(data, dict):
        add("RPD_NOT_OBJECT", "decision", "root value is not an object", "use a JSON object")
        return {"status": "fail", "diagnostics": errors}

    if data.get("decision_version") != 1:
        add("RPD_VERSION", "decision_version", repr(data.get("decision_version")), "set decision_version to 1")

    target = data.get("target")
    if not isinstance(target, str) or not target.strip():
        add("RPD_TARGET", "target", repr(target), "provide a non-empty target identity")

    state = data.get("state")
    if state not in STATES:
        add("RPD_STATE", "state", repr(state), f"use one of {sorted(STATES)}")

    mode = data.get("selected_mode")
    if mode not in MODES:
        add("RPD_MODE", "selected_mode", repr(mode), f"use one of {sorted(MODES)}")

    specialist = data.get("specialist_status")
    if specialist not in SPECIALIST_STATUSES:
        add("RPD_SPECIALIST_STATUS", "specialist_status", repr(specialist), f"use one of {sorted(SPECIALIST_STATUSES)}")

    owner = data.get("downstream_owner")
    if owner not in OWNERS:
        add("RPD_OWNER", "downstream_owner", repr(owner), f"use one of {sorted(OWNERS)}")

    rationale = data.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        add("RPD_RATIONALE", "rationale", repr(rationale), "record the evidence-based routing rationale")

    signals = data.get("material_signals")
    if not isinstance(signals, list):
        add("RPD_SIGNALS", "material_signals", repr(signals), "use a list; it may be empty only for not-applicable")
        signals = []
    else:
        for index, signal in enumerate(signals):
            if not isinstance(signal, dict) or not signal.get("id") or not signal.get("evidence"):
                add("RPD_SIGNAL_SHAPE", f"material_signals[{index}]", repr(signal), "provide id and evidence")

    if state == "invoke-audit":
        if mode != "audit-only":
            add("RPD_ROUTE_MODE", "selected_mode", repr(mode), "invoke-audit requires audit-only")
        if specialist != "invoked":
            add("RPD_ROUTE_INVOCATION", "specialist_status", repr(specialist), "invoke the specialist or use blocked/unavailable state")
        if owner != "skill-improver":
            add("RPD_ROUTE_OWNER", "downstream_owner", repr(owner), "audit findings normally flow to skill-improver through hypothesis discovery")
        if not signals:
            add("RPD_ROUTE_EVIDENCE", "material_signals", "empty", "record at least one material reproducibility signal")

    if state == "invoke-apply":
        if mode != "apply":
            add("RPD_ROUTE_MODE", "selected_mode", repr(mode), "invoke-apply requires apply")
        if specialist != "invoked":
            add("RPD_ROUTE_INVOCATION", "specialist_status", repr(specialist), "invoke the specialist or use blocked/unavailable state")
        if owner != "reproducibility-engineer":
            add("RPD_ROUTE_OWNER", "downstream_owner", repr(owner), "apply mode makes reproducibility-engineer owner of the bounded batch")
        if not signals:
            add("RPD_ROUTE_EVIDENCE", "material_signals", "empty", "record at least one material reproducibility signal")

    if state == "not-applicable":
        if mode != "none" or specialist != "not-applicable" or owner != "none":
            add("RPD_NOT_APPLICABLE_COMBINATION", "routing", f"mode={mode}, specialist={specialist}, owner={owner}", "use none/not-applicable/none")
        if signals:
            add("RPD_NOT_APPLICABLE_SIGNALS", "material_signals", "non-empty", "remove material signals or choose an applicable route")

    if state == "blocked":
        if mode != "none" or specialist != "blocked" or owner != "none":
            add("RPD_BLOCKED_COMBINATION", "routing", f"mode={mode}, specialist={specialist}, owner={owner}", "use none/blocked/none")
        if not signals:
            add("RPD_BLOCKED_EVIDENCE", "material_signals", "empty", "record why reproducibility work is materially applicable before the blocker")

    if state == "unavailable":
        if mode != "none" or specialist != "unavailable" or owner != "none":
            add("RPD_UNAVAILABLE_COMBINATION", "routing", f"mode={mode}, specialist={specialist}, owner={owner}", "use none/unavailable/none")
        if not signals:
            add("RPD_UNAVAILABLE_EVIDENCE", "material_signals", "empty", "record why the specialist would have been applicable")

    return {"status": "fail" if errors else "pass", "diagnostics": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a reproducibility routing decision JSON file.")
    parser.add_argument("decision")
    parser.add_argument("--json", dest="json_output")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.decision).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {
            "status": "fail",
            "diagnostics": [{
                "code": "RPD_READ_ERROR",
                "severity": "error",
                "subject": args.decision,
                "evidence": str(exc),
                "supported_fixes": ["provide a readable valid JSON decision file"],
            }],
        }

    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json_output:
        Path(args.json_output).write_text(text + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
