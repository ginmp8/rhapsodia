#!/usr/bin/env python3
"""Validate the canonical non-authoritative Mago change-delta Markdown contract."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SECTIONS = [
    "Added Behavior", "Modified Behavior", "Removed Behavior", "Preserved Behavior",
    "Compatibility Impact", "Migration Impact", "Rollback Assumptions", "Merge and Retention",
]

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path")
    ap.add_argument("--json-output")
    args = ap.parse_args()
    path = Path(args.path)
    text = path.read_text(encoding="utf-8-sig")
    errors = []
    if not re.search(r"^authoritative:\s*false\s*$", text, re.MULTILINE):
        errors.append("delta must declare authoritative: false")
    positions = []
    for section in SECTIONS:
        m = re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE | re.IGNORECASE)
        if not m:
            errors.append(f"missing section: {section}")
        else:
            positions.append((m.start(), section, m.end()))
    positions.sort()
    for index, (_, section, end) in enumerate(positions):
        next_start = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        body = text[end:next_start].strip()
        if not body or not re.search(r"^-\s+\S", body, re.MULTILINE):
            errors.append(f"section has no explicit entry or none-with-reason: {section}")
    if "Source of truth after merge: Mago registry and canonical package artifacts" not in text:
        errors.append("merge section must preserve Mago canonical source of truth")
    result = {"status": "pass" if not errors else "fail", "errors": errors, "path": str(path.resolve())}
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
