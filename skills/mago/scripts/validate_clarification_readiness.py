#!/usr/bin/env python3
"""Validate structured assumptions, blockers, and open questions before handoff."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

CONTRACT_RE = re.compile(r"(?m)^clarification_contract:\s*2\s*$")
HEADER_RE = re.compile(
    r"(?m)^###\s+(?P<kind>ASSUMPTION|BLOCKER|QUESTION)-(?P<number>\d{3})\s+-\s+(?P<title>.+?)\s*$"
)
FIELD_RE = re.compile(r"(?m)^-\s+(?P<key>[^:]+):\s*(?P<value>.*?)\s*$")
UNRESOLVED_RE = re.compile(r"(?i)^(?:tbd|to[d]o|unknown|n/?a|none|placeholder|<[^>]+>)$")
VALID_SEVERITY = {"low", "medium", "high", "critical"}
VALID_STATUS = {
    "ASSUMPTION": {"open", "confirmed", "invalidated"},
    "BLOCKER": {"open", "resolved"},
    "QUESTION": {"open", "resolved", "deferred"},
}
REQUIRED_FIELDS = ("Status", "Severity", "Evidence", "Owner", "Resolution condition")


@dataclass
class ClarificationRecord:
    record_id: str
    kind: str
    title: str
    fields: dict[str, str] = field(default_factory=dict)


def read(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{path}: notes artifact must be a regular file")
    return path.read_text(encoding="utf-8-sig")


def parse_records(text: str) -> tuple[list[ClarificationRecord], list[str]]:
    matches = list(HEADER_RE.finditer(text))
    records: list[ClarificationRecord] = []
    errors: list[str] = []
    seen: set[str] = set()
    for index, match in enumerate(matches):
        kind = match.group("kind")
        record_id = f"{kind}-{match.group('number')}"
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
        fields = {item.group("key").strip(): item.group("value").strip() for item in FIELD_RE.finditer(body)}
        if record_id in seen:
            errors.append(f"duplicate clarification id `{record_id}`")
        seen.add(record_id)
        records.append(ClarificationRecord(record_id, kind, match.group("title").strip(), fields))
    return records, errors


def resolved(value: str) -> bool:
    return bool(value.strip()) and not UNRESOLVED_RE.fullmatch(value.strip())


def validate_notes(path: Path, *, require_v2: bool = False, handoff: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        text = read(path)
    except ValueError as exc:
        return [str(exc)]

    has_v2 = bool(CONTRACT_RE.search(text))
    if require_v2 and not has_v2:
        return [f"{path}: clarification readiness v2 requires frontmatter `clarification_contract: 2`"]
    if not has_v2 and not require_v2:
        return []

    records, parse_errors = parse_records(text)
    errors.extend(f"{path}: {message}" for message in parse_errors)
    for record in records:
        for name in REQUIRED_FIELDS:
            value = record.fields.get(name, "")
            if not resolved(value):
                errors.append(f"{path}: `{record.record_id}` missing resolved field `{name}`")
        status = record.fields.get("Status", "").lower()
        severity = record.fields.get("Severity", "").lower()
        if status and status not in VALID_STATUS[record.kind]:
            errors.append(
                f"{path}: `{record.record_id}` Status must be one of {sorted(VALID_STATUS[record.kind])}"
            )
        if severity and severity not in VALID_SEVERITY:
            errors.append(f"{path}: `{record.record_id}` Severity must be one of {sorted(VALID_SEVERITY)}")

        is_closed = status in {"confirmed", "invalidated", "resolved"}
        if is_closed and not resolved(record.fields.get("Resolution evidence", "")):
            errors.append(f"{path}: closed `{record.record_id}` requires `Resolution evidence`")

        if handoff:
            if record.kind == "BLOCKER" and status == "open":
                errors.append(f"{path}: handoff blocked by open `{record.record_id}`")
            if record.kind in {"ASSUMPTION", "QUESTION"} and status == "open" and severity in {"high", "critical"}:
                errors.append(
                    f"{path}: handoff blocked by open {severity} `{record.record_id}`"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Mago clarification readiness records.")
    parser.add_argument("notes", help="Path to notes.md")
    parser.add_argument("--require-v2", action="store_true", help="Require clarification_contract: 2")
    parser.add_argument("--handoff", action="store_true", help="Reject unresolved handoff-blocking records")
    args = parser.parse_args(argv)
    errors = validate_notes(Path(args.notes).resolve(), require_v2=args.require_v2, handoff=args.handoff)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} clarification readiness error(s)")
        return 1
    print(f"OK: clarification readiness {'handoff' if args.handoff else 'structure'} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
