#!/usr/bin/env python3
"""Deterministic structural checks for systematic-debugging package policy."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REQUIRED_TOP100 = [
    "## At a Glance",
    "## Activation Boundary",
    "## Core Contract",
    "## Failure-Class Router",
    "## Workflow at a Glance",
    "## Control Model",
    "## Causal Confidence",
    "## Critical Invariants and Diagnostic Safety",
    "## Stop Conditions",
    "## Direct Resource Map",
]
PREVIEW_FIELDS = ("**Purpose:**", "**Load when:**", "**Decision impact:**")


def fail(code: str, subject: str, evidence: str) -> dict:
    return {"code": code, "subject": subject, "evidence": evidence, "severity": "error"}


def main() -> int:
    findings: list[dict] = []
    text = SKILL.read_text(encoding="utf-8")
    lines = text.splitlines()
    top = "\n".join(lines[:100])

    if not text.startswith("---\n") or "\nname: systematic-debugging\n" not in text[:1200]:
        findings.append(fail("frontmatter", "SKILL.md", "missing canonical frontmatter/name"))

    for marker in REQUIRED_TOP100:
        if marker not in top:
            findings.append(fail("top100", "SKILL.md", f"missing from first 100 lines: {marker}"))

    md_links = re.findall(r"\[[^\]]+\]\(([^)#]+\.md)\)", text)
    for rel in sorted(set(md_links)):
        target = (ROOT / rel).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            findings.append(fail("reference-escape", rel, "reference resolves outside skill root"))
            continue
        if not target.is_file():
            findings.append(fail("broken-reference", rel, "referenced Markdown does not exist"))

    # All authored supporting Markdown >100 lines needs decision-useful preview and Contents.
    for p in sorted(ROOT.rglob("*.md")):
        if p == SKILL:
            continue
        content = p.read_text(encoding="utf-8")
        ls = content.splitlines()
        if len(ls) <= 100:
            continue
        early = "\n".join(ls[:40])
        missing = [f for f in PREVIEW_FIELDS if f not in early]
        if missing:
            findings.append(fail("long-md-preview", str(p.relative_to(ROOT)), "missing early fields: " + ", ".join(missing)))
        if not re.search(r"^## (Contents|Table of Contents|Section Map)\s*$", early, re.M):
            findings.append(fail("long-md-contents", str(p.relative_to(ROOT)), "missing early Contents/section map"))

    for p in (ROOT / "evals").glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            findings.append(fail("eval-json", str(p.relative_to(ROOT)), str(exc)))
            continue
        if data.get("schema_version") != 1 or not isinstance(data.get("scenarios"), list) or not data["scenarios"]:
            findings.append(fail("eval-shape", str(p.relative_to(ROOT)), "requires schema_version=1 and non-empty scenarios"))

    result = {
        "validator": "systematic-debugging.validate_skill.v1",
        "status": "pass" if not findings else "fail",
        "findings": findings,
        "top100_line_count_checked": min(100, len(lines)),
        "skill_line_count": len(lines),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
