#!/usr/bin/env python3
"""Render a disposable traceability projection from canonical Mago package Markdown."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

HEADINGS = {
    "requirements": re.compile(r"^###\s+(REQ-\d{3})\b"),
    "acceptance": re.compile(r"^###\s+(AC-\d{3})\b"),
    "decisions": re.compile(r"^###\s+(DECISION-\d{3})\b"),
    "validations": re.compile(r"^###\s+(VAL-\d{3})\b"),
}
TASK_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(task\d{3}):")
LINK_RE = re.compile(r"^\s*-\s*(Requirements|Acceptance|Decisions|Validations|Tasks):\s*(.+?)\s*$")
ID_PATTERNS = {
    "Requirements": re.compile(r"REQ-\d{3}"),
    "Acceptance": re.compile(r"AC-\d{3}"),
    "Decisions": re.compile(r"DECISION-\d{3}"),
    "Validations": re.compile(r"VAL-\d{3}"),
    "Tasks": re.compile(r"task\d{3}"),
}
FILES = {
    "prd.md": ("requirements", "acceptance"),
    "technical-design.md": ("decisions",),
    "tasks.md": ("tasks",),
    "validation.md": ("validations",),
}

def parse_file(path: Path, allowed: tuple[str, ...]) -> tuple[dict[str, dict[str, list[str]]], list[str]]:
    records: dict[str, dict[str, list[str]]] = {}
    duplicates: list[str] = []
    current: str | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        found = None
        if "tasks" in allowed:
            m = TASK_RE.match(line)
            if m:
                found = m.group(1)
        if found is None:
            for kind in allowed:
                if kind == "tasks":
                    continue
                m = HEADINGS[kind].match(line)
                if m:
                    found = m.group(1)
                    break
        if found:
            if found in records:
                duplicates.append(f"{path.name}:{line_number}: duplicate {found}")
            records.setdefault(found, {})
            current = found
            continue
        m = LINK_RE.match(line)
        if current and m:
            field, value = m.groups()
            records[current][field.lower()] = ID_PATTERNS[field].findall(value)
    return records, duplicates

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("package", help="Canonical Mago spec package directory")
    ap.add_argument("--output", required=True, help="External JSON output path")
    args = ap.parse_args()
    package = Path(args.package).resolve()
    all_records: dict[str, dict[str, list[str]]] = {}
    errors: list[str] = []
    for name, allowed in FILES.items():
        path = package / name
        if not path.is_file():
            errors.append(f"missing canonical artifact: {name}")
            continue
        records, duplicates = parse_file(path, allowed)
        all_records.update(records)
        errors.extend(duplicates)
    output = {
        "kind": "mago-traceability-projection",
        "authoritative": False,
        "package": str(package),
        "records": dict(sorted(all_records.items())),
        "render_errors": errors,
    }
    out = Path(args.output).resolve()
    if package == out or package in out.parents:
        raise SystemExit("output must be outside the canonical package directory")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status: {'pass' if not errors else 'fail'}")
    print(f"records: {len(all_records)}")
    print(f"output: {out}")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
