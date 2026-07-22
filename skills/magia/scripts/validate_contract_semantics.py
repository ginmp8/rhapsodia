#!/usr/bin/env python3
"""Validate current MAGIA prose against canonical ecosystem contracts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CANONICAL_FIELDS = ("business_priority", "technical_criticality", "execution_sequence")
ALIAS_RE = re.compile(r"(?<!business_)\bpriority\b|\border[ _-]?hint\b", re.IGNORECASE)
REJECTION_RE = re.compile(r"unsupported|reject|rejected|must not|never", re.IGNORECASE)


def collect_errors(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    path = root / "references" / "shared-artifact-ownership.md"
    if not path.is_file():
        return ["missing references/shared-artifact-ownership.md"]
    text = path.read_text(encoding="utf-8")
    for field in CANONICAL_FIELDS:
        if field not in text:
            errors.append(f"shared artifact ownership must name canonical field {field}")
    for number, line in enumerate(text.splitlines(), start=1):
        for match in ALIAS_RE.finditer(line):
            prefix = line[max(0, match.start() - 120):match.start()]
            if not REJECTION_RE.search(prefix):
                errors.append(
                    f"shared artifact ownership preserves or uses unsupported generic priority alias at line {number}"
                )
                break
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
