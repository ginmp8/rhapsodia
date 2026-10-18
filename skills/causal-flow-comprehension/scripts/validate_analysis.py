#!/usr/bin/env python3
"""Validate a Causal Flow Comprehension JSON artifact (Python 3.10+, stdlib).

This proves JSON shape, ID referential integrity and limited evidence-class guards.
It does NOT verify source content, reasoning, closed-world completeness or runtime truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "assets" / "analysis.schema.json"

class DuplicateKeyError(ValueError):
    pass


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys), raw


def check_schema(value: Any, spec: dict, path: str, errors: list[str]) -> None:
    kind = spec.get("type")
    if kind:
        valid = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "boolean": lambda v: isinstance(v, bool),
        }[kind](value)
        if not valid:
            errors.append(f"{path}: expected {kind}")
            return
    if "const" in spec and value != spec["const"]:
        errors.append(f"{path}: unexpected constant value")
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{path}: unrecognized enum value {value!r}")
    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0):
            errors.append(f"{path}: too short")
        if "pattern" in spec and not re.fullmatch(spec["pattern"], value):
            errors.append(f"{path}: invalid identifier format")
    if isinstance(value, dict):
        props = spec.get("properties", {})
        for key in spec.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        for key, item in value.items():
            if key not in props:
                if spec.get("additionalProperties") is False:
                    errors.append(f"{path}.{key}: unexpected field")
            else:
                check_schema(item, props[key], f"{path}.{key}", errors)
    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0):
            errors.append(f"{path}: too few items")
        for i, item in enumerate(value):
            check_schema(item, spec.get("items", {}), f"{path}[{i}]", errors)


def validate(data: Any, schema: dict) -> list[str]:
    errors: list[str] = []
    check_schema(data, schema, "$", errors)
    if errors or not isinstance(data, dict):
        return errors

    sources = data["sources"]
    claims = data["claims"]
    transitions = data["transitions"]
    checks = data["checks"]
    gaps = data["gaps"]

    for name, group in (("sources", sources), ("claims", claims),
                        ("transitions", transitions), ("checks", checks),
                        ("gaps", gaps)):
        ids = [item["id"] for item in group]
        if len(ids) != len(set(ids)):
            errors.append(f"{name}: duplicate IDs")

    by_source = {s["id"]: s for s in sources}
    by_claim = {c["id"]: c for c in claims}
    observed_classes = {
        "static-observed": {"code", "config", "test-definition"},
        "runtime-observed": {"test-run", "trace", "log"},
    }
    for claim in claims:
        cid, status = claim["id"], claim["status"]
        source_ids = claim["source_ids"]
        for sid in source_ids:
            if sid not in by_source:
                errors.append(f"{cid}: source {sid} is absent")
        if status in {"static-observed", "runtime-observed", "inferred"} and not source_ids:
            errors.append(f"{cid}: {status} requires cited sources")
        if status in observed_classes and not any(
            by_source[sid]["kind"] in observed_classes[status]
            for sid in source_ids if sid in by_source
        ):
            errors.append(f"{cid}: {status} requires an appropriate evidence source kind")
        if status == "hypothesis" and not claim["countercheck"]:
            errors.append(f"{cid}: hypothesis needs a falsification check")
        if status == "unknown" and not claim["countercheck"]:
            errors.append(f"{cid}: unknown needs a next verification check")
        if claim["universality"] == "bounded":
            if not data["scope"]["closed_world"]:
                errors.append(f"{cid}: bounded-universal claim requires a declared closed-world scope")
            if not any(c["status"] == "passed" and c["source_ids"] for c in checks):
                errors.append(f"{cid}: bounded-universal claim requires an evidence-linked passed check")

    for transition in transitions:
        for cid in transition["claim_ids"]:
            if cid not in by_claim:
                errors.append(f"{transition['id']}: unknown claim ID {cid}")

    for check in checks:
        if check["status"] == "passed" and not check["source_ids"]:
            errors.append(f"{check['id']}: passed check requires evidence sources")
        for sid in check["source_ids"]:
            if sid not in by_source:
                errors.append(f"{check['id']}: source {sid} is absent")

    if data["verdict"] == "supported-within-scope" and not any(
        c["status"] in ("static-observed", "runtime-observed") for c in claims
    ):
        errors.append("verdict: supported-within-scope requires at least one observed claim")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable status")
    args = parser.parse_args(argv)
    try:
        schema, schema_raw = load_json(SCHEMA)
        data, raw = load_json(args.analysis)
        problems = validate(data, schema)
        code = 1 if problems else 0
        response = {"status": "fail" if problems else "pass",
                    "analysis_sha256": hashlib.sha256(raw).hexdigest(),
                    "schema_sha256": hashlib.sha256(schema_raw).hexdigest(),
                    "diagnostics": problems,
                    "limit": "Structural integrity only; source truth and runtime behavior not verified."}
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError, ValueError) as error:
        code = 1
        response = {"status": "fail", "diagnostics": [str(error)]}
    if args.json:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(response["status"].upper(), args.analysis)
        for problem in response["diagnostics"]:
            print(" -", problem)
    return code


if __name__ == "__main__":
    sys.exit(main())
