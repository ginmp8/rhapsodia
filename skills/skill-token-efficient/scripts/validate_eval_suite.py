#!/usr/bin/env python3
"""Validate regression-suite structure and required coverage using only stdlib."""
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED = {
    "should_activate", "should_not_activate", "ambiguous", "scope_regression",
    "protected_region_regression", "progressive_loading_regression",
    "output_contract", "rollback", "receipt", "adversarial", "holdout",
}

def main() -> int:
    ap = argparse.ArgumentParser(description="Validate token-efficient skill eval coverage.")
    ap.add_argument("suite")
    args = ap.parse_args()
    errors, warnings = [], []
    try:
        data = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status":"fail","errors":[f"invalid JSON: {exc}"],"warnings":[]}, indent=2)); return 1
    if not data.get("schema_version"): errors.append("schema_version is required")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list): errors.append("scenarios must be a list"); scenarios = []
    ids, cats = set(), set()
    for i, item in enumerate(scenarios):
        if not isinstance(item, dict): errors.append(f"scenarios[{i}] must be an object"); continue
        sid = item.get("id"); cat = item.get("category")
        if not sid: errors.append(f"scenarios[{i}] missing id")
        elif sid in ids: errors.append(f"duplicate scenario id: {sid}")
        ids.add(sid)
        if not cat: errors.append(f"scenarios[{i}] missing category")
        else: cats.add(cat)
        if not item.get("prompt"): errors.append(f"scenarios[{i}] missing prompt")
        if not item.get("expected_behavior"): errors.append(f"scenarios[{i}] missing expected_behavior")
        criteria = item.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria: errors.append(f"scenarios[{i}] needs acceptance_criteria")
    missing = sorted(REQUIRED - cats)
    if missing: errors.append("missing required scenario categories: " + ", ".join(missing))
    report = {"status":"fail" if errors else "pass", "errors":errors, "warnings":warnings, "scenario_count":len(scenarios), "categories":sorted(cats)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
