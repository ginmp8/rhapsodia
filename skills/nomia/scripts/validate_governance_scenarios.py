#!/usr/bin/env python3
"""Validate Nomia governance profile, lifecycle, routing, and boundary scenarios."""
from __future__ import annotations
import argparse, json, sys
from collections import Counter
from pathlib import Path

from nomia_utils import atomic_write_text

REQUIRED_FIELDS = {"id", "title", "prompt", "category", "expected_activation", "expected_profile", "expected_lifecycle", "expected_mode", "expected_boundary"}
CATEGORIES = {"activation", "non_activation", "ambiguous", "edge", "adversarial", "governance"}
PROFILES = {"quick", "standard", "governed", "not_applicable", "escalate"}
LIFECYCLE = {"intake", "triage", "commit", "track", "decide", "close", "not_applicable"}


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = [], []
    if not isinstance(data, dict) or not isinstance(data.get("scenarios"), list):
        return {"status": "fail", "errors": ["scenario suite must be an object with a scenarios list"], "warnings": [], "count": 0}
    seen = set(); counts = Counter()
    for i, item in enumerate(data["scenarios"]):
        label = item.get("id", f"index-{i}") if isinstance(item, dict) else f"index-{i}"
        if not isinstance(item, dict):
            errors.append(f"{label}: scenario must be an object"); continue
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing: errors.append(f"{label}: missing fields {missing}")
        if label in seen: errors.append(f"{label}: duplicate id")
        seen.add(label)
        category = item.get("category")
        if category not in CATEGORIES: errors.append(f"{label}: invalid category {category!r}")
        else: counts[category] += 1
        if item.get("expected_profile") not in PROFILES: errors.append(f"{label}: invalid expected_profile")
        if item.get("expected_lifecycle") not in LIFECYCLE: errors.append(f"{label}: invalid expected_lifecycle")
        if item.get("expected_activation") not in (True, False, None): errors.append(f"{label}: expected_activation must be true, false, or null")
        for field in ("title", "prompt", "expected_mode", "expected_boundary"):
            if not isinstance(item.get(field), str) or not item[field].strip(): errors.append(f"{label}: {field} must be non-empty")
        risk = set(item.get("risk_triggers") or [])
        if item.get("expected_profile") == "quick" and risk.intersection({"regulatory", "financial", "privacy", "security", "contractual", "executive", "cross_org"}):
            errors.append(f"{label}: quick profile cannot retain mandatory escalation risk")
        if item.get("expected_profile") == "escalate" and not risk:
            errors.append(f"{label}: escalate profile requires at least one risk trigger")
    for category in ("activation", "non_activation", "ambiguous", "edge", "adversarial"):
        if counts[category] < 2: warnings.append(f"category {category} has fewer than 2 scenarios")
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "count": len(data["scenarios"]), "counts": dict(counts)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("scenario_file", nargs="?", default=str(Path(__file__).resolve().parents[1] / "evals" / "governance-scenarios.json"))
    p.add_argument("--json-output")
    args = p.parse_args()
    try: result = validate(Path(args.scenario_file))
    except Exception as exc: result = {"status": "fail", "errors": [str(exc)], "warnings": [], "count": 0}
    if args.json_output: atomic_write_text(Path(args.json_output), json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(main())
