#!/usr/bin/env python3
"""Validate current Nomia prose against strict ecosystem compatibility rules."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

LEGACY_ACCEPT_RE = re.compile(
    r"legacy[^\n.]*(accepted|normaliz(?:e|ed|ation)\s+before\s+validation)",
    re.IGNORECASE,
)
NEGATED_RE = re.compile(r"not accepted|reject|rejected|must not|never", re.IGNORECASE)


def collect_errors(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    path = root / "references" / "state-risk-and-handoffs.md"
    if not path.is_file():
        return ["missing references/state-risk-and-handoffs.md"]
    text = path.read_text(encoding="utf-8")
    for number, line in enumerate(text.splitlines(), start=1):
        if LEGACY_ACCEPT_RE.search(line) and not NEGATED_RE.search(line):
            errors.append(f"legacy handoff compatibility is described as accepted at line {number}")
    required = {
        "strict handoff v2": "strict handoff v2 requirement is missing",
        "not accepted as ecosystem handoff compatibility": "explicit legacy handoff rejection is missing",
        "governance-adapt": "migration-only governance-adapt isolation is missing",
        "externally supplied current identities": "current identity provenance gate is missing",
    }
    lower = text.lower()
    for phrase, message in required.items():
        if phrase.lower() not in lower:
            errors.append(message)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    errors = collect_errors(root)
    result: dict[str, Any] = {
        "status": "pass" if not errors else "fail",
        "target": str(root),
        "errors": errors,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
