#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ALLOWED_STATUS = {"decided", "undetermined", "blocked", "escalate"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_MATERIALITY = {"low", "medium", "high"}
REQUIRED_ROOT = {
    "contract_version",
    "materiality",
    "decision",
    "confidence",
    "evidence_refs",
    "rationale",
    "calibration",
    "next_action",
}
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

    if data.get("contract_version") != "decision-engine/2":
        err(errors, "DE002", "contract_version must equal decision-engine/2")

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
    if dtype not in {"binary", "choice", "score"}:
        err(errors, "DE005", "decision.type must be binary, choice, or score")
    if status not in ALLOWED_STATUS:
        err(errors, "DE006", "decision.status is invalid")
    if not nonempty_string(decision.get("question")):
        err(errors, "DE007", "decision.question must be a trimmed non-empty string")

    if dtype == "binary":
        required = {"type", "question", "status", "value"}
        missing = sorted(required - set(decision))
        if missing:
            err(errors, "DE009", f"binary missing required fields: {', '.join(missing)}")
        if set(decision) - required:
            err(errors, "DE010", "binary contains unsupported fields")
        value = decision.get("value")
        if status == "decided" and not isinstance(value, bool):
            err(errors, "DE011", "decided binary requires boolean value")
        if status != "decided" and value is not None:
            err(errors, "DE012", "non-decided binary requires null value")

    if dtype == "choice":
        required = {"type", "question", "status", "options", "options_exhaustive", "selected"}
        allowed = required | {"option_criteria"}
        missing = sorted(required - set(decision))
        if missing:
            err(errors, "DE019", f"choice missing required fields: {', '.join(missing)}")
        if set(decision) - allowed:
            err(errors, "DE020", "choice contains unsupported fields")
        options = decision.get("options")
        if not isinstance(options, list) or len(options) < 2 or any(not nonempty_string(x) for x in options):
            err(errors, "DE021", "choice.options must contain at least two trimmed non-empty strings")
            options = []
        elif len(set(options)) != len(options):
            err(errors, "DE022", "choice.options must be unique")
        selected = decision.get("selected")
        if status == "decided" and selected not in options:
            err(errors, "DE023", "decided choice.selected must exactly match one supplied option")
        if status != "decided" and selected is not None:
            err(errors, "DE024", "non-decided choice requires null selected")
        if not isinstance(decision.get("options_exhaustive"), bool):
            err(errors, "DE025", "choice.options_exhaustive must be boolean")
        if "option_criteria" in decision:
            criteria = decision.get("option_criteria")
            if not isinstance(criteria, dict):
                err(errors, "DE026", "choice.option_criteria must be an object when supplied")
            else:
                invalid = [
                    key for key, value in criteria.items()
                    if not nonempty_string(key) or key not in options or not nonempty_string(value)
                ]
                if invalid:
                    err(errors, "DE027", "choice.option_criteria keys must be supplied options with trimmed non-empty descriptions")

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
        kind = scale.get("kind")
        if kind not in {"ordinal", "numeric"}:
            err(errors, "DE032", "score.scale.kind must be ordinal or numeric")

        if kind == "ordinal":
            allowed = {"kind", "levels"}
            if set(scale) - allowed:
                err(errors, "DE037", "ordinal scale contains unsupported fields")
            levels = scale.get("levels")
            if (
                not isinstance(levels, list)
                or len(levels) < 2
                or any(not nonempty_string(x) for x in levels)
                or len(set(levels)) != len(levels)
            ):
                err(errors, "DE033", "ordinal scale.levels must contain at least two unique trimmed non-empty descriptions")
                levels = []
            score = decision.get("score")
            if status == "decided":
                if not isinstance(score, int) or isinstance(score, bool):
                    err(errors, "DE034", "decided ordinal score must be an integer level index")
                elif not levels or score < 0 or score >= len(levels):
                    err(errors, "DE035", "decided ordinal score must index one declared level")

        if kind == "numeric":
            required_scale = {"kind", "min", "max", "meaning"}
            allowed_scale = required_scale | {"unit"}
            missing_scale = sorted(required_scale - set(scale))
            if missing_scale:
                err(errors, "DE036", f"numeric scale missing required fields: {', '.join(missing_scale)}")
            if set(scale) - allowed_scale:
                err(errors, "DE037", "numeric scale contains unsupported fields")
            min_v, max_v = scale.get("min"), scale.get("max")
            if not finite_number(min_v) or not finite_number(max_v) or not min_v < max_v:
                err(errors, "DE038", "numeric scale requires finite min < max")
            if not nonempty_string(scale.get("meaning")):
                err(errors, "DE039", "numeric scale.meaning must be a trimmed non-empty string")
            if "unit" in scale and scale.get("unit") is not None and not nonempty_string(scale.get("unit")):
                err(errors, "DE039", "numeric scale.unit must be null or a trimmed non-empty string")
            score = decision.get("score")
            if status == "decided":
                if not finite_number(score):
                    err(errors, "DE040", "decided numeric score must be a finite number")
                elif finite_number(min_v) and finite_number(max_v) and not (min_v <= score <= max_v):
                    err(errors, "DE041", "decided numeric score must lie within the inclusive scale bounds")

        if status != "decided" and decision.get("score") is not None:
            err(errors, "DE042", "non-decided score requires null score")

    confidence = data.get("confidence")
    if status == "decided":
        if not isinstance(confidence, dict):
            err(errors, "DE053", "decided result requires a confidence object")
        else:
            if set(confidence) != {"level", "basis"}:
                err(errors, "DE050", "confidence must contain exactly level and basis")
            if confidence.get("level") not in ALLOWED_CONFIDENCE:
                err(errors, "DE051", "confidence.level must be low, medium, or high")
            if not nonempty_string(confidence.get("basis")):
                err(errors, "DE052", "confidence.basis must be a trimmed non-empty string")
            if materiality == "high" and confidence.get("level") == "low":
                err(errors, "DE055", "high-materiality decided result cannot use low confidence")
    else:
        if confidence is not None:
            err(errors, "DE054", "non-decided result requires confidence to be null")

    evidence = data.get("evidence_refs")
    if not isinstance(evidence, list) or any(not nonempty_string(x) for x in evidence):
        err(errors, "DE060", "evidence_refs must be a list of trimmed non-empty strings")
        evidence = []
    elif len(set(evidence)) != len(evidence):
        err(errors, "DE061", "evidence_refs must be unique")
    if status == "decided" and materiality == "high" and not evidence:
        err(errors, "DE062", "high-materiality decided result requires at least one evidence reference")

    if not nonempty_string(data.get("rationale")):
        err(errors, "DE070", "rationale must be a trimmed non-empty string")

    calibration = data.get("calibration")
    if not isinstance(calibration, dict):
        err(errors, "DE080", "calibration must be an object")
        calibration = {}
    kind = calibration.get("kind")
    if kind == "none":
        if set(calibration) != {"kind"}:
            err(errors, "DE081", "calibration kind none contains unsupported fields")
    elif kind == "calibrated_probability":
        required = {"kind", "value", "source", "calibration_ref"}
        if set(calibration) != required:
            err(errors, "DE082", "calibrated_probability must contain exactly kind, value, source, and calibration_ref")
        value = calibration.get("value")
        if not finite_number(value) or not 0 <= value <= 1:
            err(errors, "DE083", "calibrated probability value must be a finite number from 0 to 1")
        if not nonempty_string(calibration.get("source")) or not nonempty_string(calibration.get("calibration_ref")):
            err(errors, "DE084", "calibrated probability requires non-empty source and calibration_ref")
    else:
        err(errors, "DE085", "calibration.kind must be none or calibrated_probability")
    if status != "decided" and kind == "calibrated_probability":
        err(errors, "DE086", "non-decided result cannot emit calibrated_probability")

    next_action = data.get("next_action")
    if next_action is not None and not nonempty_string(next_action):
        err(errors, "DE090", "next_action must be null or a trimmed non-empty string")
    if status in {"blocked", "escalate"} and not nonempty_string(next_action):
        err(errors, "DE091", f"{status} requires a concrete next_action")

    return errors


def main():
    ap = argparse.ArgumentParser(description="Validate one decision-engine/2 envelope.")
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
