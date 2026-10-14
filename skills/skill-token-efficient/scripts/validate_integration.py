#!/usr/bin/env python3
"""Validate token-efficiency delegation v1 using Python stdlib only.

This validates the request and authorization boundary, not model behavior.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from pathlib import Path

CONTRACT_ID = "skill-opt.token-efficiency"
CONTRACT_VERSION = 1
FORMATS = frozenset({
    "markdown", "plaintext", "yaml", "json-compact", "json-pretty", "toml",
    "ini", "xml", "html", "csv", "tsv", "toon", "jton", "ndjson",
})
ROLES = frozenset({
    "skill-instructions", "human-config", "flat-records", "nested-data",
    "event-stream", "html-dom", "tool-schema", "workflow",
})
OPERATIONS = {
    "format-advice": frozenset({"audit", "plan"}),
    "optimize-existing": frozenset({"apply"}),
    "compare-existing": frozenset({"validate"}),
}
TOKENIZER_SCOPES = frozenset({"catalog", "entrypoint", "activated", "instructions", "all-text"})


def valid_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_request(req: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(req, dict):
        return ["root must be a JSON object"]
    if req.get("contract_id") != CONTRACT_ID:
        problems.append(f"contract_id must be {CONTRACT_ID!r}")
    if type(req.get("contract_version")) is not int or req.get("contract_version") != CONTRACT_VERSION:
        problems.append(f"contract_version must be {CONTRACT_VERSION}")
    permitted = {"contract_id", "contract_version", "consumer", "operation", "mode", "target_skill",
                 "mutation_authorized", "format_context", "tokenization", "staged_candidate",
                 "baseline_path", "candidate_path"}
    extra = set(req) - permitted
    if extra:
        problems.append("unknown request fields: " + ", ".join(sorted(extra)))
    consumer = req.get("consumer")
    if not valid_nonempty(consumer):
        problems.append("consumer must be a non-empty skill identifier")
    op = req.get("operation")
    mode = req.get("mode")
    if not isinstance(op, str) or op not in OPERATIONS:
        problems.append(f"operation must be one of {', '.join(sorted(OPERATIONS))}")
    elif not isinstance(mode, str) or mode not in OPERATIONS[op]:
        problems.append(f"{op} requires mode in {sorted(OPERATIONS[op])}")
    if not valid_nonempty(req.get("target_skill")):
        problems.append("target_skill must identify exactly one existing/draft skill root")
    if type(req.get("mutation_authorized")) is not bool:
        problems.append("mutation_authorized must be a boolean")
    elif op == "optimize-existing":
        if consumer != "skill-booster":
            problems.append("optimize-existing mutation may be delegated only by skill-booster under v1")
        if not req["mutation_authorized"]:
            problems.append("optimize-existing requires explicit mutation_authorized=true")
        if not valid_nonempty(req.get("staged_candidate")):
            problems.append("optimize-existing requires staged_candidate, isolated from baseline")
        elif valid_nonempty(req.get("target_skill")):
            original = Path(req["target_skill"]).resolve()
            staged = Path(req["staged_candidate"]).resolve()
            if staged == original or original in staged.parents:
                problems.append("staged_candidate must not alias or reside inside target_skill")
    elif req["mutation_authorized"]:
        problems.append(f"{op} is read-only and forbids mutation_authorized=true")
    token = req.get("tokenization")
    if op in ("compare-existing", "optimize-existing") and not isinstance(token, dict):
        problems.append("compare/optimize require an explicit tokenization identity")
    if isinstance(token, dict):
        unknown = set(token) - {"primary_method", "scope"}
        if unknown:
            problems.append("unknown tokenization fields: " + ", ".join(sorted(unknown)))
        method = token.get("primary_method")
        if not valid_nonempty(method) or (method != "estimator-v1" and not method.startswith("tiktoken:")):
            problems.append("tokenization.primary_method must be estimator-v1 or tiktoken:<encoding>")
        elif method.startswith("tiktoken:") and not method[len("tiktoken:"):].strip():
            problems.append("tiktoken encoding must be non-empty")
        if not isinstance(token.get("scope"), str) or token["scope"] not in TOKENIZER_SCOPES:
            problems.append("tokenization.scope must identify a supported skill audit surface")
    elif token is not None:
        problems.append("tokenization must be a JSON object or null")
    if op == "compare-existing":
        for key in ("baseline_path", "candidate_path"):
            if not valid_nonempty(req.get(key)):
                problems.append(f"compare-existing requires {key}")
        if valid_nonempty(req.get("baseline_path")) and valid_nonempty(req.get("candidate_path")):
            if Path(req["baseline_path"]).resolve() == Path(req["candidate_path"]).resolve():
                problems.append("compare-existing requires distinct baseline_path and candidate_path")
    ctx = req.get("format_context")
    if op == "format-advice":
        if not isinstance(ctx, dict):
            problems.append("format-advice requires format_context object")
        else:
            unknown = set(ctx) - {"role", "supported_formats", "requires_machine_parse", "requires_type_fidelity", "schema_available", "has_typed_decoder", "allow_nonstandard_codec", "human_editable"}
            if unknown:
                problems.append("unknown format_context fields: " + ", ".join(sorted(unknown)))
            if not isinstance(ctx.get("role"), str) or ctx.get("role") not in ROLES:
                problems.append(f"format_context.role must be one of {', '.join(sorted(ROLES))}")
            formats = ctx.get("supported_formats")
            if not isinstance(formats, list) or not formats:
                problems.append("format_context.supported_formats must be a nonempty array")
            else:
                if not all(valid_nonempty(v) for v in formats):
                    problems.append("each supported format must be a non-empty string")
                unknown = set(str(v) for v in formats) - FORMATS
                if unknown:
                    problems.append("unsupported format(s): " + ", ".join(sorted(unknown)))
                if len(formats) != len(set(str(v) for v in formats)):
                    problems.append("supported_formats contains duplicates")
            for name in ("requires_machine_parse", "requires_type_fidelity", "schema_available", "has_typed_decoder", "allow_nonstandard_codec", "human_editable"):
                if type(ctx.get(name)) is not bool:
                    problems.append(f"format_context.{name} must be a boolean")
    elif ctx is not None:
        problems.append("format_context is only permitted for format-advice")
    return problems


def load_input(name: str) -> Any:
    if name == "-":
        return json.load(sys.stdin)
    with open(name, encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate v1 token-efficiency delegation request")
    ap.add_argument("--json-input", required=True, help="JSON request path or - for stdin")
    ns = ap.parse_args()
    try:
        req = load_input(ns.json_input)
        errors = validate_request(req)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        errors = [f"unreadable or malformed JSON request: {exc}"]
    result = {"status": "pass" if not errors else "fail", "contract_id": CONTRACT_ID, "contract_version": CONTRACT_VERSION, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
