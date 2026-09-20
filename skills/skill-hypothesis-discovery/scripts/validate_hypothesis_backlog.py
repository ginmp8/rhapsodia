#!/usr/bin/env python3
"""Validate and deterministically rank Skill Hypothesis Discovery backlogs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "2.0"
MODES = {"backlog-discovery", "deep-discovery", "closure-discovery", "evidence-gap-review"}
MODE_LIMITS = {
    "backlog-discovery": (8, 3),
    "deep-discovery": (8, 3),
    "closure-discovery": (5, 2),
    "evidence-gap-review": (5, 0),
}
EVIDENCE_STATUSES = {"measured", "observed", "derived", "supplied", "planned", "gap", "unknown"}
STRONG_EVIDENCE = {"measured", "observed", "derived", "supplied"}
ITEM_KINDS = {"testable-hypothesis", "recommendation", "evidence-gap", "unsupported-speculation"}
ITEM_RECOMMENDATIONS = {"test-now", "defer", "reject", "gather-evidence"}
TOP_RECOMMENDATIONS = {"test-hypotheses", "gather-evidence", "no-mutation-recommended"}
GATE_EFFECTS = {"blocking", "non-blocking", "informational"}
GATE_ORDER = {"blocking": 0, "non-blocking": 1, "informational": 2}
EVALUATOR_STATUSES = {"available", "planned", "missing"}
METRIC_STATUSES = {"active", "saturated", "unknown"}
METRIC_ROLES = {"primary", "auxiliary", "gate"}
DIRECTIONS = {"increase", "decrease", "reduce", "maintain", "pass", "fail", "change"}
AREAS = {
    "activation",
    "ambiguity",
    "output",
    "architecture",
    "resource-integration",
    "documentation",
    "scripts",
    "security",
    "validation",
    "packaging",
    "token",
    "behavioral",
    "consistency",
    "evidence",
    "other",
}
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")

LEGACY_RECOMMENDATIONS = {"test-now", "defer", "reject", "gather-evidence"}
LEGACY_REQUIRED_TOP = {"target", "mode", "evidence_status", "recommendation", "hypotheses"}
LEGACY_REQUIRED_HYPOTHESIS = {
    "id",
    "title",
    "statement",
    "target_area",
    "evidence",
    "expected_effect",
    "validation_method",
    "impact",
    "confidence",
    "testability",
    "risk",
    "cost",
    "recommendation",
}


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"failed to read JSON: {path}: {exc}") from exc


def score(item: dict[str, Any]) -> int:
    return (
        int(item["impact"])
        + int(item["confidence"])
        + int(item["testability"])
        - int(item["risk"])
        - math.ceil(int(item["cost"]) / 2)
    )



def canonical_hypothesis_pool_id(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

def canonical_snapshot_id(sources: list[dict[str, Any]]) -> str:
    ordered = sorted(sources, key=lambda item: str(item.get("id", "")))
    payload = json.dumps(ordered, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _legacy_validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = [
        "legacy/unversioned backlog: v2 evidence identity, eligibility, conflict, saturation, and deterministic selection gates were not applied"
    ]
    missing = sorted(LEGACY_REQUIRED_TOP - set(data))
    if missing:
        errors.append(f"missing top-level fields: {missing}")

    mode = data.get("mode")
    if mode is not None and mode not in MODES:
        warnings.append(f"unknown mode: {mode}")

    hypotheses = data.get("hypotheses")
    if not isinstance(hypotheses, list):
        errors.append("hypotheses must be a list")
        hypotheses = []

    seen: set[str] = set()
    ranked: list[tuple[str, int]] = []
    for i, item in enumerate(hypotheses):
        subject = f"hypothesis[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{subject}: must be an object")
            continue
        hid = item.get("id")
        if isinstance(hid, str) and hid:
            subject = hid
            if hid in seen:
                errors.append(f"duplicate hypothesis id: {hid}")
            seen.add(hid)
        else:
            errors.append(f"hypothesis[{i}]: id is required")

        missing_h = sorted(LEGACY_REQUIRED_HYPOTHESIS - set(item))
        if missing_h:
            errors.append(f"{subject}: missing fields: {missing_h}")
            continue
        valid_scores = True
        for field in ("impact", "confidence", "testability", "risk", "cost"):
            value = item.get(field)
            if not isinstance(value, int) or value < 1 or value > 5:
                errors.append(f"{subject}: {field} must be integer 1..5")
                valid_scores = False
        if item.get("recommendation") not in LEGACY_RECOMMENDATIONS:
            errors.append(f"{subject}: invalid recommendation")
        if valid_scores and isinstance(hid, str):
            ranked.append((hid, score(item)))

    ranked_ids = [hid for hid, _ in sorted(ranked, key=lambda pair: (-pair[1], pair[0]))]
    return {
        "status": "fail" if errors else "pass-with-warnings",
        "schema_version": "legacy",
        "errors": errors,
        "warnings": warnings,
        "diagnostics": [],
        "ranked_ids": ranked_ids,
        "eligible_ids": ranked_ids,
        "scores": {hid: sc for hid, sc in sorted(ranked, key=lambda pair: pair[0])},
        "item_count": len(hypotheses),
    }


def validate(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {
            "status": "fail",
            "schema_version": None,
            "errors": ["[ROOT_TYPE] root: must be an object"],
            "warnings": [],
            "diagnostics": [{"code": "ROOT_TYPE", "severity": "error", "subject": "root", "evidence": "root must be an object"}],
            "ranked_ids": [],
            "eligible_ids": [],
            "scores": {},
            "item_count": 0,
        }

    if data.get("schema_version") != SCHEMA_VERSION:
        return _legacy_validate(data)

    errors: list[str] = []
    warnings: list[str] = []
    diagnostics: list[dict[str, str]] = []

    def add_error(code: str, subject: str, message: str) -> None:
        errors.append(f"[{code}] {subject}: {message}")
        diagnostics.append({"code": code, "severity": "error", "subject": subject, "evidence": message})

    def add_warning(code: str, subject: str, message: str) -> None:
        warnings.append(f"[{code}] {subject}: {message}")
        diagnostics.append({"code": code, "severity": "warning", "subject": subject, "evidence": message})

    required_top = {
        "schema_version",
        "target",
        "mode",
        "evidence_status",
        "recommendation",
        "evidence_snapshot",
        "metrics",
        "items",
        "selected_for_testing",
        "next_hypothesis_id",
    }
    missing_top = sorted(required_top - set(data))
    if missing_top:
        add_error("MISSING_TOP_FIELDS", "root", f"missing fields: {missing_top}")

    mode = data.get("mode")
    if mode not in MODES:
        add_error("INVALID_MODE", "mode", f"expected one of {sorted(MODES)}, got {mode!r}")
        mode = "backlog-discovery"

    if data.get("evidence_status") not in EVIDENCE_STATUSES | {"mixed", "insufficient"}:
        add_error("INVALID_EVIDENCE_STATUS", "evidence_status", f"invalid value {data.get('evidence_status')!r}")
    if data.get("recommendation") not in TOP_RECOMMENDATIONS:
        add_error("INVALID_TOP_RECOMMENDATION", "recommendation", f"invalid value {data.get('recommendation')!r}")

    target = data.get("target")
    if not isinstance(target, dict):
        add_error("TARGET_TYPE", "target", "must be an object")
    else:
        for field in ("name", "identity"):
            value = target.get(field)
            if not isinstance(value, str) or not value.strip():
                add_error("TARGET_IDENTITY", f"target.{field}", "must be a non-empty string")

    evidence_snapshot = data.get("evidence_snapshot")
    source_by_id: dict[str, dict[str, Any]] = {}
    sources: list[dict[str, Any]] = []
    if not isinstance(evidence_snapshot, dict):
        add_error("EVIDENCE_SNAPSHOT_TYPE", "evidence_snapshot", "must be an object")
    else:
        raw_sources = evidence_snapshot.get("sources")
        if not isinstance(raw_sources, list):
            add_error("EVIDENCE_SOURCES_TYPE", "evidence_snapshot.sources", "must be a list")
        else:
            sources = raw_sources
            for i, source in enumerate(sources):
                subject = f"evidence_snapshot.sources[{i}]"
                if not isinstance(source, dict):
                    add_error("EVIDENCE_SOURCE_TYPE", subject, "must be an object")
                    continue
                sid = source.get("id")
                if not isinstance(sid, str) or not sid:
                    add_error("EVIDENCE_SOURCE_ID", subject, "id must be a non-empty string")
                    continue
                if sid in source_by_id:
                    add_error("EVIDENCE_SOURCE_DUPLICATE", sid, "duplicate evidence source id")
                source_by_id[sid] = source
                if source.get("status") not in EVIDENCE_STATUSES:
                    add_error("EVIDENCE_SOURCE_STATUS", sid, f"invalid status {source.get('status')!r}")
                for field in ("identity", "summary"):
                    value = source.get(field)
                    if not isinstance(value, str) or len(value.strip()) < 3:
                        add_error("EVIDENCE_SOURCE_FIELD", f"{sid}.{field}", "must be a non-empty descriptive string")

            expected_snapshot = canonical_snapshot_id([s for s in sources if isinstance(s, dict)])
            actual_snapshot = evidence_snapshot.get("snapshot_id")
            if actual_snapshot != expected_snapshot:
                add_error("EVIDENCE_SNAPSHOT_MISMATCH", "evidence_snapshot.snapshot_id", f"expected {expected_snapshot}, got {actual_snapshot!r}")

    metrics = data.get("metrics")
    metric_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(metrics, list):
        add_error("METRICS_TYPE", "metrics", "must be a list")
        metrics = []
    else:
        for i, metric in enumerate(metrics):
            subject = f"metrics[{i}]"
            if not isinstance(metric, dict):
                add_error("METRIC_TYPE", subject, "must be an object")
                continue
            mid = metric.get("id")
            if not isinstance(mid, str) or not mid:
                add_error("METRIC_ID", subject, "id must be a non-empty string")
                continue
            if mid in metric_by_id:
                add_error("METRIC_DUPLICATE", mid, "duplicate metric id")
            metric_by_id[mid] = metric
            if metric.get("status") not in METRIC_STATUSES:
                add_error("METRIC_STATUS", mid, f"invalid status {metric.get('status')!r}")
            if metric.get("role") not in METRIC_ROLES:
                add_error("METRIC_ROLE", mid, f"invalid role {metric.get('role')!r}")
            if not isinstance(metric.get("name"), str) or len(metric.get("name", "").strip()) < 3:
                add_error("METRIC_NAME", mid, "name must be descriptive")

    items = data.get("items")
    if not isinstance(items, list):
        add_error("ITEMS_TYPE", "items", "must be a list")
        items = []

    max_items, max_selected = MODE_LIMITS.get(mode, MODE_LIMITS["backlog-discovery"])
    if len(items) > max_items:
        add_error("ITEM_LIMIT", "items", f"mode {mode} allows at most {max_items} final items, got {len(items)}")

    item_by_id: dict[str, dict[str, Any]] = {}
    dedupe_owner: dict[str, str] = {}
    item_scores: dict[str, int] = {}
    structurally_testable: set[str] = set()

    common_required = {"id", "kind", "title", "statement", "target_area", "evidence_refs", "recommendation", "conflicts_with", "depends_on"}
    testable_required = {
        "subject_key",
        "mechanism_key",
        "effect_key",
        "dedupe_key",
        "mechanism",
        "expected_effect",
        "evaluator",
        "acceptance_criteria",
        "impact",
        "confidence",
        "testability",
        "risk",
        "cost",
        "gate_effect",
    }

    for i, item in enumerate(items):
        subject = f"items[{i}]"
        if not isinstance(item, dict):
            add_error("ITEM_TYPE", subject, "must be an object")
            continue
        missing_common = sorted(common_required - set(item))
        if missing_common:
            add_error("ITEM_MISSING_FIELDS", subject, f"missing common fields: {missing_common}")
        iid = item.get("id")
        if not isinstance(iid, str) or not iid:
            add_error("ITEM_ID", subject, "id must be a non-empty string")
            continue
        subject = iid
        if iid in item_by_id:
            add_error("ITEM_DUPLICATE_ID", iid, "duplicate item id")
        item_by_id[iid] = item

        kind = item.get("kind")
        if kind not in ITEM_KINDS:
            add_error("ITEM_KIND", iid, f"invalid kind {kind!r}")
        if item.get("target_area") not in AREAS:
            add_warning("ITEM_AREA", iid, f"unknown target_area {item.get('target_area')!r}")
        if item.get("recommendation") not in ITEM_RECOMMENDATIONS:
            add_error("ITEM_RECOMMENDATION", iid, f"invalid recommendation {item.get('recommendation')!r}")
        for field in ("title", "statement"):
            if not isinstance(item.get(field), str) or len(item.get(field, "").strip()) < 8:
                add_error("ITEM_TEXT", f"{iid}.{field}", "must contain at least 8 non-whitespace characters")

        evidence_refs = item.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            add_error("EVIDENCE_REFS_TYPE", iid, "evidence_refs must be a list")
            evidence_refs = []
        unknown_evidence = [ref for ref in evidence_refs if ref not in source_by_id]
        if unknown_evidence:
            add_error("EVIDENCE_REF_UNKNOWN", iid, f"unknown evidence refs: {unknown_evidence}")

        for edge_field in ("conflicts_with", "depends_on"):
            edges = item.get(edge_field)
            if not isinstance(edges, list) or any(not isinstance(x, str) for x in edges):
                add_error("EDGE_TYPE", f"{iid}.{edge_field}", "must be a list of string ids")

        if kind == "unsupported-speculation" and item.get("recommendation") != "reject":
            add_error("SPECULATION_NOT_REJECTED", iid, "unsupported-speculation must use recommendation=reject")
        if kind == "evidence-gap" and item.get("recommendation") not in {"gather-evidence", "defer"}:
            add_error("EVIDENCE_GAP_RECOMMENDATION", iid, "evidence-gap may only be gather-evidence or defer")
        if kind == "recommendation" and item.get("recommendation") == "test-now":
            add_error("RECOMMENDATION_NOT_TESTABLE", iid, "recommendation items cannot be test-now")

        if kind != "testable-hypothesis":
            continue

        missing_testable = sorted(testable_required - set(item))
        if missing_testable:
            add_error("HYPOTHESIS_MISSING_FIELDS", iid, f"missing testable fields: {missing_testable}")
            continue

        key_fields = ("subject_key", "mechanism_key", "effect_key")
        valid_keys = True
        for field in key_fields:
            value = item.get(field)
            if not isinstance(value, str) or KEY_RE.fullmatch(value) is None:
                add_error("SEMANTIC_KEY", f"{iid}.{field}", "must match ^[a-z0-9][a-z0-9_.-]*$")
                valid_keys = False
        if valid_keys:
            expected_dedupe = f"{item.get('target_area')}:{item['subject_key']}:{item['mechanism_key']}:{item['effect_key']}"
            if item.get("dedupe_key") != expected_dedupe:
                add_error("DEDUPE_KEY_MISMATCH", iid, f"expected {expected_dedupe!r}, got {item.get('dedupe_key')!r}")
            owner = dedupe_owner.get(expected_dedupe)
            if owner is not None:
                add_error("DUPLICATE_HYPOTHESIS", iid, f"dedupe_key already used by {owner}")
            else:
                dedupe_owner[expected_dedupe] = iid

        strong_refs = [ref for ref in evidence_refs if source_by_id.get(ref, {}).get("status") in STRONG_EVIDENCE]
        if not strong_refs:
            add_error("MIN_EVIDENCE", iid, "testable-hypothesis requires measured/observed/derived/supplied evidence")

        if not isinstance(item.get("mechanism"), str) or len(item.get("mechanism", "").strip()) < 12:
            add_error("MECHANISM", iid, "mechanism must be explicit and descriptive")

        effect = item.get("expected_effect")
        effect_valid = True
        effect_metric_ids: list[str] = []
        if not isinstance(effect, dict):
            add_error("EXPECTED_EFFECT_TYPE", iid, "expected_effect must be an object")
            effect_valid = False
        else:
            observable = effect.get("observable")
            if not isinstance(observable, str) or len(observable.strip()) < 8:
                add_error("UNMEASURABLE_EFFECT", iid, "expected_effect.observable must name an inspectable/measurable outcome")
                effect_valid = False
            if effect.get("direction") not in DIRECTIONS:
                add_error("EFFECT_DIRECTION", iid, f"invalid direction {effect.get('direction')!r}")
                effect_valid = False
            mids = effect.get("metric_ids")
            if not isinstance(mids, list) or not mids or any(not isinstance(x, str) for x in mids):
                add_error("EFFECT_METRICS", iid, "expected_effect.metric_ids must be a non-empty list of metric ids")
                effect_valid = False
            else:
                effect_metric_ids = mids
                unknown_metrics = [mid for mid in mids if mid not in metric_by_id]
                if unknown_metrics:
                    add_error("EFFECT_METRIC_UNKNOWN", iid, f"unknown metric ids: {unknown_metrics}")
                    effect_valid = False

        evaluator = item.get("evaluator")
        evaluator_available = False
        if not isinstance(evaluator, dict):
            add_error("EVALUATOR_TYPE", iid, "evaluator must be an object")
        else:
            for field in ("id", "status", "method"):
                value = evaluator.get(field)
                if not isinstance(value, str) or not value.strip():
                    add_error("EVALUATOR_FIELD", f"{iid}.evaluator.{field}", "must be a non-empty string")
            if evaluator.get("status") not in EVALUATOR_STATUSES:
                add_error("EVALUATOR_STATUS", iid, f"invalid evaluator status {evaluator.get('status')!r}")
            evaluator_available = evaluator.get("status") == "available"

        criteria = item.get("acceptance_criteria")
        criteria_valid = isinstance(criteria, list) and bool(criteria) and all(isinstance(x, str) and len(x.strip()) >= 8 for x in criteria)
        if not criteria_valid:
            add_error("ACCEPTANCE_CRITERIA", iid, "requires at least one explicit acceptance criterion")

        score_fields_valid = True
        for field in ("impact", "confidence", "testability", "risk", "cost"):
            value = item.get(field)
            if not isinstance(value, int) or value < 1 or value > 5:
                add_error("SCORE_RANGE", f"{iid}.{field}", "must be integer 1..5")
                score_fields_valid = False
        if item.get("gate_effect") not in GATE_EFFECTS:
            add_error("GATE_EFFECT", iid, f"must be one of {sorted(GATE_EFFECTS)}")

        if item.get("recommendation") == "test-now":
            if not evaluator_available:
                add_error("MISSING_EVALUATOR", iid, "test-now requires evaluator.status=available")
            active_metrics = [mid for mid in effect_metric_ids if metric_by_id.get(mid, {}).get("status") == "active"]
            if not active_metrics:
                add_error("SATURATED_OR_UNKNOWN_METRIC", iid, "test-now requires at least one active metric; saturated metrics remain gates")
            if item.get("depends_on"):
                add_error("UNRESOLVED_DEPENDENCY", iid, "test-now item cannot have unresolved depends_on entries")

        if score_fields_valid:
            item_scores[iid] = score(item)
        if strong_refs and effect_valid and evaluator_available and criteria_valid and not item.get("depends_on"):
            structurally_testable.add(iid)

    # Validate edges after all ids exist.
    for iid, item in item_by_id.items():
        for edge_field in ("conflicts_with", "depends_on"):
            edges = item.get(edge_field)
            if not isinstance(edges, list):
                continue
            for other in edges:
                if other == iid:
                    add_error("SELF_EDGE", f"{iid}.{edge_field}", "cannot reference itself")
                elif other not in item_by_id:
                    add_error("EDGE_UNKNOWN", f"{iid}.{edge_field}", f"unknown item id {other}")
        conflicts = item.get("conflicts_with")
        if isinstance(conflicts, list):
            for other in conflicts:
                if other in item_by_id and iid not in item_by_id[other].get("conflicts_with", []):
                    add_error("ASYMMETRIC_CONFLICT", iid, f"conflict with {other} must be symmetric")

    # Ready items are test-now hypotheses that satisfy all structural prerequisites.
    ready_items: list[dict[str, Any]] = []
    for iid in structurally_testable:
        item = item_by_id[iid]
        if item.get("kind") != "testable-hypothesis" or item.get("recommendation") != "test-now":
            continue
        metric_ids = item.get("expected_effect", {}).get("metric_ids", [])
        if not any(metric_by_id.get(mid, {}).get("status") == "active" for mid in metric_ids):
            continue
        if iid not in item_scores or item.get("gate_effect") not in GATE_EFFECTS:
            continue
        ready_items.append(item)

    ranked_ready = sorted(
        ready_items,
        key=lambda item: (
            GATE_ORDER[item["gate_effect"]],
            -item_scores[item["id"]],
            -int(item["testability"]),
            -int(item["confidence"]),
            int(item["risk"]),
            int(item["cost"]),
            item["id"],
        ),
    )
    ranked_ids = [item["id"] for item in ranked_ready]

    selected = data.get("selected_for_testing")
    if not isinstance(selected, list) or any(not isinstance(x, str) for x in selected):
        add_error("SELECTED_TYPE", "selected_for_testing", "must be a list of string ids")
        selected = []
    if len(selected) > max_selected:
        add_error("SELECTED_LIMIT", "selected_for_testing", f"mode {mode} allows at most {max_selected} selected items")
    for iid in selected:
        if iid not in item_by_id:
            add_error("SELECTED_UNKNOWN", "selected_for_testing", f"unknown item id {iid}")
        elif iid not in ranked_ids:
            add_error("SELECTED_INELIGIBLE", iid, "selected item is not a ready test-now hypothesis")
    if selected and selected != ranked_ids[: len(selected)]:
        add_error("NONDETERMINISTIC_SELECTION", "selected_for_testing", f"must be a prefix of deterministic ranking {ranked_ids}")
    for i, left in enumerate(selected):
        for right in selected[i + 1 :]:
            if right in item_by_id.get(left, {}).get("conflicts_with", []):
                add_error("SELECTED_CONFLICT", "selected_for_testing", f"{left} conflicts with {right}")

    next_id = data.get("next_hypothesis_id")
    top_recommendation = data.get("recommendation")
    if mode == "evidence-gap-review":
        if selected:
            add_error("EVIDENCE_GAP_SELECTION", "selected_for_testing", "evidence-gap-review cannot select mutation hypotheses")
        if next_id is not None:
            add_error("EVIDENCE_GAP_NEXT", "next_hypothesis_id", "must be null in evidence-gap-review")
    elif top_recommendation == "test-hypotheses":
        if not selected:
            add_error("NEXT_SELECTION_REQUIRED", "selected_for_testing", "test-hypotheses requires at least one selected ready hypothesis")
        elif next_id != selected[0]:
            add_error("NEXT_ID_MISMATCH", "next_hypothesis_id", f"must equal first selected hypothesis {selected[0]!r}")
    else:
        if selected:
            add_error("TOP_RECOMMENDATION_SELECTION", "selected_for_testing", f"recommendation={top_recommendation} requires an empty selection")
        if next_id is not None:
            add_error("TOP_RECOMMENDATION_NEXT", "next_hypothesis_id", f"recommendation={top_recommendation} requires null next_hypothesis_id")

    # A saturated primary with no active auxiliary is a deliberate stop condition.
    saturated_primary = any(m.get("role") == "primary" and m.get("status") == "saturated" for m in metric_by_id.values())
    active_auxiliary = any(m.get("role") == "auxiliary" and m.get("status") == "active" for m in metric_by_id.values())
    if saturated_primary and not active_auxiliary and top_recommendation == "test-hypotheses":
        add_error("SATURATED_NO_AUXILIARY", "metrics", "saturated primary metric requires an active auxiliary metric before selecting more mutation experiments")

    status = "fail" if errors else "pass" if not warnings else "pass-with-warnings"
    return {
        "status": status,
        "schema_version": SCHEMA_VERSION,
        "errors": errors,
        "warnings": warnings,
        "diagnostics": diagnostics,
        "snapshot_id": evidence_snapshot.get("snapshot_id") if isinstance(evidence_snapshot, dict) else None,
        "hypothesis_pool_id": canonical_hypothesis_pool_id(data),
        "ranked_ids": ranked_ids,
        "eligible_ids": ranked_ids,
        "scores": {iid: item_scores[iid] for iid in sorted(item_scores)},
        "item_count": len(items),
        "selected_for_testing": selected,
        "next_hypothesis_id": next_id,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and deterministically rank a hypothesis backlog JSON file.")
    parser.add_argument("--input", required=True, help="Path to backlog JSON")
    parser.add_argument("--json-output", help="Optional path to write validation result JSON")
    args = parser.parse_args(argv)

    result = validate(read_json(Path(args.input)))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"pass", "pass-with-warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
