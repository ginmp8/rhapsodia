#!/usr/bin/env python3
"""Validate current MAGO prose against canonical ecosystem contracts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CANONICAL_FIELDS = ("business_priority", "technical_criticality", "execution_sequence")
LEGACY_ACCEPT_RE = re.compile(
    r"legacy[^\n.]*(accepted|supported|compatibility\s+(?:mode|switch)|normaliz(?:e|ed|ation)\s+before\s+validation)",
    re.IGNORECASE,
)
NEGATED_RE = re.compile(
    r"not accepted|unsupported|reject|rejected|must not|never|no runtime compatibility",
    re.IGNORECASE,
)
ALIAS_RE = re.compile(r"(?<!business_)\bpriority\b|\border[ _-]?hint\b", re.IGNORECASE)
ALIAS_REJECTION_RE = re.compile(
    r"unsupported|reject|rejected|must not|never|migration|generic fields?|aliases?",
    re.IGNORECASE,
)


def read_required(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def load_object(root: Path, relative: str, errors: list[str]) -> dict[str, Any]:
    text = read_required(root, relative, errors)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid {relative}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{relative} must contain a JSON object")
        return {}
    return value


def collect_errors(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    handoff_json = load_object(root, "references/ecosystem-handoff-contract.json", errors)
    priority_json = load_object(root, "references/priority-contract.json", errors)
    compatibility_json = load_object(root, "references/ecosystem-compatibility.json", errors)

    handoff_compatibility = handoff_json.get("compatibility") or {}
    if handoff_compatibility.get("classification") != "breaking-no-legacy":
        errors.append("handoff contract must remain breaking-no-legacy")
    if handoff_compatibility.get("legacy_read_support") is not False:
        errors.append("handoff contract must keep legacy_read_support false")

    priority_compatibility = priority_json.get("compatibility") or {}
    if priority_compatibility.get("classification") != "breaking-no-legacy":
        errors.append("priority contract must remain breaking-no-legacy")
    if priority_compatibility.get("legacy_read_support") is not False:
        errors.append("priority contract must keep legacy_read_support false")
    if priority_compatibility.get("rejected_fields") != ["priority", "order_hint"]:
        errors.append("priority contract must reject priority and order_hint")

    policy = compatibility_json.get("policy") or {}
    if policy.get("classification") != "coordinated-exact":
        errors.append("ecosystem compatibility must remain coordinated-exact")
    if policy.get("mixed_versions_allowed") is not False:
        errors.append("ecosystem compatibility must reject mixed versions")

    handoff_md = read_required(root, "references/ecosystem-handoff-contract.md", errors)
    required_handoff_phrases = (
        "Legacy aliases and envelopes are rejected",
        "There is no runtime compatibility switch for pre-v2 envelopes",
        "adaptation must occur before a handoff is built",
    )
    for phrase in required_handoff_phrases:
        if phrase.lower() not in handoff_md.lower():
            errors.append(f"ecosystem handoff prose missing required rule: {phrase}")
    for number, line in enumerate(handoff_md.splitlines(), start=1):
        if LEGACY_ACCEPT_RE.search(line) and not NEGATED_RE.search(line):
            errors.append(f"ecosystem handoff prose describes legacy compatibility as accepted at line {number}")

    priority_md = read_required(root, "references/priority-contract.md", errors)
    for field in CANONICAL_FIELDS:
        if field not in priority_md:
            errors.append(f"priority prose must name canonical field {field}")
    required_priority_phrases = (
        "Every package must reject the generic fields `priority` and `order_hint`",
        "Migration must be explicit and external",
        "No implicit mapping is allowed",
    )
    for phrase in required_priority_phrases:
        if phrase.lower() not in priority_md.lower():
            errors.append(f"priority prose missing required rule: {phrase}")

    ownership_md = read_required(root, "references/shared-artifact-ownership.md", errors)
    for field in CANONICAL_FIELDS:
        if field not in ownership_md:
            errors.append(f"shared artifact ownership must name canonical field {field}")
    for number, line in enumerate(ownership_md.splitlines(), start=1):
        for match in ALIAS_RE.finditer(line):
            context = line[max(0, match.start() - 140):match.end() + 80]
            if not ALIAS_REJECTION_RE.search(context):
                errors.append(
                    f"shared artifact ownership preserves or uses unsupported generic priority alias at line {number}"
                )
                break

    compatibility_md = read_required(root, "references/ecosystem-compatibility.md", errors)
    required_compatibility_phrases = (
        "Mixed package versions are rejected before mutation or handoff consumption",
        "Changelog entries are documentation and are not compatibility aliases or migration inputs",
    )
    for phrase in required_compatibility_phrases:
        if phrase.lower() not in compatibility_md.lower():
            errors.append(f"ecosystem compatibility prose missing required rule: {phrase}")

    release_md = read_required(root, "references/installation-and-release.md", errors)
    release_lower = release_md.lower()
    if "legacy runtime path is permitted only when the machine-readable compatibility contract explicitly enables it" not in release_lower:
        errors.append("release guidance must condition legacy runtime support on the machine-readable contract")
    if "current handoff and priority v2 contracts do not enable legacy runtime support" not in release_lower:
        errors.append("release guidance must explicitly reject legacy runtime support for current contracts")

    skill_md = read_required(root, "SKILL.md", errors)
    for phrase in ("reject mixed ecosystem versions before mutation", "unsupported envelope schemas"):
        if phrase.lower() not in skill_md.lower():
            errors.append(f"SKILL.md missing ecosystem fail-closed rule: {phrase}")

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
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
