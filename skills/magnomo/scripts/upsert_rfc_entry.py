#!/usr/bin/env python3
"""Create or update a Magnomo RFC proposal entry by stable proposal id."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


PROPOSAL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_STATUSES = {"draft", "in_review", "accepted", "rejected", "deferred", "superseded"}
VALID_IMPACTS = {"high", "medium", "low"}
REQUIRED_FIELDS = (
    "Status",
    "Impact",
    "Driver",
    "Approvers",
    "Contributors",
    "Informed",
    "Due Date",
    "Background",
    "Assumptions",
    "Decision Criteria",
    "Options",
    "Recommendation",
    "Outcome",
    "Links",
)


def normalize_multivalue(values: list[str] | None, *, default: str = "none") -> str:
    if not values:
        return default
    cleaned = [value.strip() for value in values if value.strip()]
    return "; ".join(cleaned) if cleaned else default


def ensure_scaffold(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# RFC Proposals\n\n## Entries\n\nNo RFC proposals recorded.\n", encoding="utf-8")


def validate_due_date(value: str) -> None:
    if value == "unknown":
        return
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("due-date must use YYYY-MM-DD format or `unknown`") from exc


def build_entry(args: argparse.Namespace) -> str:
    proposal_id = args.proposal_id.strip()
    if not PROPOSAL_ID_RE.match(proposal_id):
        raise ValueError("proposal-id must be lowercase hyphen-case")

    title = args.title.strip()
    status = args.status.strip().lower()
    impact = args.impact.strip().lower()
    due_date = args.due_date.strip()
    validate_due_date(due_date)

    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
    if impact not in VALID_IMPACTS:
        raise ValueError(f"impact must be one of {sorted(VALID_IMPACTS)}")
    if len(args.option or []) < 2:
        raise ValueError("at least two --option values are required")

    values = {
        "Status": status,
        "Impact": impact,
        "Driver": args.driver.strip(),
        "Approvers": normalize_multivalue(args.approver, default="unknown"),
        "Contributors": normalize_multivalue(args.contributor),
        "Informed": normalize_multivalue(args.informed),
        "Due Date": due_date,
        "Background": args.background.strip(),
        "Assumptions": normalize_multivalue(args.assumption, default="unknown"),
        "Decision Criteria": normalize_multivalue(args.criterion, default="unknown"),
        "Options": normalize_multivalue(args.option),
        "Recommendation": args.recommendation.strip(),
        "Outcome": args.outcome.strip(),
        "Links": normalize_multivalue(args.link),
    }

    missing = [label for label, value in values.items() if not value]
    if not title:
        missing.append("title")
    if missing:
        raise ValueError(f"missing required value(s): {', '.join(missing)}")

    lines = [f"### {proposal_id} - {title}", ""]
    for label in REQUIRED_FIELDS:
        lines.append(f"- {label}: {values[label]}")
    return "\n".join(lines) + "\n"


def upsert_entry(path: Path, proposal_id: str, entry: str) -> None:
    ensure_scaffold(path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if "## Entries" not in lines:
        raise ValueError("rfc-proposals.md must contain `## Entries`")

    text = text.replace("\nNo RFC proposals recorded.\n", "\n")
    lines = text.splitlines()
    heading_prefix = f"### {proposal_id} - "
    entry_starts = [index for index, line in enumerate(lines) if line.startswith("### ")]
    target_start = next((index for index in entry_starts if lines[index].startswith(heading_prefix)), None)

    if target_start is None:
        rendered = text.rstrip() + "\n\n" + entry
        path.write_text(rendered, encoding="utf-8")
        return

    following = [index for index in entry_starts if index > target_start]
    target_end = following[0] if following else len(lines)
    replacement = entry.rstrip().splitlines()
    rendered_lines = lines[:target_start] + replacement + lines[target_end:]
    path.write_text("\n".join(rendered_lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create or update a Magnomo RFC proposal in rfc-proposals.md.")
    parser.add_argument("path", help="Path to rfc-proposals.md.")
    parser.add_argument("--proposal-id", required=True, help="Stable lowercase hyphen-case proposal id.")
    parser.add_argument("--title", required=True, help="RFC title.")
    parser.add_argument("--background", required=True, help="Current state, problem, why now, and cost of not deciding.")
    parser.add_argument("--driver", required=True, help="Person or role driving the proposal.")
    parser.add_argument("--option", action="append", required=True, help="Option considered. Repeat at least twice.")
    parser.add_argument("--status", default="draft", help="draft, in_review, accepted, rejected, deferred, or superseded.")
    parser.add_argument("--impact", default="medium", help="high, medium, or low.")
    parser.add_argument("--approver", action="append", help="Approver. May be repeated.")
    parser.add_argument("--contributor", action="append", help="Contributor. May be repeated.")
    parser.add_argument("--informed", action="append", help="Informed stakeholder or group. May be repeated.")
    parser.add_argument("--due-date", default="unknown", help="YYYY-MM-DD or unknown.")
    parser.add_argument("--assumption", action="append", help="Assumption with confidence/invalidation trigger when known.")
    parser.add_argument("--criterion", action="append", help="Decision criterion in priority order. May be repeated.")
    parser.add_argument("--recommendation", default="unknown", help="Recommended option or unknown.")
    parser.add_argument("--outcome", default="pending", help="Decision outcome; keep pending until decided.")
    parser.add_argument("--link", action="append", help="Related roadmap, spec, ticket, Architecture Decision Record, or note. May be repeated.")
    args = parser.parse_args(argv)

    try:
        entry = build_entry(args)
        upsert_entry(Path(args.path).resolve(), args.proposal_id.strip(), entry)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"OK: upserted RFC proposal in {Path(args.path).resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

