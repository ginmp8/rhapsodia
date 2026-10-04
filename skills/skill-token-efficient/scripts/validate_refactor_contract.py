#!/usr/bin/env python3
"""Validate frozen semantic-preservation contracts using only stdlib.

Contract v1 remains accepted for backward compatibility. Contract v2 adds
explicit authority/workflow, placement/load-condition, and claim-evidence gates.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

V1_REQUIRED = {
    "activation", "scope", "safety", "validation", "evidence",
    "compatibility", "output_contract", "readability", "progressive_loading",
}
V2_REQUIRED = V1_REQUIRED | {"authority", "workflow"}
PROTECTED_KEYS = {
    "urls", "paths", "commands", "env_vars", "schemas", "flags",
    "proper_nouns", "versions", "numbers",
}
VERIFICATION = {"contains", "regex", "local_reference", "manual", "scenario"}
PLACEMENTS = {"entrypoint", "reference", "either"}
PLACEHOLDER = re.compile(r"\breplace with\b|\bT(?:ODO)\b|\bTBD\b", re.I)
V1_SCOPES = {"entrypoint", "instructions", "all-text"}
V2_SCOPES = {"catalog", "entrypoint", "activated", "instructions", "all-text"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a token-refactor preservation contract.")
    ap.add_argument("contract")
    args = ap.parse_args()
    path = Path(args.contract)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "fail", "errors": [f"invalid JSON: {exc}"], "warnings": []}, indent=2))
        return 1

    version = data.get("contract_version")
    if version not in {"1.0", "2.0"}:
        errors.append("contract_version must be '1.0' or '2.0'")

    tok = data.get("tokenization")
    if not isinstance(tok, dict) or not isinstance(tok.get("method"), str) or not tok["method"].strip():
        errors.append("tokenization.method is required")
    else:
        allowed_scopes = V2_SCOPES if version == "2.0" else V1_SCOPES
        if tok.get("scope") is not None and tok.get("scope") not in allowed_scopes:
            errors.append("tokenization.scope is unsupported for this contract version")
        comparisons = tok.get("comparison_methods", [])
        if version == "2.0":
            if not isinstance(comparisons, list) or any(not isinstance(x, str) or not x.strip() for x in comparisons):
                errors.append("v2 tokenization.comparison_methods must be an array of non-empty strings")
            elif len(set(comparisons)) != len(comparisons):
                errors.append("v2 tokenization.comparison_methods must be unique")
            elif tok.get("method") in comparisons:
                errors.append("v2 primary tokenization.method must not be repeated in comparison_methods")
            surfaces = tok.get("surfaces")
            if not isinstance(surfaces, list) or set(surfaces) != V2_SCOPES or len(surfaces) != len(V2_SCOPES):
                errors.append("v2 tokenization.surfaces must contain catalog, entrypoint, activated, instructions, and all-text exactly once")

    if version == "2.0":
        claim = data.get("claim_evidence")
        if not isinstance(claim, dict):
            errors.append("v2 claim_evidence is required")
        else:
            if claim.get("behavioral_claims_require") != "executed-scenario":
                errors.append("v2 behavioral_claims_require must be 'executed-scenario'")
            if claim.get("runtime_claims_require") != "executed-runtime":
                errors.append("v2 runtime_claims_require must be 'executed-runtime'")

    inv = data.get("semantic_invariants")
    ids: set[str] = set()
    cats: set[str] = set()
    if not isinstance(inv, list):
        errors.append("semantic_invariants must be a list")
        inv = []
    for i, item in enumerate(inv):
        if not isinstance(item, dict):
            errors.append(f"semantic_invariants[{i}] must be an object")
            continue
        iid = item.get("id")
        cat = item.get("category")
        stmt = item.get("statement")
        ver = item.get("verification")
        if not isinstance(iid, str) or not iid.strip():
            errors.append(f"semantic_invariants[{i}] missing id")
        elif iid in ids:
            errors.append(f"duplicate invariant id: {iid}")
        else:
            ids.add(iid)
        if not isinstance(cat, str) or not cat.strip():
            errors.append(f"semantic_invariants[{i}] missing category")
        else:
            cats.add(cat)
        if not isinstance(stmt, str) or not stmt.strip():
            errors.append(f"semantic_invariants[{i}] missing statement")
        elif PLACEHOLDER.search(stmt):
            errors.append(f"semantic_invariants[{i}] still contains placeholder text")
        if ver not in VERIFICATION:
            errors.append(f"semantic_invariants[{i}] unsupported verification: {ver!r}")
        if ver in {"contains", "regex", "local_reference"} and not item.get("pattern"):
            errors.append(f"semantic_invariants[{i}] verification {ver} requires pattern")
        if ver == "manual" and not item.get("evidence_refs"):
            errors.append(f"semantic_invariants[{i}] manual verification requires evidence_refs")
        if ver == "scenario" and not item.get("scenario_ids"):
            errors.append(f"semantic_invariants[{i}] scenario verification requires scenario_ids")

        if version == "2.0":
            placement = item.get("placement")
            if placement not in PLACEMENTS:
                errors.append(f"semantic_invariants[{i}] v2 placement must be entrypoint, reference, or either")
            if placement == "reference" and not isinstance(item.get("load_condition"), str):
                errors.append(f"semantic_invariants[{i}] reference placement requires load_condition")
            elif placement == "reference" and not item.get("load_condition", "").strip():
                errors.append(f"semantic_invariants[{i}] reference placement requires non-empty load_condition")

    required = V2_REQUIRED if version == "2.0" else V1_REQUIRED
    missing_cats = sorted(required - cats)
    if missing_cats:
        errors.append("missing required invariant categories: " + ", ".join(missing_cats))

    protected = data.get("protected")
    if not isinstance(protected, dict):
        errors.append("protected must be an object")
    else:
        missing = sorted(PROTECTED_KEYS - set(protected))
        extra = sorted(set(protected) - PROTECTED_KEYS)
        if missing:
            errors.append("missing protected categories: " + ", ".join(missing))
        if extra:
            errors.append("unsupported protected categories: " + ", ".join(extra))
        for key in sorted(PROTECTED_KEYS & set(protected)):
            value = protected[key]
            if not isinstance(value, list):
                errors.append(f"protected.{key} must be an array")
                continue
            for j, item in enumerate(value):
                if isinstance(item, str):
                    continue
                if not isinstance(item, dict):
                    errors.append(f"protected.{key}[{j}] must be a string or object")
                    continue
                if not isinstance(item.get("value"), str) or not item["value"].strip():
                    errors.append(f"protected.{key}[{j}].value is required")
                eq = item.get("equivalents", [])
                if not isinstance(eq, list) or any(not isinstance(x, str) or not x for x in eq):
                    errors.append(f"protected.{key}[{j}].equivalents must be an array of strings")
                if eq and item.get("authorized") is not True:
                    errors.append(f"protected.{key}[{j}] equivalents require authorized=true")
                if eq and not isinstance(item.get("reason"), str):
                    errors.append(f"protected.{key}[{j}] authorized equivalence requires reason")

    report = {
        "status": "fail" if errors else ("warn" if warnings else "pass"),
        "contract_version": version,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
