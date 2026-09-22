#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ALLOWED_STATUS = {"decided", "undetermined", "blocked", "escalate"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_MATERIALITY = {"low", "medium", "high"}
REQUIRED_ROOT = {"contract_version", "materiality", "decision", "confidence", "evidence_refs", "rationale", "calibration", "next_action"}
ALLOWED_ROOT = REQUIRED_ROOT | {"decision_id"}


def err(errors, code, message):
    errors.append({"code": code, "message": message})


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return [{"code": "DE000", "message": "root must be an object"}]

    missing_root = sorted(REQUIRED_ROOT - set(data))
    if missing_root:
        err(errors, "DE001A", f"missing required root fields: {', '.join(missing_root)}")
    extra = sorted(set(data) - ALLOWED_ROOT)
    if extra:
        err(errors, "DE001", f"unexpected root fields: {', '.join(extra)}")

    if data.get("contract_version") != "decision-engine/1":
        err(errors, "DE002", "contract_version must equal decision-engine/1")

    if "decision_id" in data and data.get("decision_id") is not None and not nonempty_string(data.get("decision_id")):
        err(errors, "DE002A", "decision_id must be null or a trimmed non-empty string")

    materiality = data.get("materiality")
    if materiality not in ALLOWED_MATERIALITY:
        err(errors, "DE003", "materiality must be low, medium, or high")

    decision = data.get("decision")
    if not isinstance(decision, dict):
        err(errors, "DE004", "decision must be an object")
        decision = {}

    dtype = decision.get("type")
    status = decision.get("status")
    if dtype not in {"noul", "choice", "score"}:
        err(errors, "DE005", "decision.type must be noul, choice, or score")
    if status not in ALLOWED_STATUS:
        err(errors, "DE006", "decision.status is invalid")
    if not nonempty_string(decision.get("question")):
        err(errors, "DE007", "decision.question must be a trimmed non-empty string")

    if dtype == "noul":
        required = {"type", "question", "status", "value"}
        missing = sorted(required - set(decision))
        if missing:
            err(errors, "DE009", f"noul missing required fields: {', '.join(missing)}")
        if set(decision) - required:
            err(errors, "DE010", "noul contains unsupported fields")
        value = decision.get("value")
        if status == "decided" and not isinstance(value, bool):
            err(errors, "DE011", "decided noul requires boolean value")
        if status != "decided" and value is not None:
            err(errors, "DE012", "non-decided noul requires null value")

    if dtype == "choice":
        required = {"type", "question", "status", "options", "selected"}
        missing = sorted(required - set(decision))
        if missing:
            err(errors, "DE019", f"choice missing required fields: {', '.join(missing)}")
        if set(decision) - required:
            err(errors, "DE020", "choice contains unsupported fields")
        options = decision.get("options")
        if not isinstance(options, list) or len(options) < 2 or any(not nonempty_string(x) for x in options):
            err(errors, "DE021", "choice.options must contain at least two trimmed non-empty strings")
            options = []
        elif len(set(options)) != len(options):
            err(errors, "DE022", "choice.options must be unique")
        selected = decision.get("selected")
        if status == "decided" and selected not in options:
            err(errors, "DE023", "decided choice.selected must exactly match one option")
        if status != "decided" and selected is not None:
            err(errors, "DE024", "non-decided choice requires null selected")

    if dtype == "score":
        required = {"type", "question", "status", "scale", "score"}
        missing = sorted(required - set(decision))
        if missing:
            err(errors, "DE029", f"score missing required fields: {', '.join(missing)}")
        if set(decision) - required:
            err(errors, "DE030", "score contains unsupported fields")
        scale = decision.get("scale")
        if not isinstance(scale, dict):
            err(errors, "DE031", "score.scale must be an object")
            scale = {}
        else:
            required_scale = {"min", "max", "meaning"}
            missing_scale = sorted(required_scale - set(scale))
            if missing_scale:
                err(errors, "DE031A", f"score.scale missing required fields: {', '.join(missing_scale)}")
            if set(scale) - required_scale:
                err(errors, "DE031B", "score.scale contains unsupported fields")
        low = scale.get("min")
        high = scale.get("max")
        meaning = scale.get("meaning")
        numeric_bounds = finite_number(low) and finite_number(high)
        if not numeric_bounds or low >= high:
            err(errors, "DE032", "score.scale requires finite numeric min < max")
        if not nonempty_string(meaning):
            err(errors, "DE033", "score.scale.meaning must be a trimmed non-empty string")
        score = decision.get("score")
        if status == "decided":
            if not finite_number(score):
                err(errors, "DE034", "decided score requires a finite numeric score")
            elif numeric_bounds and not (low <= score <= high):
                err(errors, "DE035", "score is outside declared bounds")
        elif score is not None:
            err(errors, "DE036", "non-decided score requires null score")

    confidence = data.get("confidence")
    if not isinstance(confidence, dict):
        err(errors, "DE040", "confidence must be an object")
        confidence = {}
    else:
        required_conf = {"level", "basis"}
        missing_conf = sorted(required_conf - set(confidence))
        if missing_conf:
            err(errors, "DE040A", f"confidence missing required fields: {', '.join(missing_conf)}")
        if set(confidence) - required_conf:
            err(errors, "DE040B", "confidence contains unsupported fields")
    level = confidence.get("level")
    if level not in ALLOWED_CONFIDENCE:
        err(errors, "DE041", "confidence.level must be low, medium, or high")
    if not nonempty_string(confidence.get("basis")):
        err(errors, "DE042", "confidence.basis must be a trimmed non-empty string")
    if status != "decided" and level not in {None, "low"}:
        err(errors, "DE043", "non-decided status must use low confidence")
    if materiality == "high" and status == "decided" and level == "low":
        err(errors, "DE044", "high-materiality decisions cannot be decided with low confidence")

    evidence_refs = data.get("evidence_refs")
    if not isinstance(evidence_refs, list) or any(not nonempty_string(x) for x in evidence_refs):
        err(errors, "DE050", "evidence_refs must be an array of trimmed non-empty strings")
        evidence_refs = []
    elif len(set(evidence_refs)) != len(evidence_refs):
        err(errors, "DE051", "evidence_refs must be unique")
    if materiality == "high" and status == "decided" and not evidence_refs:
        err(errors, "DE052", "high-materiality decided result requires evidence_refs")

    if not nonempty_string(data.get("rationale")):
        err(errors, "DE060", "rationale must be a trimmed non-empty string")

    calibration = data.get("calibration")
    if not isinstance(calibration, dict):
        err(errors, "DE070", "calibration must be an object")
    else:
        kind = calibration.get("kind")
        if kind == "none":
            if set(calibration) != {"kind"}:
                err(errors, "DE071", "calibration kind none cannot include probability fields")
        elif kind == "calibrated_probability":
            allowed = {"kind", "value", "source", "calibration_ref"}
            if set(calibration) != allowed:
                err(errors, "DE072", "calibrated_probability requires exactly kind,value,source,calibration_ref")
            value = calibration.get("value")
            if not finite_number(value) or not (0 <= value <= 1):
                err(errors, "DE073", "calibrated probability value must be finite within 0..1")
            for field in ("source", "calibration_ref"):
                if not nonempty_string(calibration.get(field)):
                    err(errors, "DE074", f"calibrated probability {field} must be a trimmed non-empty string")
        else:
            err(errors, "DE075", "calibration.kind must be none or calibrated_probability")

    next_action = data.get("next_action")
    if next_action is not None and not nonempty_string(next_action):
        err(errors, "DE080", "next_action must be null or a trimmed non-empty string")
    if status in {"blocked", "escalate"} and next_action is None:
        err(errors, "DE081", "blocked/escalate status requires next_action")

    return errors


def main():
    ap = argparse.ArgumentParser(description="Validate one decision-engine/1 envelope.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except Exception as exc:
        payload = {"status": "fail", "errors": [{"code": "DEJSON", "message": str(exc)}]}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    errors = validate(data)
    payload = {"status": "pass" if not errors else "fail", "errors": errors}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
