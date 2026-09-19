#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_SCENARIOS = {
    "duplicate-add-column",
    "drop-column",
    "rename-vs-drop-add",
    "conflicting-indexes",
    "conflicting-fks",
    "migration-ordering",
    "branch-divergence",
    "snapshot-divergence",
    "raw-sql",
    "non-idempotent-data-migration",
    "concurrent-deploy-hazard",
    "harmless-migration",
    "unknown-operation",
    "same-diff-rerun",
}
REQUIRED_RULE_FIELDS = {"severity", "confidence", "gate", "hazard_type", "title"}


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Migration Conflict Analyzer package contracts without importing the analyzer.")
    ap.add_argument("--skill-root", required=True)
    ap.add_argument("--json-out")
    ns = ap.parse_args()
    root = Path(ns.skill_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    required_paths = [
        root / "SKILL.md",
        root / "scripts" / "migration_conflict_analyzer.py",
        root / "references" / "heuristic-set.json",
        root / "schemas" / "analysis-report.schema.json",
        root / "evals" / "analyzer-regression-scenarios.json",
        root / "evals" / "expected-heuristics.json",
        root / "evals" / "run_analyzer_regressions.py",
    ]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing required path: {path.relative_to(root) if path.exists() or path.parent.exists() else path}")

    heuristics = load_json(root / "references" / "heuristic-set.json", errors)
    scenarios = load_json(root / "evals" / "analyzer-regression-scenarios.json", errors)
    expected = load_json(root / "evals" / "expected-heuristics.json", errors)
    schema = load_json(root / "schemas" / "analysis-report.schema.json", errors)

    if heuristics.get("set_name") != "migration-conflict-analyzer":
        errors.append("heuristic set_name mismatch")
    if heuristics.get("version") != "2.0.0":
        errors.append("heuristic version must be 2.0.0")
    rules = heuristics.get("rules", {})
    if not isinstance(rules, dict) or not rules:
        errors.append("heuristic rules must be a non-empty object")
        rules = {}

    severities = set(heuristics.get("severity_order", []))
    confidences = set(heuristics.get("confidence_levels", []))
    gates = set(heuristics.get("gates", []))
    for rule_id, rule in sorted(rules.items()):
        missing = REQUIRED_RULE_FIELDS - set(rule)
        if missing:
            errors.append(f"rule {rule_id} missing fields: {sorted(missing)}")
        if rule.get("severity") not in severities:
            errors.append(f"rule {rule_id} invalid severity {rule.get('severity')!r}")
        if rule.get("confidence") not in confidences:
            errors.append(f"rule {rule_id} invalid confidence {rule.get('confidence')!r}")
        if rule.get("gate") not in gates:
            errors.append(f"rule {rule_id} invalid gate {rule.get('gate')!r}")

    if expected.get("heuristic_version") != heuristics.get("version"):
        errors.append("expected-heuristics version does not match heuristic set")
    for rule_id, contract in sorted(expected.get("required_rules", {}).items()):
        rule = rules.get(rule_id)
        if not rule:
            errors.append(f"expected rule missing from heuristic set: {rule_id}")
            continue
        for field in ("severity", "gate"):
            if rule.get(field) != contract.get(field):
                errors.append(f"expected rule {rule_id} {field} mismatch: {rule.get(field)!r} != {contract.get(field)!r}")

    scenario_rows = scenarios.get("scenarios", [])
    ids = [item.get("id") for item in scenario_rows if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate regression scenario IDs")
    missing_scenarios = REQUIRED_SCENARIOS - set(ids)
    if missing_scenarios:
        errors.append(f"missing required regression scenarios: {sorted(missing_scenarios)}")
    for item in scenario_rows:
        if not isinstance(item, dict):
            errors.append("regression scenario must be an object")
            continue
        for rule_id in item.get("expected_rules", []):
            if rule_id not in rules:
                errors.append(f"scenario {item.get('id')} references unknown rule {rule_id}")

    if schema.get("$id") != "urn:migration-conflict-analyzer:analysis-report:2.0":
        errors.append("report schema identity mismatch")
    required_report_fields = set(schema.get("required", []))
    for field in ("analysis_version", "analysis_id", "heuristic_set", "input_identity", "findings", "analysis_receipt"):
        if field not in required_report_fields:
            errors.append(f"report schema missing required field {field}")

    analyzer_text = (root / "scripts" / "migration_conflict_analyzer.py").read_text(encoding="utf-8") if (root / "scripts" / "migration_conflict_analyzer.py").is_file() else ""
    if not re.search(r'^ANALYSIS_VERSION\s*=\s*"2\.0\.0"', analyzer_text, flags=re.M):
        errors.append("analyzer ANALYSIS_VERSION is not 2.0.0")
    if "references\" / \"heuristic-set.json" not in analyzer_text and 'references" / "heuristic-set.json' not in analyzer_text:
        warnings.append("could not statically confirm heuristic-set.json loading path")

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8") if (root / "SKILL.md").is_file() else ""
    for phrase in ("heuristic-set.json", "analysis_receipt", "stable finding IDs", "uncertainty"):
        if phrase not in skill_text:
            errors.append(f"SKILL.md missing contract phrase: {phrase}")

    report = {
        "validator_version": "1.0.0",
        "status": "fail" if errors else ("warn" if warnings else "pass"),
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "rules": len(rules),
            "regression_scenarios": len(ids),
            "required_scenarios_present": len(REQUIRED_SCENARIOS - missing_scenarios),
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if ns.json_out:
        Path(ns.json_out).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
