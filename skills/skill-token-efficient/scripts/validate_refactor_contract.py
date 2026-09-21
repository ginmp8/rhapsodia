#!/usr/bin/env python3
"""Validate the frozen semantic-preservation contract using only stdlib."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

REQUIRED_CATEGORIES = {
    "activation", "scope", "safety", "validation", "evidence",
    "compatibility", "output_contract", "readability", "progressive_loading",
}
PROTECTED_KEYS = {
    "urls", "paths", "commands", "env_vars", "schemas", "flags",
    "proper_nouns", "versions", "numbers",
}
VERIFICATION = {"contains", "regex", "local_reference", "manual", "scenario"}
PLACEHOLDER = re.compile(r"\breplace with\b|\bT(?:ODO)\b|\bTBD\b", re.I)

def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a token-refactor preservation contract.")
    ap.add_argument("contract")
    args = ap.parse_args()
    path = Path(args.contract)
    errors, warnings = [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status":"fail","errors":[f"invalid JSON: {exc}"],"warnings":[]}, indent=2))
        return 1
    if data.get("contract_version") != "1.0": errors.append("contract_version must be '1.0'")
    tok = data.get("tokenization")
    if not isinstance(tok, dict) or not isinstance(tok.get("method"), str) or not tok["method"].strip():
        errors.append("tokenization.method is required")
    elif tok.get("scope") is not None and tok.get("scope") not in {"entrypoint", "instructions", "all-text"}:
        errors.append("tokenization.scope must be entrypoint, instructions, or all-text when present")
    inv = data.get("semantic_invariants")
    ids, cats = set(), set()
    if not isinstance(inv, list):
        errors.append("semantic_invariants must be a list")
        inv = []
    for i, item in enumerate(inv):
        if not isinstance(item, dict):
            errors.append(f"semantic_invariants[{i}] must be an object"); continue
        iid = item.get("id"); cat = item.get("category"); stmt = item.get("statement"); ver = item.get("verification")
        if not isinstance(iid, str) or not iid.strip(): errors.append(f"semantic_invariants[{i}] missing id")
        elif iid in ids: errors.append(f"duplicate invariant id: {iid}")
        ids.add(iid)
        if not isinstance(cat, str) or not cat.strip(): errors.append(f"semantic_invariants[{i}] missing category")
        else: cats.add(cat)
        if not isinstance(stmt, str) or not stmt.strip(): errors.append(f"semantic_invariants[{i}] missing statement")
        elif PLACEHOLDER.search(stmt): errors.append(f"semantic_invariants[{i}] still contains placeholder text")
        if ver not in VERIFICATION: errors.append(f"semantic_invariants[{i}] unsupported verification: {ver!r}")
        if ver in {"contains", "regex", "local_reference"} and not item.get("pattern"):
            errors.append(f"semantic_invariants[{i}] verification {ver} requires pattern")
        if ver == "manual" and not item.get("evidence_refs"):
            errors.append(f"semantic_invariants[{i}] manual verification requires evidence_refs")
        if ver == "scenario" and not item.get("scenario_ids"):
            errors.append(f"semantic_invariants[{i}] scenario verification requires scenario_ids")
    missing_cats = sorted(REQUIRED_CATEGORIES - cats)
    if missing_cats: errors.append("missing required invariant categories: " + ", ".join(missing_cats))
    protected = data.get("protected")
    if not isinstance(protected, dict):
        errors.append("protected must be an object")
    else:
        missing = sorted(PROTECTED_KEYS - set(protected))
        extra = sorted(set(protected) - PROTECTED_KEYS)
        if missing: errors.append("missing protected categories: " + ", ".join(missing))
        if extra: errors.append("unsupported protected categories: " + ", ".join(extra))
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
    report = {"status":"fail" if errors else ("warn" if warnings else "pass"), "errors":errors, "warnings":warnings}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
