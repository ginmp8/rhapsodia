#!/usr/bin/env python3
"""Validate a Nomia canonical governance record and generate deterministic projections."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to project Nomia governance views") from exc

from governance_contract import (
    GOVERNANCE_STATES,
    LIFECYCLE_VALUES,
    PROFILE_VALUES,
    RELEASE_STATES,
    STATE_VALUES_BY_DIMENSION,
    parse_timestamp,
    validate_non_unknown_enum,
    validate_release_state,
    validate_technical_state,
)
from nomia_utils import atomic_write_text, validate_id_provenance, validate_spec_id_format

PROFILES = PROFILE_VALUES
LIFECYCLE = LIFECYCLE_VALUES
GOV_STATES = GOVERNANCE_STATES
PLANNING_STATES = STATE_VALUES_BY_DIMENSION["planning"]
EXECUTION_STATES = STATE_VALUES_BY_DIMENSION["execution"]
VALIDATION_STATES = STATE_VALUES_BY_DIMENSION["validation"]
RELEASE_STATES = RELEASE_STATES


def json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def missing(value: Any) -> bool:
    return value is None or value == "" or value == "unknown" or value == []


def business_priority_value(data: dict[str, Any], field: str, default: Any = None) -> Any:
    value = data.get("business_priority")
    if isinstance(value, dict):
        return value.get(field, default)
    return default


def dotted(data: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return default
        current = current.get(part, default)
    return current


def validate_record(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["record must be a YAML mapping"], warnings

    required_sections = (
        "schema_version",
        "spec_id",
        "spec_id_provenance",
        "request",
        "ownership",
        "planning",
        "status",
        "blockers",
        "risks",
        "links",
        "governance",
        "technical_state",
        "release",
        "dependencies",
        "decision",
        "handoffs",
        "provenance",
        "privacy",
    )
    for key in required_sections:
        if key not in data:
            errors.append(f"missing canonical section: {key}")
    if "priority" in data:
        errors.append("unsupported generic section: priority")
    if "business_priority" not in data:
        errors.append("missing canonical section: business_priority")

    if data.get("schema_version") != 2:
        errors.append("schema_version must be 2 for canonical projections; adapt legacy schema_version 1 first")
    from validate_artifact_privacy import validate_block as validate_privacy_block
    errors.extend(validate_privacy_block(data.get("privacy"), Path(__file__).resolve().parents[1]))

    spec_id = data.get("spec_id")
    if validate_spec_id_format(spec_id):
        errors.append("spec_id must use spec-YYYY-MM-DD-feature-key")
    provenance_error = validate_id_provenance(
        data.get("spec_id_provenance"), id_value=spec_id, field_name="spec_id_provenance"
    )
    if provenance_error:
        errors.append(provenance_error)

    governance = data.get("governance")
    if not isinstance(governance, dict):
        errors.append("governance must be a mapping")
        governance = {}
    errors.extend(validate_non_unknown_enum("governance.profile", governance.get("profile"), PROFILES))
    errors.extend(validate_non_unknown_enum("governance.lifecycle", governance.get("lifecycle"), LIFECYCLE))
    errors.extend(validate_non_unknown_enum("governance.status", governance.get("status"), GOV_STATES))

    status = data.get("status") if isinstance(data.get("status"), dict) else {}
    legacy_state = str(status.get("state") or "unknown")
    canonical_state_value = str(governance.get("status") or "unknown")
    if legacy_state not in {"unknown", canonical_state_value}:
        errors.append("status.state conflicts with governance.status; legacy state must be adapted explicitly")

    technical_state = data.get("technical_state")
    if not isinstance(technical_state, dict):
        errors.append("technical_state must be a mapping")
        technical_state = {}
    for dimension in ("planning", "execution", "validation"):
        errors.extend(validate_technical_state(dimension, technical_state.get(dimension)))

    errors.extend(validate_release_state(data.get("release")))

    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("dependencies must be a list")
    decision = data.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be a mapping")
    handoffs = data.get("handoffs")
    if not isinstance(handoffs, dict):
        errors.append("handoffs must be a mapping")

    provenance = data.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be a mapping")
        provenance = {}
    if parse_timestamp(provenance.get("updated_at")) is None:
        errors.append("provenance.updated_at is required and must be ISO-8601")
    if not isinstance(provenance.get("facts"), dict):
        errors.append("provenance.facts must be a mapping")
    if not isinstance(provenance.get("changes"), list):
        errors.append("provenance.changes must be a list")

    for field in ("request.requester", "ownership.owner", "planning.target_date", "status.updated_at"):
        if missing(dotted(data, field)):
            warnings.append(f"unknown fact: {field}")
    return errors, warnings


def evidence_age(data: dict[str, Any], today: date) -> tuple[list[str], list[str]]:
    stale: list[str] = []
    conflicts: list[str] = []
    facts = dotted(data, "provenance.facts", {}) or {}
    for field, metadata in facts.items():
        if not isinstance(metadata, dict):
            continue
        if metadata.get("conflict"):
            conflicts.append(field)
        observed = metadata.get("observed_at")
        max_age = metadata.get("max_age_days")
        if observed and isinstance(max_age, int):
            parsed = parse_timestamp(observed)
            if parsed is None:
                conflicts.append(f"{field}:invalid_observed_at")
            elif (today - parsed.date()).days > max_age:
                stale.append(field)
    return sorted(stale), sorted(conflicts)


def canonical_state(data: dict[str, Any]) -> str:
    return str(dotted(data, "governance.status") or "unknown")


def safe_completion(data: dict[str, Any]) -> dict[str, str]:
    return {
        "planning": str(dotted(data, "technical_state.planning.state") or "unknown"),
        "execution": str(dotted(data, "technical_state.execution.state") or "unknown"),
        "validation": str(dotted(data, "technical_state.validation.state") or "unknown"),
        "release": str(dotted(data, "release.state") or "unknown"),
    }


def list_summary(items: Any, field: str = "summary") -> list[str]:
    result: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            result.append(str(item.get(field) or item.get("id") or "unknown"))
        elif item not in (None, ""):
            result.append(str(item))
    return result


def evidence_health(stale: list[str], conflicts: list[str], unknown: list[str]) -> str:
    if conflicts:
        return "conflicting"
    if stale:
        return "stale"
    if unknown:
        return "incomplete"
    return "current"


def next_responsible_skill(data: dict[str, Any], stale: list[str], conflicts: list[str]) -> str:
    lifecycle = str(dotted(data, "governance.lifecycle") or "unknown")
    decision = dotted(data, "decision.current")
    planning = str(dotted(data, "technical_state.planning.state") or "unknown")
    execution = str(dotted(data, "technical_state.execution.state") or "unknown")
    validation = str(dotted(data, "technical_state.validation.state") or "unknown")
    release = str(dotted(data, "release.state") or "unknown")
    if stale or conflicts or lifecycle in {"intake", "triage", "commit", "decide"} or decision not in (None, "", "unknown"):
        return "nomia"
    if planning not in {"ready", "complete"}:
        return "mago"
    if execution != "complete" or validation != "passed":
        return "magia"
    if release not in {"released", "closed", "canceled", "superseded"}:
        return "nomia"
    return "nomia"


def next_governance_action(data: dict[str, Any], stale: list[str], conflicts: list[str]) -> str:
    lifecycle = str(dotted(data, "governance.lifecycle") or "unknown")
    decision = dotted(data, "decision.current")
    planning = str(dotted(data, "technical_state.planning.state") or "unknown")
    execution = str(dotted(data, "technical_state.execution.state") or "unknown")
    validation = str(dotted(data, "technical_state.validation.state") or "unknown")
    release = str(dotted(data, "release.state") or "unknown")
    if conflicts:
        return "Resolve conflicting evidence before changing any governed state."
    if stale:
        return "Refresh stale evidence before changing commitments or completion claims."
    if decision not in (None, "", "unknown"):
        return "Prepare or resolve the pending governance decision with the required authority."
    if lifecycle in {"intake", "triage"}:
        return "Refine the minimum governance intake and preserve unresolved facts as unknown."
    if planning not in {"ready", "complete"}:
        return "Validate the typed Nomia-to-Mago handoff; do not create technical planning artifacts."
    if execution != "complete" or validation != "passed":
        return "Await or request current attributed Magia execution and validation evidence."
    if release not in {"released", "closed", "canceled", "superseded"}:
        return "Evaluate governance release readiness without certifying technical validation."
    return "Close or supersede the governance record with final attributed evidence."


def build_audience_views(
    data: dict[str, Any],
    common: dict[str, Any],
    operational: dict[str, Any],
    stakeholder: dict[str, Any],
    executive: dict[str, Any],
    next_action: str,
) -> dict[str, dict[str, Any]]:
    request = dotted(data, "request.title") or "unknown"
    decision = dotted(data, "decision.current") or "unknown"
    risks = list_summary(data.get("risks"))
    blockers = list_summary(data.get("blockers"))
    dependencies = list_summary(data.get("dependencies"), "summary")
    minimal = {
        "authority": "non_authoritative_projection",
        "canonical_source": common["canonical_source"],
        "generated_at": common["generated_at"],
        "evidence_as_of": common["evidence_as_of"],
        "request": request,
        "state": common["state"],
        "target_date": common["target_date"],
        "unknown_fields": common["unknown_fields"],
        "stale_fields": common["stale_fields"],
        "conflicting_fields": common["conflicting_fields"],
        "decision_needed": decision,
        "next_action": next_action,
    }
    return {
        "requester": {**minimal, "owner": common["owner"], "blockers": blockers},
        "owner": {**operational, "next_action": next_action},
        "executive": {**executive, "decision_needed": decision, "next_action": next_action},
        "product": {**stakeholder, "dependencies": dependencies, "next_action": next_action},
        "engineering": {
            **minimal,
            "spec_id": data.get("spec_id"),
            "technical_state": common["technical_state"],
            "dependencies": dependencies,
            "boundary": "Technical planning belongs to Mago; execution evidence belongs to Magia.",
        },
        "operations": {**operational, "release_state": common["technical_state"]["release"], "next_action": next_action},
        "compliance": {
            **minimal,
            "profile": common["profile"],
            "material_risks": risks,
            "decision_authority": dotted(data, "ownership.decision_maker") or "unknown",
        },
        "risk": {**minimal, "material_risks": risks, "blockers": blockers},
        "external_partner": ({
            **minimal,
            "privacy": common.get("privacy"),
            "confidentiality_note": "Audit records, internal notes, and technical detail are intentionally excluded.",
        } if (common.get("privacy") or {}).get("external_share_allowed") is True
          and set((common.get("privacy") or {}).get("allowed_destinations") or []) & {"approved-vendor", "public"}
          else {
            "status": "blocked",
            "reason": "external sharing is not allowed by artifact privacy metadata",
            "canonical_source": common["canonical_source"],
            "privacy": common.get("privacy"),
          }),
    }


def build_views(data: dict[str, Any], source: str, generated_at: str) -> dict[str, Any]:
    generated = parse_timestamp(generated_at)
    if generated is None:
        raise ValueError("generated_at must be ISO-8601")
    today = generated.date()
    stale, conflicts = evidence_age(data, today)
    state = canonical_state(data)
    owner = dotted(data, "ownership.owner") or "unknown"
    target = dotted(data, "planning.target_date") or "unknown"
    blockers = list_summary(data.get("blockers"))
    risks = list_summary(data.get("risks"))
    dependencies = list_summary(data.get("dependencies"), "summary")
    completion = safe_completion(data)
    flags: list[str] = []
    if stale:
        flags.append("stale=" + ",".join(stale))
    if conflicts:
        flags.append("conflict=" + ",".join(conflicts))
    unknown = [
        field
        for field in ("request.requester", "ownership.owner", "planning.target_date", "status.updated_at")
        if missing(dotted(data, field))
    ]
    if unknown:
        flags.append("unknown=" + ",".join(unknown))
    detail = "; ".join(flags) if flags else "evidence current"
    top_issue = (blockers or risks or ["none evidenced"])[0]
    one_line = f"{state} | owner={owner} | target={target} | issue={top_issue} | {detail}"
    common = {
        "authority": "canonical_projection",
        "source": source,
        "canonical_source": source,
        "generated_at": generated.isoformat(),
        "evidence_as_of": dotted(data, "provenance.updated_at"),
        "profile": dotted(data, "governance.profile"),
        "lifecycle": dotted(data, "governance.lifecycle"),
        "state": state,
        "owner": owner,
        "target_date": target,
        "unknown_fields": unknown,
        "stale_fields": stale,
        "conflicting_fields": conflicts,
        "technical_state": completion,
        "privacy": copy.deepcopy(data.get("privacy")),
    }
    operational = {
        **common,
        "summary": dotted(data, "status.summary") or "unknown",
        "blockers": blockers,
        "risks": risks,
        "dependencies": dependencies,
        "next_governance_action": dotted(data, "decision.current") or "unknown",
    }
    stakeholder = {
        **common,
        "request": dotted(data, "request.title") or "unknown",
        "impact": business_priority_value(data, "impact") or "unknown",
        "decision_needed": dotted(data, "decision.current") or "unknown",
        "stakeholders": dotted(data, "ownership.stakeholders", []) or [],
    }
    executive = {
        **common,
        "business_priority": business_priority_value(data, "level") or "unknown",
        "confidence": dotted(data, "status.confidence") or "unknown",
        "material_risks": risks,
        "release_state": completion["release"],
        "completion_claim_supported": completion["validation"] == "passed"
        and completion["release"] in {"released", "closed"},
    }
    health = evidence_health(stale, conflicts, unknown)
    next_skill = next_responsible_skill(data, stale, conflicts)
    next_action = next_governance_action(data, stale, conflicts)
    lifecycle_status = {
        **common,
        "evidence_health": health,
        "state_authority": {
            "governance": "nomia",
            "planning": "mago",
            "execution": "magia",
            "validation": "magia",
            "release": "nomia with attributed technical and release evidence",
        },
        "blockers": blockers,
        "pending_decision": dotted(data, "decision.current") or "unknown",
        "handoff_status": {
            "mago": dotted(data, "handoffs.mago.state") or "unknown",
            "magia": dotted(data, "handoffs.magia.state") or "unknown",
        },
        "next_action": next_action,
        "next_responsible_skill": next_skill,
        "technical_certification": "not_provided_by_nomia",
    }
    decision_ready = {
        **common,
        "decision_required": dotted(data, "decision.current") or "unknown",
        "decision_state": dotted(data, "decision.state") or "unknown",
        "authority_required": dotted(data, "ownership.decision_maker") or "unknown",
        "context": dotted(data, "request.context") or "unknown",
        "business_alternatives": dotted(data, "decision.alternatives", []) or [],
        "decision_criteria": dotted(data, "decision.criteria", []) or [],
        "impact": business_priority_value(data, "impact") or "unknown",
        "stakeholders": dotted(data, "ownership.stakeholders", []) or [],
        "deadline": target,
        "business_risks": risks,
        "evidence": dotted(data, "decision.evidence", []) or [],
        "consequence_of_no_decision": dotted(data, "decision.consequence_of_no_decision") or "unknown",
        "next_action": next_action,
        "note": "This projection organizes supplied governance evidence and does not manufacture a recommendation or technical assessment.",
    }
    audience_views = build_audience_views(data, common, operational, stakeholder, executive, next_action)
    audit = {**common, "record": data, "projection_rule": "deterministic-v2"}
    return {
        "one_line": one_line,
        "operational_summary": operational,
        "stakeholder_brief": stakeholder,
        "executive_summary": executive,
        "lifecycle_status": lifecycle_status,
        "decision_ready_brief": decision_ready,
        "audience_views": audience_views,
        "audit_record": audit,
    }


def adapter(name: str, data: dict[str, Any], views: dict[str, Any], source: str, generated_at: str) -> dict[str, Any]:
    common = {
        "authority": "non_authoritative_projection",
        "format": name,
        "source": source,
        "canonical_source": source,
        "generated_at": generated_at,
        "evidence_as_of": dotted(data, "provenance.updated_at"),
        "unknown_fields": views["audit_record"]["unknown_fields"],
        "stale_fields": views["audit_record"]["stale_fields"],
        "conflicting_fields": views["audit_record"]["conflicting_fields"],
    }
    mapped = {
        "lightweight_proposal": {
            "title": dotted(data, "request.title"),
            "rationale": dotted(data, "request.context"),
            "status": canonical_state(data),
        },
        "roadmap_item": {
            "title": dotted(data, "request.title"),
            "owner": dotted(data, "ownership.owner"),
            "target_date": dotted(data, "planning.target_date"),
            "status": canonical_state(data),
        },
        "status_report": views["operational_summary"],
        "decision_log": {
            "state": dotted(data, "decision.state"),
            "decision": dotted(data, "decision.current"),
            "changes": dotted(data, "provenance.changes", []) or [],
        },
        "release_note_input": {
            "title": dotted(data, "request.title"),
            "release_state": dotted(data, "release.state"),
            "evidence": dotted(data, "release.evidence", []) or [],
        },
        "spec_kit_reference": {
            "spec_id": data.get("spec_id"),
            "governance_state": canonical_state(data),
            "planning_reference": dotted(data, "technical_state.planning.source"),
        },
        "openspec_reference": {
            "change_reference": (dotted(data, "links.external", []) or [None])[0],
            "governance_state": canonical_state(data),
            "proposal_summary": dotted(data, "request.context"),
        },
        "kiro_reference": {
            "spec_reference": data.get("spec_id"),
            "governance_state": canonical_state(data),
            "review_required": dotted(data, "governance.profile") == "governed",
        },
    }[name]
    represented = set(json.dumps(json_safe(mapped), sort_keys=True).lower().replace('"', "").split())
    canonical = {
        "request",
        "ownership",
        "planning",
        "business_priority",
        "status",
        "governance",
        "blockers",
        "risks",
        "dependencies",
        "decision",
        "handoffs",
        "release",
        "provenance",
        "technical_state",
    }
    lossy = sorted(key for key in canonical if key not in represented)
    return json_safe({**common, "mapped": mapped, "lossy_fields": lossy})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("--output-dir")
    parser.add_argument(
        "--adapter",
        choices=[
            "lightweight_proposal",
            "roadmap_item",
            "status_report",
            "decision_log",
            "release_note_input",
            "spec_kit_reference",
            "openspec_reference",
            "kiro_reference",
        ],
    )
    parser.add_argument("--generated-at", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    args = parser.parse_args(argv)
    path = Path(args.record).resolve()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors, warnings = validate_record(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    views = build_views(data, str(path), args.generated_at)
    payload = adapter(args.adapter, data, views, str(path), args.generated_at) if args.adapter else views
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        values = payload.items() if isinstance(payload, dict) and not args.adapter else [(args.adapter or "projection", payload)]
        for name, value in values:
            atomic_write_text(
                output_dir / f"{name}.json",
                json.dumps(json_safe(value), indent=2, sort_keys=True) + "\n",
            )
    print(json.dumps(json_safe({"status": "pass", "warnings": warnings, "output": payload}), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
