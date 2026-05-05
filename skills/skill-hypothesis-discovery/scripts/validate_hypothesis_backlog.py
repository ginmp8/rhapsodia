#!/usr/bin/env python3
"""Validate and rank a skill-hypothesis-discovery JSON backlog."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

RECOMMENDATIONS = {"test-now", "defer", "reject", "gather-evidence"}
EVIDENCE_STATUSES = {"measured", "supplied", "derived", "planned", "mixed", "insufficient", "unknown"}
MODES = {"backlog-discovery", "deep-discovery", "closure-discovery", "evidence-gap-review"}
AREAS = {
    "activation",
    "ambiguity",
    "output",
    "architecture",
    "resource-integration",
    "documentation",
    "scripts",
    "security",
    "validation",
    "packaging",
    "token",
    "behavioral",
    "consistency",
    "evidence",
    "other",
}
REQUIRED_TOP = {"target", "mode", "evidence_status", "recommendation", "hypotheses"}
REQUIRED_HYPOTHESIS = {
    "id",
    "title",
    "statement",
    "target_area",
    "evidence",
    "expected_effect",
    "validation_method",
    "impact",
    "confidence",
    "testability",
    "risk",
    "cost",
    "recommendation",
}


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"failed to read JSON: {path}: {exc}") from exc


def score(item: dict[str, Any]) -> int:
    return int(item["impact"]) + int(item["confidence"]) + int(item["testability"]) - int(item["risk"]) - math.ceil(int(item["cost"]) / 2)


def check_int_range(value: Any, field: str, errors: list[str], item_id: str) -> None:
    if not isinstance(value, int) or value < 1 or value > 5:
        errors.append(f"{item_id}: {field} must be integer 1..5")


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["root must be an object"], "warnings": [], "ranked_ids": []}

    missing = sorted(REQUIRED_TOP - set(data))
    if missing:
        errors.append(f"missing top-level fields: {missing}")

    mode = data.get("mode")
    if mode is not None and mode not in MODES:
        warnings.append(f"unknown mode: {mode}")
    evidence_status = data.get("evidence_status")
    if evidence_status is not None and evidence_status not in EVIDENCE_STATUSES:
        warnings.append(f"unknown evidence_status: {evidence_status}")

    hypotheses = data.get("hypotheses")
    if not isinstance(hypotheses, list):
        errors.append("hypotheses must be a list")
        hypotheses = []
    elif len(hypotheses) == 0 and data.get("recommendation") != "no-mutation-recommended":
        warnings.append("no hypotheses provided")

    seen: set[str] = set()
    ranked: list[tuple[str, int]] = []
    for i, item in enumerate(hypotheses):
        item_id = f"hypothesis[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{item_id}: must be an object")
            continue
        hid = item.get("id")
        if isinstance(hid, str) and hid:
            item_id = hid
            if hid in seen:
                errors.append(f"duplicate hypothesis id: {hid}")
            seen.add(hid)
        else:
            errors.append(f"hypothesis[{i}]: id is required")

        missing_h = sorted(REQUIRED_HYPOTHESIS - set(item))
        if missing_h:
            errors.append(f"{item_id}: missing fields: {missing_h}")
            continue

        for field in ("impact", "confidence", "testability", "risk", "cost"):
            check_int_range(item.get(field), field, errors, item_id)
        if item.get("recommendation") not in RECOMMENDATIONS:
            errors.append(f"{item_id}: recommendation must be one of {sorted(RECOMMENDATIONS)}")
        if item.get("target_area") not in AREAS:
            warnings.append(f"{item_id}: target_area not in known set: {item.get('target_area')}")
        for text_field in ("title", "statement", "evidence", "expected_effect", "validation_method"):
            value = item.get(text_field)
            if not isinstance(value, str) or len(value.strip()) < 8:
                warnings.append(f"{item_id}: {text_field} is very short or empty")

        if not errors:
            ranked.append((str(hid), score(item)))

    selected = data.get("selected_for_testing", [])
    if selected is None:
        selected = []
    if not isinstance(selected, list):
        errors.append("selected_for_testing must be a list when present")
        selected = []
    else:
        unknown_selected = [x for x in selected if x not in seen]
        if unknown_selected:
            errors.append(f"selected_for_testing contains unknown ids: {unknown_selected}")
        if len(selected) > 5:
            warnings.append("selected_for_testing has more than 5 items; consider narrowing")

    if mode == "backlog-discovery" and len(hypotheses) > 0 and not (3 <= len(hypotheses) <= 12):
        warnings.append("backlog-discovery usually contains 5-10 hypotheses")
    if mode == "deep-discovery" and len(hypotheses) > 12:
        warnings.append("deep-discovery output should be deduped, not a raw long list")

    ranked_ids = [hid for hid, _ in sorted(ranked, key=lambda pair: (-pair[1], pair[0]))]
    status = "fail" if errors else "pass" if not warnings else "pass-with-warnings"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "ranked_ids": ranked_ids,
        "scores": {hid: sc for hid, sc in sorted(ranked, key=lambda pair: pair[0])},
        "hypothesis_count": len(hypotheses),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and rank a hypothesis backlog JSON file.")
    parser.add_argument("--input", required=True, help="Path to backlog JSON")
    parser.add_argument("--json-output", help="Optional path to write validation result JSON")
    args = parser.parse_args(argv)

    result = validate(read_json(Path(args.input)))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"pass", "pass-with-warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
