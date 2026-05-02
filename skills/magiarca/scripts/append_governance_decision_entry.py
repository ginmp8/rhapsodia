#!/usr/bin/env python3
"""Append a material Magiarca governance decision entry without rewriting history."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path


VALID_STATUSES = {"accepted", "superseded", "deprecated", "corrected"}
REQUIRED_FIELDS = (
    "Status",
    "Decision",
    "Context",
    "Reason",
    "Alternatives",
    "Impact",
    "Decision Maker",
    "Links",
    "Supersedes",
)


def normalize_multivalue(values: list[str] | None) -> str:
    if not values:
        return "none"
    cleaned = [value.strip() for value in values if value.strip()]
    return "; ".join(cleaned) if cleaned else "none"


def ensure_scaffold(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Governance Decisions\n\n## Entries\n\nNo governance decisions recorded.\n", encoding="utf-8")


def build_entry(args: argparse.Namespace) -> str:
    entry_date = args.date
    title = args.title.strip()
    status = args.status.strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")

    try:
        date.fromisoformat(entry_date)
    except ValueError as exc:
        raise ValueError("date must use YYYY-MM-DD format") from exc

    values = {
        "Status": status,
        "Decision": args.decision.strip(),
        "Context": args.context.strip(),
        "Reason": args.reason.strip(),
        "Alternatives": normalize_multivalue(args.alternative),
        "Impact": args.impact.strip(),
        "Decision Maker": args.decision_maker.strip(),
        "Links": normalize_multivalue(args.link),
        "Supersedes": args.supersedes.strip(),
    }

    missing = [label for label, value in values.items() if not value]
    if not title:
        missing.append("title")
    if missing:
        raise ValueError(f"missing required value(s): {', '.join(missing)}")

    lines = [f"### {entry_date} - {title}", ""]
    for label in REQUIRED_FIELDS:
        lines.append(f"- {label}: {values[label]}")
    return "\n".join(lines) + "\n"


def append_entry(path: Path, entry: str) -> None:
    ensure_scaffold(path)
    text = path.read_text(encoding="utf-8")
    if "## Entries" not in text.splitlines():
        raise ValueError("governance-decisions.md must contain `## Entries`")

    text = text.replace("\nNo governance decisions recorded.\n", "\n")
    rendered = text.rstrip() + "\n\n" + entry
    path.write_text(rendered, encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Append a material Magiarca governance decision to governance-decisions.md.")
    parser.add_argument("path", help="Path to governance-decisions.md.")
    parser.add_argument("--title", required=True, help="governance decision title, stated as the chosen outcome.")
    parser.add_argument("--decision", required=True, help="What was decided.")
    parser.add_argument("--context", required=True, help="Forces or constraints that made the decision necessary.")
    parser.add_argument("--reason", required=True, help="Why this option was chosen.")
    parser.add_argument("--impact", required=True, help="Roadmap, delivery, stakeholder, or handoff impact.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Decision date in YYYY-MM-DD format.")
    parser.add_argument("--status", default="accepted", help="accepted, superseded, deprecated, or corrected.")
    parser.add_argument("--decision-maker", default="unknown", help="Person, group, role, or unknown.")
    parser.add_argument("--alternative", action="append", help="Alternative considered. May be repeated.")
    parser.add_argument("--link", action="append", help="Related RFC, artifact, ticket, PR, or note. May be repeated.")
    parser.add_argument("--supersedes", default="none", help="Previous governance decision this supersedes, or none.")
    args = parser.parse_args(argv)

    try:
        entry = build_entry(args)
        append_entry(Path(args.path).resolve(), entry)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"OK: appended governance decision entry to {Path(args.path).resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

