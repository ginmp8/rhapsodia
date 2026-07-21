#!/usr/bin/env python3
"""Validate provenance metadata on generated human-readable Nomia projections."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ("Authority", "Generated From", "Generated At", "Evidence As Of")
FIELD_RE = re.compile(r"^- (?P<field>Authority|Generated From|Generated At|Evidence As Of):\s*(?P<value>.+?)\s*$", re.MULTILINE)
ALLOWED_AUTHORITIES = {"nomia-projection", "non-authoritative-draft"}


def iso_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"{path}: missing projection file"]
    text = path.read_text(encoding="utf-8")
    if "## Projection Metadata" not in text:
        return [f"{path}: missing heading `## Projection Metadata`"]
    fields = {match.group("field"): match.group("value").strip() for match in FIELD_RE.finditer(text)}
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in fields or fields[field] in {"", "unknown", "null"}:
            errors.append(f"{path}: projection metadata field `{field}` must be resolved")
    authority = fields.get("Authority")
    if authority and authority not in ALLOWED_AUTHORITIES:
        errors.append(f"{path}: Authority must be one of {sorted(ALLOWED_AUTHORITIES)}")
    for field in ("Generated At", "Evidence As Of"):
        value = fields.get(field)
        if value and not iso_timestamp(value):
            errors.append(f"{path}: `{field}` must use ISO-8601")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Nomia projection provenance metadata.")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)
    errors = [error for raw in args.paths for error in validate(Path(raw).resolve())]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: validated projection metadata for {len(args.paths)} artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
