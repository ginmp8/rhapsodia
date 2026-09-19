#!/usr/bin/env python3
"""Deterministic package-footprint audit for thinking-token-efficient.

This measures static text footprint only. It does not observe private reasoning
or billed model tokens.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".template"}
LEXEME_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
METHOD = {
    "id": "lexeme-v1",
    "definition": r"unicode word runs OR one non-whitespace punctuation/symbol; regex=\w+|[^\w\s]",
    "model_tokenizer": False,
    "claim_boundary": "static comparison proxy only; does not measure private reasoning or billing tokens",
}


def text_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in TEXT_SUFFIXES
        and not any(part in {".git", "__pycache__", ".pytest_cache"} for part in p.parts)
    )


def counts(text: str) -> dict[str, int]:
    return {
        "bytes": len(text.encode("utf-8")),
        "characters": len(text),
        "words": len(text.split()),
        "proxy_units": len(LEXEME_RE.findall(text)),
    }


def add(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {key: a.get(key, 0) + b.get(key, 0) for key in {**a, **b}}


def audit(root: Path) -> dict[str, object]:
    files: dict[str, dict[str, int]] = {}
    groups = {
        "entrypoint": {"bytes": 0, "characters": 0, "words": 0, "proxy_units": 0},
        "metadata": {"bytes": 0, "characters": 0, "words": 0, "proxy_units": 0},
        "control_plane": {"bytes": 0, "characters": 0, "words": 0, "proxy_units": 0},
        "supporting": {"bytes": 0, "characters": 0, "words": 0, "proxy_units": 0},
        "total_text": {"bytes": 0, "characters": 0, "words": 0, "proxy_units": 0},
    }
    for path in text_files(root):
        rel = path.relative_to(root).as_posix()
        value = counts(path.read_text(encoding="utf-8", errors="strict"))
        files[rel] = value
        if rel == "SKILL.md":
            group = "entrypoint"
        elif rel == "agents/openai.yaml":
            group = "metadata"
        else:
            group = "supporting"
        groups[group] = add(groups[group], value)
        if group in {"entrypoint", "metadata"}:
            groups["control_plane"] = add(groups["control_plane"], value)
        groups["total_text"] = add(groups["total_text"], value)
    return {"root": str(root), "method": METHOD, "groups": groups, "files": files}


def delta(base: dict[str, int], cand: dict[str, int]) -> dict[str, int | float | None]:
    out: dict[str, int | float | None] = {}
    for key in ("bytes", "characters", "words", "proxy_units"):
        b = int(base.get(key, 0))
        c = int(cand.get(key, 0))
        out[f"{key}_delta"] = c - b
        out[f"{key}_pct"] = None if b == 0 else round((c - b) * 100.0 / b, 2)
    return out


def compare(baseline: Path, candidate: Path) -> dict[str, object]:
    before = audit(baseline)
    after = audit(candidate)
    group_delta = {
        name: delta(before["groups"][name], after["groups"][name])
        for name in before["groups"]
    }
    return {
        "status": "pass",
        "evidence_type": "static-package-footprint-only",
        "method": METHOD,
        "baseline": before,
        "candidate": after,
        "delta": group_delta,
        "limitations": [
            "Proxy units are not model tokens.",
            "Static footprint does not prove hidden reasoning-token savings.",
            "Behavioral equivalence requires executed paired scenarios.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--target", type=Path)
    mode.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    if args.target:
        payload: dict[str, object] = {
            "status": "pass",
            "evidence_type": "static-package-footprint-only",
            **audit(args.target.resolve()),
        }
    else:
        if args.candidate is None:
            parser.error("--candidate is required with --baseline")
        payload = compare(args.baseline.resolve(), args.candidate.resolve())

    serialized = json.dumps(payload, indent=2, sort_keys=True)
    print(serialized)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(serialized + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
