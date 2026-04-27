#!/usr/bin/env python3
"""Validate the structure and evidence hygiene of a skill benchmark report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = [
    "executive summary",
    "scorecard",
    "gate evaluation",
    "static structure inventory",
    "behavioral metrics",
    "scenario suite",
    "evidence-based findings",
    "top prioritized improvements",
    "risks if used as-is",
    "suggested improved description",
    "suggested ideal file structure",
    "verdict",
]

SCAFFOLD_MARKERS = [
    re.compile(r"\[" + "TO" + "DO", re.IGNORECASE),
    re.compile(r"\b" + "TO" + "DO" + r"\s*:", re.IGNORECASE),
    re.compile(r"replace with " + "actual", re.IGNORECASE),
    re.compile(r"this is a " + "placeholder", re.IGNORECASE),
]

VERDICT_RE = re.compile(r"\b(approve|approve with reservations|reject)\b", re.IGNORECASE)
SCORE_RE = re.compile(r"\b(\d{1,3})\s*/\s*100\b")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def normalize_heading(line: str) -> str | None:
    match = re.match(r"^#{1,6}\s+(.*)$", line.strip())
    if not match:
        return None
    text = match.group(1).strip().lower()
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"[`*_]+", "", text)
    return text


def find_sections(text: str) -> set[str]:
    sections: set[str] = set()
    for line in text.splitlines():
        heading = normalize_heading(line)
        if heading:
            sections.add(heading)
    return sections


def scan_markers(text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in SCAFFOLD_MARKERS):
            hits.append({"line": line_no, "text": line.strip()[:160]})
    return hits


def validate_report(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        return {"status": "fail", "errors": [f"report file not found: {path}"], "warnings": [], "checks": {}}

    text = read_text(path)
    lower = text.lower()
    sections = find_sections(text)
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in sections]
    if missing_sections:
        errors.append("missing required sections: " + ", ".join(missing_sections))

    marker_hits = scan_markers(text)
    if marker_hits:
        errors.append(f"unresolved scaffold markers found: {len(marker_hits)}")

    scores = [int(match.group(1)) for match in SCORE_RE.finditer(text)]
    if not any(0 <= score <= 100 for score in scores):
        errors.append("no score on a 0 to 100 scale found")

    if not VERDICT_RE.search(text):
        errors.append("no benchmark verdict found")

    if "not measured" not in lower and "measured" not in lower:
        warnings.append("behavioral measurement status is not explicit")

    scenario_keywords = ["should activate", "should not activate", "ambiguous", "edge case"]
    missing_scenario_keywords = [keyword for keyword in scenario_keywords if keyword not in lower]
    if missing_scenario_keywords:
        warnings.append("scenario category labels missing or renamed: " + ", ".join(missing_scenario_keywords))

    checks = {
        "required_sections_present": not missing_sections,
        "scaffold_marker_count": len(marker_hits),
        "score_values_found": scores[:20],
        "verdict_present": bool(VERDICT_RE.search(text)),
        "measurement_status_explicit": "not measured" in lower or "measured" in lower,
        "scenario_category_labels_present": not missing_scenario_keywords,
    }

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a generated skill benchmark report.")
    parser.add_argument("--report", required=True, help="Path to the benchmark markdown report.")
    parser.add_argument("--json-output", help="Optional path for JSON validation evidence.")
    args = parser.parse_args(argv)

    report_path = Path(args.report).resolve()
    result = validate_report(report_path)
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
