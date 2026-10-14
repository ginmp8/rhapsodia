#!/usr/bin/env python3
"""Deterministic *advisory* format eligibility; no token or behavior measurements.

Only operates on v1 read-only format-advice requests, using Python stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from validate_integration import CONTRACT_ID, CONTRACT_VERSION, load_input, validate_request


def choose(req: dict[str, Any]) -> dict[str, Any]:
    errors = validate_request(req)
    if errors:
        raise ValueError("; ".join(errors))
    if req["operation"] != "format-advice":
        raise ValueError("recommend_format.py only supports format-advice; other operations must use existing skill workflows")
    ctx = req["format_context"]
    role = ctx["role"]
    supported = set(ctx["supported_formats"])
    machine = ctx["requires_machine_parse"]
    typed = ctx["requires_type_fidelity"]
    schema = ctx["schema_available"]
    codec = ctx["allow_nonstandard_codec"]
    decoder = ctx["has_typed_decoder"]
    editable = ctx["human_editable"]
    conditional: list[str] = []
    checks = [
        "Prove content/contract, guards, hierarchy, authority, and tool/schema preservation before conversion.",
        "Count complete serialized input including schema/format hints with the pinned tokenizer before ranking by tokens.",
        "Run paired agent/model scenarios before making equivalence, quality, or total-cost claims.",
    ]
    reasoning = "Format suggestion is based on structural eligibility, not measured token or agent results."
    # These are compatibility-first defaults, not universal token efficiency ranks.
    if role == "skill-instructions":
        priority = ["markdown"]
        reasoning = "Agent Skills SKILL.md is a Markdown instruction control plane; keep operative rules in Markdown."
    elif role == "tool-schema":
        priority = ["json-compact"]
        reasoning = "A native JSON tool contract must not be replaced by a non-native serialization."
    elif role == "html-dom":
        priority = ["html"]
        reasoning = "DOM/HTML semantics are required; removing tags changes the input contract."
    elif role == "event-stream":
        priority = ["ndjson"]
        reasoning = "Newline-delimited JSON supports streaming records; it is not assumed token-minimal."
    elif role == "workflow":
        priority = ["json-compact"] if machine else ["markdown", "plaintext"]
        reasoning = "Keep workflow dependencies and instructions explicit; machine consumers require a parseable contract."
    elif role == "human-config":
        priority = ["json-compact"] if (machine and typed) or not editable else ["yaml", "toml", "json-compact"]
        reasoning = "Choose human-editable syntax only if consumer parsing/typing is compatible."
    elif role == "flat-records":
        # CSV/TSV are semantically eligible only with a defined schema; typed values need a typed decoder.
        flat_eligible = schema and (not typed or decoder)
        priority = (["csv", "tsv"] if flat_eligible else []) + ["json-compact", "json-pretty", "yaml"]
        reasoning = "Tabular encoding avoids repeated field names when a reversible column schema exists."
        if flat_eligible:
            checks.append("Execute round-trip with schema, null/empty, escaped delimiter, newline and type cases.")
        if codec and schema and decoder:
            conditional.extend(x for x in ("toon", "jton") if x in supported)
    elif role == "nested-data":
        priority = ["json-compact", "json-pretty", "yaml", "xml"]
        reasoning = "Typed, nested or heterogeneous payloads default to JSON until an alternative proves reversible and cheaper."
        if codec and schema and decoder:
            conditional.extend(x for x in ("toon", "jton") if x in supported)
            checks.append("For nonstandard codecs, test parser compatibility and round-trip of nested structures.")
    else:
        raise ValueError("unsupported role")
    # Typed machine contracts must not silently fall back to a YAML/XML codec
    # whose parsing/type rules were not proven through this request surface.
    if typed and machine and role in ("nested-data", "flat-records", "human-config", "workflow"):
        if role == "flat-records" and schema and decoder:
            priority = [x for x in priority if x in ("csv", "tsv", "json-compact")]
        else:
            priority = [x for x in priority if x == "json-compact"]
    primary_candidates = [f for f in priority if f in supported]
    candidates = primary_candidates + conditional
    # An experimental/custom codec is a measurement candidate, not a safe default.
    # Without a compatible native fallback, escalation is required.
    selected = primary_candidates[0] if primary_candidates else None
    if role in ("skill-instructions", "tool-schema", "html-dom", "event-stream"):
        # No format fallback when the medium is part of the contract.
        candidates = [priority[0]] if selected else []
        selected = candidates[0] if candidates else None
    if selected is None:
        checks.append("No contract-compatible format was provided; do not silently downgrade or invent a decoder.")
    return {
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
        "consumer": req["consumer"],
        "operation": req["operation"],
        "status": "advice-only" if selected else "blocked",
        "recommended_format": selected,
        "candidates_to_measure": candidates,
        "conditional_formats": conditional,
        "decision_basis": reasoning,
        "evidence": {"layer": "deterministic-eligibility", "token_count_status": "not-run", "behavior_status": "not-run", "runtime_status": "not-run"},
        "required_checks": checks,
        "mutation_performed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Recommend compatible format candidates; NOT token measurements")
    ap.add_argument("--json-input", required=True, help="request JSON file or - for stdin")
    ns = ap.parse_args()
    try:
        outcome = choose(load_input(ns.json_input))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0 if outcome["status"] != "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
