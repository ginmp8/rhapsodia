#!/usr/bin/env python3
"""Compare a candidate skill against a baseline semantic-preservation contract."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
URL_RE = re.compile(r"https?://[^\s)>\]}]+")
FLAG_RE = re.compile(r"(?<!\w)--[a-zA-Z0-9][a-zA-Z0-9-]*")
ENV_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?\b")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
PROPER_RE = re.compile(r"\b(?:[A-Z]{2,}|[A-Z][a-z]+[A-Z][A-Za-z]*)\b")
COMMAND_STARTS = ("python ", "python3 ", "git ", "bash ", "sh ", "dotnet ", "npm ", "npx ", "uv ", "pytest ")
HARD_LITERAL_CATEGORIES = {"urls", "paths", "commands", "env_vars", "schemas", "flags", "versions"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def extract(text: str) -> dict[str, set[str]]:
    spans = CODE_SPAN_RE.findall(text)
    path_prefixes = ("references/", "scripts/", "evals/", "assets/", "agents/", "contracts/", "./", "../", "/")
    paths = {s.strip() for s in spans if "/" in s and " " not in s and s.strip().startswith(path_prefixes)}
    commands = {s.strip() for s in spans if s.strip().lower().startswith(COMMAND_STARTS)}
    schemas = {s.strip() for s in spans if s.strip().lower().endswith((".json", ".yaml", ".yml"))}
    return {
        "urls": set(URL_RE.findall(text)),
        "paths": paths,
        "commands": commands,
        "env_vars": set(ENV_RE.findall(text)),
        "schemas": schemas,
        "flags": set(FLAG_RE.findall(text)),
        "proper_nouns": set(PROPER_RE.findall(text)),
        "versions": set(VERSION_RE.findall(text)),
        "numbers": set(NUMBER_RE.findall(text)),
    }


def merge(dst: dict[str, set[str]], src: dict[str, set[str]]) -> None:
    for key, values in src.items():
        dst.setdefault(key, set()).update(values)


def load_contract(path: Path) -> dict[str, object]:
    return json.loads(read(path))


def invariant_diagnostics(candidate: Path, contract: dict[str, object]) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    for item in contract.get("required_invariants", []):
        inv_id = item.get("id", "unknown")
        severity = item.get("severity", "hard")
        needles = [str(x).lower() for x in item.get("match_any", [])]
        for rel in item.get("files", []):
            path = candidate / rel
            if not path.exists():
                diagnostics.append({"code": "INVARIANT_FILE_MISSING", "severity": severity, "subject": rel, "evidence": inv_id})
                continue
            lower = read(path).lower()
            if needles and not any(needle in lower for needle in needles):
                diagnostics.append({"code": "INVARIANT_MISSING", "severity": severity, "subject": rel, "evidence": inv_id})
    return diagnostics


def compare(baseline: Path, candidate: Path, contract_path: Path) -> dict[str, object]:
    contract = load_contract(contract_path)
    diagnostics = invariant_diagnostics(candidate, contract)
    base_literals: dict[str, set[str]] = {}
    cand_literals: dict[str, set[str]] = {}

    for rel in contract.get("protected_core_files", []):
        bp = baseline / rel
        cp = candidate / rel
        if bp.exists():
            merge(base_literals, extract(read(bp)))
        if cp.exists():
            merge(cand_literals, extract(read(cp)))
        elif bp.exists():
            diagnostics.append({"code": "PROTECTED_FILE_MISSING", "severity": "hard", "subject": rel, "evidence": "present in baseline"})

    literal_delta: dict[str, object] = {}
    for category in contract.get("protected_literal_categories", []):
        if category in {"safety_rules", "validation_rules", "evidence_rules"}:
            continue
        before = base_literals.get(category, set())
        after = cand_literals.get(category, set())
        removed = sorted(before - after)
        added = sorted(after - before)
        literal_delta[category] = {"removed": removed, "added": added}
        if removed:
            diagnostics.append({
                "code": "PROTECTED_LITERAL_REMOVED" if category in HARD_LITERAL_CATEGORIES else "PROTECTED_LITERAL_REVIEW",
                "severity": "hard" if category in HARD_LITERAL_CATEGORIES else "review",
                "subject": category,
                "evidence": removed,
            })

    hard = [d for d in diagnostics if d.get("severity") == "hard"]
    review = [d for d in diagnostics if d.get("severity") == "review"]
    return {
        "status": "pass" if not hard else "fail",
        "baseline": str(baseline),
        "candidate": str(candidate),
        "contract": str(contract_path),
        "diagnostics": diagnostics,
        "summary": {"hard_failures": len(hard), "review_items": len(review)},
        "literal_delta": literal_delta,
        "limitations": [
            "Literal preservation is not semantic equivalence proof.",
            "Proper-noun and numeric deltas are review signals, not automatic failures.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    contract = args.contract.resolve() if args.contract else candidate / "contracts/semantic-contract.json"
    result = compare(args.baseline.resolve(), candidate, contract)
    serialized = json.dumps(result, indent=2, sort_keys=True)
    print(serialized)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(serialized + "\n", encoding="utf-8")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
