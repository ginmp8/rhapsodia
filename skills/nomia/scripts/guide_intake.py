#!/usr/bin/env python3
"""Produce deterministic, non-authoritative guidance from partial governance intake evidence."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to guide Nomia intake") from exc

from nomia_utils import atomic_write_text, validate_id_provenance, validate_spec_id_format

PROFILES = {"quick", "standard", "governed"}
LIFECYCLES = {"intake", "triage", "commit", "track", "decide", "close"}
GOVERNED_TRIGGERS = {
    "regulatory",
    "financial",
    "privacy",
    "security",
    "contractual",
    "executive",
    "cross_organization",
    "irreversible",
    "stale_evidence",
    "conflicting_evidence",
}
CLAIM_TYPES = {"fact", "opinion", "hypothesis", "commitment"}


def dotted(data: dict[str, Any], *paths: str, default: Any = None) -> Any:
    for path in paths:
        current: Any = data
        found = True
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                found = False
                break
            current = current[part]
        if found:
            return current
    return default


def missing(value: Any) -> bool:
    return value in (None, "", "unknown") or value == []


def load_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("intake input must be a YAML or JSON mapping")
    return data


def normalized_triggers(data: dict[str, Any]) -> list[str]:
    values = dotted(data, "risk_triggers", "governance.risk_triggers", default=[]) or []
    if not isinstance(values, list):
        return ["invalid:risk_triggers"]
    return sorted({str(item).strip().lower().replace("-", "_") for item in values if str(item).strip()})


def classify_claims(data: dict[str, Any]) -> dict[str, int]:
    counts = {claim_type: 0 for claim_type in sorted(CLAIM_TYPES)}
    invalid = 0
    claims = data.get("claims") or []
    if not isinstance(claims, list):
        return {**counts, "invalid": 1}
    for claim in claims:
        claim_type = claim.get("type") if isinstance(claim, dict) else None
        if claim_type in CLAIM_TYPES:
            counts[str(claim_type)] += 1
        else:
            invalid += 1
    return {**counts, "invalid": invalid}


def build_guidance(data: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "problem": dotted(data, "problem", "request.problem", "request.context"),
        "evidence": dotted(data, "evidence", "request.evidence", "request.source"),
        "requester": dotted(data, "requester", "request.requester"),
        "affected": dotted(data, "affected", "request.affected"),
        "outcome": dotted(data, "outcome", "request.outcome"),
        "rationale": dotted(data, "rationale", "request.rationale"),
        "urgency": dotted(data, "urgency", "business_priority.urgency"),
        "target_date": dotted(data, "target_date", "planning.target_date"),
        "owner": dotted(data, "owner", "ownership.owner"),
        "stakeholders": dotted(data, "stakeholders", "ownership.stakeholders", default=[]),
        "decision_maker": dotted(data, "decision_maker", "ownership.decision_maker"),
        "dependencies": dotted(data, "dependencies", default=[]),
        "business_risks": dotted(data, "business_risks", "risks", default=[]),
        "constraints": dotted(data, "constraints", default=[]),
        "scope": dotted(data, "scope"),
        "non_goals": dotted(data, "non_goals", default=[]),
        "decision_needed": dotted(data, "decision_needed", "decision.current"),
    }
    triggers = normalized_triggers(data)
    governed_reasons = sorted(trigger for trigger in triggers if trigger in GOVERNED_TRIGGERS)
    explicit_profile = dotted(data, "profile", "governance.profile")
    low_risk = dotted(data, "low_risk", default=False) is True
    if governed_reasons:
        profile = "governed"
    elif explicit_profile in PROFILES:
        profile = str(explicit_profile)
    elif low_risk:
        profile = "quick"
    else:
        profile = "standard"

    blocking_questions: list[str] = []
    if missing(fields["problem"]):
        blocking_questions.append("What problem or request must governance capture?")
    if missing(fields["outcome"]):
        blocking_questions.append("What observable business outcome is expected?")
    if missing(fields["evidence"]):
        blocking_questions.append("Which current source supports this intake?")
    if "invalid:risk_triggers" in triggers:
        blocking_questions.append("Which explicit risk triggers apply as a list?")

    explicit_lifecycle = dotted(data, "lifecycle", "governance.lifecycle")
    if explicit_lifecycle in LIFECYCLES:
        lifecycle = str(explicit_lifecycle)
    elif blocking_questions:
        lifecycle = "intake"
    elif missing(fields["owner"]) or missing(fields["requester"]) or missing(fields["decision_needed"]):
        lifecycle = "triage"
    else:
        lifecycle = "commit"
    mode = "delivery-intake" if lifecycle == "intake" else "delivery-triage"

    non_blocking_questions: list[str] = []
    prompts = {
        "requester": "Who requested the change, or should requester remain unknown?",
        "affected": "Which users, teams, or processes are affected?",
        "owner": "Who owns the governance follow-through, or is ownership still unknown?",
        "stakeholders": "Which stakeholders must be consulted or informed?",
        "target_date": "Is there an evidenced target date or only urgency?",
        "dependencies": "Which business dependencies are already evidenced?",
        "business_risks": "Which business risks are known, and who can accept them?",
        "constraints": "Which policy, budget, vendor, or process constraints apply?",
        "scope": "What is explicitly in scope?",
        "non_goals": "What is explicitly out of scope?",
        "decision_needed": "Which governance decision is required next?",
    }
    for key, question in prompts.items():
        if missing(fields[key]):
            non_blocking_questions.append(question)

    spec_id = dotted(data, "spec_id")
    spec_id_provenance = dotted(data, "spec_id_provenance")
    identity_issues: list[str] = []
    format_error = validate_spec_id_format(spec_id)
    if format_error:
        identity_issues.append(format_error)
    provenance_error = validate_id_provenance(
        spec_id_provenance, id_value=spec_id, field_name="spec_id_provenance"
    )
    if provenance_error:
        identity_issues.append(provenance_error)

    repository_write_requested = dotted(data, "repository_write", default=False) is True
    repository_fields = {
        "BOARD_ROOT": dotted(data, "BOARD_ROOT", "board_root"),
        "board_id": dotted(data, "board_id"),
        "year": dotted(data, "year"),
        "cycle_id": dotted(data, "cycle_id"),
        "spec_id": spec_id,
        "spec_id_provenance": spec_id_provenance,
    }
    missing_repository_fields = [key for key, value in repository_fields.items() if missing(value)]
    repository_write_ready = (
        repository_write_requested
        and not missing_repository_fields
        and not identity_issues
        and not blocking_questions
    )

    ready_for_mago = (
        not blocking_questions
        and not missing(fields["outcome"])
        and not missing(fields["scope"])
        and not governed_reasons
        and not identity_issues
    )
    if blocking_questions:
        next_action = "Resolve blocking intake questions; keep any output as a non-authoritative draft."
        next_skill = "nomia"
    elif fields["decision_needed"] not in (None, "", "unknown", False):
        next_action = "Prepare a decision-ready governance brief from canonical or attributed facts."
        next_skill = "nomia"
    elif ready_for_mago:
        next_action = "Validate a typed Nomia-to-Mago handoff; do not create technical planning artifacts."
        next_skill = "mago"
    else:
        next_action = "Create or refine the minimal governance intake and preserve unresolved facts as unknown."
        next_skill = "nomia"

    unknown_fields = sorted(key for key, value in fields.items() if missing(value))
    known_facts = {key: value for key, value in fields.items() if not missing(value)}
    return {
        "status": "pass",
        "authority": "non_authoritative_guidance",
        "profile": profile,
        "escalation_reasons": governed_reasons,
        "lifecycle": lifecycle,
        "mode": mode,
        "known_facts": known_facts,
        "unknown_fields": unknown_fields,
        "blocking_questions": blocking_questions[:3],
        "non_blocking_questions": non_blocking_questions,
        "claim_classification": classify_claims(data),
        "identity_issues": identity_issues,
        "repository_write": {
            "requested": repository_write_requested,
            "ready": repository_write_ready,
            "missing_fields": missing_repository_fields,
        },
        "mago_handoff_candidate": {
            "ready_for_validation": ready_for_mago,
            "note": "Candidate readiness is guidance only; the typed handoff validator remains authoritative.",
        },
        "next_action": next_action,
        "next_responsible_skill": next_skill,
        "rules": [
            "Do not invent requester, owner, target date, stakeholders, identities, status, or evidence.",
            "Governance readiness does not certify planning, execution, validation, or release.",
            "Technical discovery and planning must be handed to Mago; implementation evidence belongs to Magia.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="YAML or JSON mapping containing partial intake evidence")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args(argv)
    try:
        guidance = build_guidance(load_mapping(Path(args.input)))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(guidance, indent=2, sort_keys=True) + "\n"
    if args.output:
        atomic_write_text(Path(args.output), text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
