#!/usr/bin/env python3
"""Validate content contracts for triggered MAGO planning artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ARTIFACT_HEADINGS: dict[str, tuple[str, ...]] = {
    "complexity-reduction-plan.md": (
        "## Scope",
        "## Preserved behavior",
        "## Non-goals",
        "## Evidence inspected",
        "## Complexity inventory",
        "## Simplification hypotheses",
        "## Target end-state",
        "## Phased task plan for Magia",
        "## ADR / decision triggers",
        "## Open questions and blockers",
        "## Handoff instructions",
    ),
    "contract-spec.md": (
        "## Scope",
        "## Producer and Consumers",
        "## Intended Contract",
        "## Compatibility",
        "## Validation Expectations for Magia",
        "## Open Questions",
    ),
    "migration-strategy.md": (
        "## Scope",
        "## Intended Change",
        "## Rollout Sequence",
        "## Compatibility",
        "## Rollback Strategy",
        "## Validation Expectations for Magia",
        "## Risks",
    ),
    "observability-design.md": (
        "## Scope",
        "## Required Logs",
        "## Required Metrics",
        "## Required Traces",
        "## Dashboards and Alerts",
        "## Validation Expectations for Magia",
    ),
    "operational-requirements.md": (
        "## Scope",
        "## Required Operations",
        "## Support Expectations",
        "## Runbook Expectations for Magia",
        "## Risks",
    ),
    "execution-handoff-plan.md": (
        "## Scope",
        "## Planned Execution Strategy",
        "## Expected Code or Documentation Areas",
        "## Sequence",
        "## Non-Goals",
        "## Validation Expectations",
        "## Risks and Trade-Offs",
        "## Handoff to Magia",
    ),
    "open-questions.md": (
        "## Scope",
        "## Questions",
        "## Blockers",
        "## Assumptions Until Resolved",
    ),
    "adr.md": (
        "## Status",
        "## Context",
        "## Decision",
        "## Alternatives Considered",
        "## Consequences",
        "## Evidence",
        "## Validation Expectations",
        "## Owner",
        "## Links",
    ),
}


SECTION_RE = re.compile(r"^##\s+.+$", re.MULTILINE)
TOKEN_RE = re.compile(r"<[A-Za-z0-9_|.-]+>")
UNRESOLVED_RE = re.compile(r"(?im)(?:`?unknown`?|\bTBD\b|\bTO[D]O\b|replace with actua[l]|this is a " + "placeholder)")


def section_content(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return ""
    collected: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{path}: missing file"]
    required = ARTIFACT_HEADINGS.get(path.name)
    if required is None:
        return [f"{path}: no triggered-artifact contract is registered for `{path.name}`"]

    text = path.read_text(encoding="utf-8-sig")
    headings = {line.strip() for line in text.splitlines() if line.startswith("## ")}
    for heading in required:
        if heading not in headings:
            errors.append(f"{path}: missing heading `{heading}`")
        elif not section_content(text, heading):
            errors.append(f"{path}: section `{heading}` must contain explicit planning content")

    tokens = sorted(set(TOKEN_RE.findall(text)))
    if tokens:
        errors.append(f"{path}: contains unresolved template token(s): {', '.join(tokens)}")
    unresolved = sorted(set(match.group(0) for match in UNRESOLVED_RE.finditer(text)))
    if unresolved:
        errors.append(f"{path}: contains unresolved value(s): {', '.join(unresolved)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate triggered MAGO planning artifacts.")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)

    errors: list[str] = []
    for raw in args.paths:
        errors.extend(validate(Path(raw).resolve()))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1
    print(f"OK: validated {len(args.paths)} triggered artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
