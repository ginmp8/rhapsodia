#!/usr/bin/env python3
"""Validate Premortem Analysis JSON reports; Python standard library only.

Schema checks validate types/shape. Cross-record checks validate referential integrity
and authority/disposition constraints. No code here validates causal truth.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "assets" / "premortem-report.schema.json"


def _type_matches(value: Any, kind: str) -> bool:
    if kind == "object":
        return isinstance(value, dict)
    if kind == "array":
        return isinstance(value, list)
    if kind == "string":
        return isinstance(value, str)
    if kind == "null":
        return value is None
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (float, int)) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    return False


def _run_schema(value: Any, rule: dict[str, Any], schema: dict[str, Any], path: str, errors: list[str]) -> None:
    if "$ref" in rule:
        ref = rule["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/$defs/"):
            errors.append(f"{path}: unsupported local schema reference")
            return
        name = ref.split("/")[-1]
        target = schema.get("$defs", {}).get(name)
        if not isinstance(target, dict):
            errors.append(f"{path}: unresolved schema reference {ref}")
            return
        _run_schema(value, target, schema, path, errors)
        return
    if "const" in rule and value != rule["const"]:
        errors.append(f"{path}: expected constant {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path}: value outside allowed enumeration")
    kinds = rule.get("type")
    if kinds is not None:
        if isinstance(kinds, str):
            kinds = [kinds]
        if not any(_type_matches(value, kind) for kind in kinds):
            errors.append(f"{path}: invalid type, expected {'|'.join(kinds)}")
            return
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0):
            errors.append(f"{path}: string shorter than allowed")
        if "pattern" in rule and not re.search(rule["pattern"], value):
            errors.append(f"{path}: pattern mismatch")
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            errors.append(f"{path}: fewer array items than allowed")
        if rule.get("uniqueItems"):
            canonical = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in value]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{path}: duplicate array items")
        for i, item in enumerate(value):
            if "items" in rule:
                _run_schema(item, rule["items"], schema, f"{path}[{i}]", errors)
    if isinstance(value, dict):
        props = rule.get("properties", {})
        for key in rule.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing key {key!r}")
        if rule.get("additionalProperties") is False:
            for key in set(value) - set(props):
                errors.append(f"{path}: unexpected key {key!r}")
        for key in value.keys() & props.keys():
            _run_schema(value[key], props[key], schema, f"{path}.{key}", errors)


def validate_report(report: Any, schema: dict[str, Any] | None = None) -> list[str]:
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    _run_schema(report, schema, schema, "$", errors)
    if not isinstance(report, dict) or any(x not in report for x in ("risks", "sources", "plan_changes", "residual_risks", "approval_gates", "status", "mode")):
        return sorted(set(errors))
    if not all(isinstance(report[k], list) for k in ("risks", "sources", "plan_changes", "residual_risks", "approval_gates")):
        return sorted(set(errors))

    def _ids(records: list, field: str, prefix: str) -> set[str]:
        seen: set[str] = set()
        for i, rec in enumerate(records):
            if not isinstance(rec, dict):
                continue
            identifier = rec.get(field)
            if not isinstance(identifier, str):
                continue
            if identifier in seen:
                errors.append(f"{prefix}[{i}].{field}: duplicate ID {identifier}")
            seen.add(identifier)
        return seen

    sources = _ids(report["sources"], "source_id", "sources")
    risks = _ids(report["risks"], "risk_id", "risks")
    _ids(report["plan_changes"], "change_id", "plan_changes")
    for i, risk in enumerate(report["risks"]):
        if not isinstance(risk, dict):
            continue
        status = risk.get("evidence_status")
        refs = risk.get("source_ids", [])
        if not isinstance(refs, list):
            continue
        if status in ("supported", "contradicted") and not refs:
            errors.append(f"risks[{i}]: {status} requires a source reference")
        for ref in refs:
            if not isinstance(ref, str) or ref not in sources:
                errors.append(f"risks[{i}]: unknown source {ref!r}")
    for i, change in enumerate(report["plan_changes"]):
        if not isinstance(change, dict):
            continue
        related = change.get("related_risk_ids", [])
        if isinstance(related, list):
            for risk_id in related:
                if not isinstance(risk_id, str) or risk_id not in risks:
                    errors.append(f"plan_changes[{i}]: unknown risk {risk_id!r}")
        if change.get("disposition") not in (None, "proposed"):
            if change.get("decision_owner") == "unknown" or not change.get("decision_evidence"):
                errors.append(f"plan_changes[{i}]: non-proposed disposition requires identified owner and decision evidence")
    for risk_id in report["residual_risks"]:
        if not isinstance(risk_id, str) or risk_id not in risks:
            errors.append(f"residual_risks: unknown risk {risk_id!r}")
    for i, gate in enumerate(report["approval_gates"]):
        if not isinstance(gate, dict):
            continue
        if gate.get("status") == "satisfied" and (gate.get("owner") == "unknown" or not gate.get("evidence")):
            errors.append(f"approval_gates[{i}]: satisfied gate requires identified owner and supporting evidence")
    if report.get("mode") == "governed" and not report["approval_gates"]:
        errors.append("governed mode requires explicit approval/stop gates")
    if report.get("status") in ("partial", "blocked") and not (report.get("unknowns") or report.get("limitations")):
        errors.append("partial/blocked report requires explicit unknowns or limitations")
    if report.get("status") == "complete" and not report["risks"]:
        errors.append("complete report with zero risks should be partial, not proof of safety")
    for i, source in enumerate(report["sources"]):
        if isinstance(source, dict):
            locator = source.get("locator", "")
            if isinstance(locator, str) and re.match(r"(?i)^\s*(?:file|javascript|data|vbscript):", locator):
                errors.append(f"sources[{i}]: unsafe locator scheme")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        errors = validate_report(report)
    except (OSError, ValueError) as exc:
        errors = [f"input error: {exc}"]
    result = {"status": "pass" if not errors else "fail", "schema_version": "1.0.0", "errors": errors, "claims": "structural and referential checks only"}
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"].upper(), "; ".join(errors) if errors else "report structure and references valid")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
