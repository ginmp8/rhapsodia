#!/usr/bin/env python3
"""Validate deterministic research-aware pre-handoff evidence for hypothesis discovery."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
RESEARCH_POLICIES = {"never", "if-needed", "required"}
RESEARCH_STATUSES = {"not-run", "complete", "blocked", "insufficient"}
SUFFICIENCY = {"sufficient", "insufficient", "unknown"}
RECOMMENDATIONS = {"proceed-to-v2-handoff", "gather-evidence", "no-mutation-recommended"}
AUTHORITIES = {"primary", "official", "academic", "secondary", "community", "user-provided"}
EVIDENCE_STATES = {"snapshotted", "pinned", "live", "user-provided"}
STANCES = {"supporting", "contradicting", "boundary", "contextual"}
EVIDENCE_ROLES = {"discovery", "validation", "regression-gate", "contextual"}
FALSIFICATION_STATUSES = {"attempted", "blocked", "not-required"}
EVALUATOR_EXPOSURES = {"held-out", "independent", "shared", "unknown"}
GAP_STATUSES = {"open", "resolved", "blocked"}


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"failed to read JSON: {path}: {exc}") from exc


def canonical_corpus_id(sources: list[dict[str, Any]], findings: list[dict[str, Any]]) -> str:
    payload = {
        "sources": sorted(sources, key=lambda item: str(item.get("id", ""))),
        "findings": sorted(findings, key=lambda item: str(item.get("id", ""))),
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def gap_score(item: dict[str, Any]) -> int:
    return int(item["information_value"]) - math.ceil(int(item["collection_cost"]) / 2)


def validate(data: Any) -> dict[str, Any]:
    diagnostics: list[dict[str, str]] = []

    def error(code: str, subject: str, evidence: str) -> None:
        diagnostics.append({"code": code, "severity": "error", "subject": subject, "evidence": evidence})

    def warning(code: str, subject: str, evidence: str) -> None:
        diagnostics.append({"code": code, "severity": "warning", "subject": subject, "evidence": evidence})

    if not isinstance(data, dict):
        error("ROOT_TYPE", "root", "root must be an object")
        return _result(diagnostics, None, [], {})

    required = {
        "schema_version",
        "target",
        "research_policy",
        "research_status",
        "evidence_sufficiency",
        "recommendation",
        "research_corpus",
        "evidence_roles",
        "hypothesis_checks",
        "evidence_gaps",
        "ranked_gap_ids",
    }
    missing = sorted(required - set(data))
    if missing:
        error("MISSING_TOP_FIELDS", "root", f"missing fields: {missing}")

    if data.get("schema_version") != SCHEMA_VERSION:
        error("SCHEMA_VERSION", "schema_version", f"expected {SCHEMA_VERSION!r}, got {data.get('schema_version')!r}")
    policy = data.get("research_policy")
    status = data.get("research_status")
    sufficiency = data.get("evidence_sufficiency")
    recommendation = data.get("recommendation")
    if policy not in RESEARCH_POLICIES:
        error("RESEARCH_POLICY", "research_policy", f"expected one of {sorted(RESEARCH_POLICIES)}, got {policy!r}")
    if status not in RESEARCH_STATUSES:
        error("RESEARCH_STATUS", "research_status", f"expected one of {sorted(RESEARCH_STATUSES)}, got {status!r}")
    if sufficiency not in SUFFICIENCY:
        error("EVIDENCE_SUFFICIENCY", "evidence_sufficiency", f"expected one of {sorted(SUFFICIENCY)}, got {sufficiency!r}")
    if recommendation not in RECOMMENDATIONS:
        error("RECOMMENDATION", "recommendation", f"expected one of {sorted(RECOMMENDATIONS)}, got {recommendation!r}")

    target = data.get("target")
    if not isinstance(target, dict):
        error("TARGET_TYPE", "target", "target must be an object")
    else:
        for field in ("name", "identity"):
            if not isinstance(target.get(field), str) or not target.get(field, "").strip():
                error("TARGET_FIELD", f"target.{field}", "must be a non-empty string")

    corpus = data.get("research_corpus")
    sources: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    source_by_id: dict[str, dict[str, Any]] = {}
    finding_by_id: dict[str, dict[str, Any]] = {}
    corpus_id: str | None = None
    if not isinstance(corpus, dict):
        error("CORPUS_TYPE", "research_corpus", "must be an object")
    else:
        raw_sources = corpus.get("sources")
        raw_findings = corpus.get("findings")
        if not isinstance(raw_sources, list):
            error("SOURCE_LIST", "research_corpus.sources", "must be a list")
        else:
            sources = raw_sources
        if not isinstance(raw_findings, list):
            error("FINDING_LIST", "research_corpus.findings", "must be a list")
        else:
            findings = raw_findings

        for i, source in enumerate(sources):
            subject = f"research_corpus.sources[{i}]"
            if not isinstance(source, dict):
                error("SOURCE_TYPE", subject, "must be an object")
                continue
            sid = source.get("id")
            if not isinstance(sid, str) or not sid:
                error("SOURCE_ID", subject, "id must be a non-empty string")
                continue
            if sid in source_by_id:
                error("SOURCE_DUPLICATE", sid, "duplicate source id")
            source_by_id[sid] = source
            for field in ("locator", "identity"):
                if not isinstance(source.get(field), str) or not source.get(field, "").strip():
                    error("SOURCE_FIELD", f"{sid}.{field}", "must be a non-empty string")
            if source.get("authority") not in AUTHORITIES:
                error("SOURCE_AUTHORITY", sid, f"invalid authority {source.get('authority')!r}")
            if source.get("evidence_state") not in EVIDENCE_STATES:
                error("SOURCE_STATE", sid, f"invalid evidence_state {source.get('evidence_state')!r}")
            if source.get("evidence_state") == "live" and status == "complete":
                warning("LIVE_SOURCE", sid, "complete research uses a live source; preserve a frozen research artifact and retrieval identity")

        for i, finding in enumerate(findings):
            subject = f"research_corpus.findings[{i}]"
            if not isinstance(finding, dict):
                error("FINDING_TYPE", subject, "must be an object")
                continue
            fid = finding.get("id")
            if not isinstance(fid, str) or not fid:
                error("FINDING_ID", subject, "id must be a non-empty string")
                continue
            if fid in finding_by_id:
                error("FINDING_DUPLICATE", fid, "duplicate finding id")
            finding_by_id[fid] = finding
            if not isinstance(finding.get("statement"), str) or len(finding.get("statement", "").strip()) < 8:
                error("FINDING_STATEMENT", fid, "statement must be descriptive")
            refs = finding.get("source_refs")
            if not isinstance(refs, list) or not refs or any(not isinstance(x, str) for x in refs):
                error("FINDING_SOURCE_REFS", fid, "source_refs must be a non-empty list of source ids")
            else:
                unknown = sorted(ref for ref in refs if ref not in source_by_id)
                if unknown:
                    error("FINDING_SOURCE_UNKNOWN", fid, f"unknown source refs: {unknown}")
            if finding.get("stance") not in STANCES:
                error("FINDING_STANCE", fid, f"invalid stance {finding.get('stance')!r}")

        corpus_id = canonical_corpus_id(
            [item for item in sources if isinstance(item, dict)],
            [item for item in findings if isinstance(item, dict)],
        )
        if corpus.get("corpus_id") != corpus_id:
            error("CORPUS_ID_MISMATCH", "research_corpus.corpus_id", f"expected {corpus_id}, got {corpus.get('corpus_id')!r}")

    if status == "complete" and (not sources or not findings):
        error("COMPLETE_EMPTY_CORPUS", "research_corpus", "research_status=complete requires at least one source and one finding")
    if policy == "required" and recommendation == "proceed-to-v2-handoff" and status != "complete":
        error("REQUIRED_RESEARCH_INCOMPLETE", "research_status", "research_policy=required must complete research before v2 handoff")
    if sufficiency != "sufficient" and recommendation == "proceed-to-v2-handoff":
        error("INSUFFICIENT_FOR_HANDOFF", "evidence_sufficiency", "v2 handoff requires evidence_sufficiency=sufficient")
    if status in {"blocked", "insufficient"} and recommendation == "proceed-to-v2-handoff":
        error("RESEARCH_BLOCKED_HANDOFF", "recommendation", f"research_status={status} cannot proceed to v2 handoff")
    if policy == "never" and sufficiency == "insufficient" and recommendation == "proceed-to-v2-handoff":
        error("POLICY_NEVER_INSUFFICIENT", "recommendation", "research_policy=never with insufficient evidence must gather evidence or stop")

    role_by_id: dict[str, dict[str, Any]] = {}
    roles = data.get("evidence_roles")
    if not isinstance(roles, list):
        error("EVIDENCE_ROLES_TYPE", "evidence_roles", "must be a list")
        roles = []
    for i, role in enumerate(roles):
        subject = f"evidence_roles[{i}]"
        if not isinstance(role, dict):
            error("EVIDENCE_ROLE_TYPE", subject, "must be an object")
            continue
        eid = role.get("evidence_id")
        if not isinstance(eid, str) or not eid:
            error("EVIDENCE_ROLE_ID", subject, "evidence_id must be a non-empty string")
            continue
        if eid in role_by_id:
            error("EVIDENCE_ROLE_DUPLICATE", eid, "duplicate evidence_id")
        role_by_id[eid] = role
        if role.get("role") not in EVIDENCE_ROLES:
            error("EVIDENCE_ROLE", eid, f"invalid role {role.get('role')!r}")
        refs = role.get("finding_refs")
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
            error("EVIDENCE_FINDING_REFS", eid, "finding_refs must be a list of finding ids")
        else:
            unknown = sorted(ref for ref in refs if ref not in finding_by_id)
            if unknown:
                error("EVIDENCE_FINDING_UNKNOWN", eid, f"unknown finding refs: {unknown}")

    checks = data.get("hypothesis_checks")
    if not isinstance(checks, list):
        error("HYPOTHESIS_CHECKS_TYPE", "hypothesis_checks", "must be a list")
        checks = []
    if recommendation == "proceed-to-v2-handoff" and status == "complete" and not checks:
        error("HYPOTHESIS_CHECK_REQUIRED", "hypothesis_checks", "research-backed v2 handoff requires at least one hypothesis check")
    seen_hypotheses: set[str] = set()
    for i, check in enumerate(checks):
        subject = f"hypothesis_checks[{i}]"
        if not isinstance(check, dict):
            error("HYPOTHESIS_CHECK_TYPE", subject, "must be an object")
            continue
        hid = check.get("hypothesis_id")
        if not isinstance(hid, str) or not hid:
            error("HYPOTHESIS_ID", subject, "hypothesis_id must be a non-empty string")
            continue
        if hid in seen_hypotheses:
            error("HYPOTHESIS_DUPLICATE", hid, "duplicate hypothesis check")
        seen_hypotheses.add(hid)

        discovery_refs = check.get("discovery_evidence_refs")
        if not isinstance(discovery_refs, list) or not discovery_refs or any(not isinstance(x, str) for x in discovery_refs):
            error("DISCOVERY_EVIDENCE_REFS", hid, "discovery_evidence_refs must be a non-empty list")
            discovery_refs = []
        for ref in discovery_refs:
            role = role_by_id.get(ref)
            if role is None:
                error("DISCOVERY_EVIDENCE_UNKNOWN", hid, f"unknown evidence role {ref}")
            elif role.get("role") == "validation":
                error("VALIDATION_LEAKAGE", hid, f"validation-role evidence {ref} cannot support hypothesis discovery")
            elif role.get("role") == "regression-gate":
                error("REGRESSION_GATE_AS_DISCOVERY", hid, f"regression-gate evidence {ref} cannot be used as causal discovery support")

        for field in ("supporting_finding_refs", "counterevidence_finding_refs"):
            refs = check.get(field)
            if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
                error("HYPOTHESIS_FINDING_REFS", f"{hid}.{field}", "must be a list of finding ids")
            else:
                unknown = sorted(ref for ref in refs if ref not in finding_by_id)
                if unknown:
                    error("HYPOTHESIS_FINDING_UNKNOWN", f"{hid}.{field}", f"unknown finding refs: {unknown}")
        alternatives = check.get("alternative_explanations")
        if not isinstance(alternatives, list) or any(not isinstance(x, str) or not x.strip() for x in alternatives):
            error("ALTERNATIVE_EXPLANATIONS", hid, "alternative_explanations must be a list of non-empty strings")

        falsification = check.get("falsification")
        falsification_status = None
        if not isinstance(falsification, dict):
            error("FALSIFICATION_TYPE", hid, "falsification must be an object")
        else:
            falsification_status = falsification.get("status")
            if falsification_status not in FALSIFICATION_STATUSES:
                error("FALSIFICATION_STATUS", hid, f"invalid falsification status {falsification_status!r}")
            criteria = falsification.get("criteria")
            if not isinstance(criteria, list) or not criteria or any(not isinstance(x, str) or len(x.strip()) < 8 for x in criteria):
                error("FALSIFICATION_CRITERIA", hid, "requires at least one explicit falsification criterion")
            if not isinstance(falsification.get("search_summary"), str) or len(falsification.get("search_summary", "").strip()) < 8:
                error("FALSIFICATION_SUMMARY", hid, "search_summary must describe the negative/counterevidence check")

        evaluator = check.get("evaluator")
        exposure = None
        if not isinstance(evaluator, dict):
            error("EVALUATOR_TYPE", hid, "evaluator must be an object")
        else:
            if not isinstance(evaluator.get("identity"), str) or not evaluator.get("identity", "").strip():
                error("EVALUATOR_IDENTITY", hid, "evaluator.identity must be a non-empty frozen/stable identity")
            exposure = evaluator.get("exposure")
            if exposure not in EVALUATOR_EXPOSURES:
                error("EVALUATOR_EXPOSURE", hid, f"invalid evaluator exposure {exposure!r}")

        if recommendation == "proceed-to-v2-handoff":
            if falsification_status != "attempted":
                error("FALSIFICATION_NOT_ATTEMPTED", hid, "research-backed v2 handoff requires falsification.status=attempted")
            if exposure not in {"held-out", "independent"}:
                error("EVALUATOR_NOT_INDEPENDENT", hid, "research-backed v2 handoff requires evaluator exposure held-out or independent")

    gaps = data.get("evidence_gaps")
    if not isinstance(gaps, list):
        error("EVIDENCE_GAPS_TYPE", "evidence_gaps", "must be a list")
        gaps = []
    gap_by_id: dict[str, dict[str, Any]] = {}
    open_gaps: list[dict[str, Any]] = []
    scores: dict[str, int] = {}
    for i, gap in enumerate(gaps):
        subject = f"evidence_gaps[{i}]"
        if not isinstance(gap, dict):
            error("GAP_TYPE", subject, "must be an object")
            continue
        gid = gap.get("id")
        if not isinstance(gid, str) or not gid:
            error("GAP_ID", subject, "id must be a non-empty string")
            continue
        if gid in gap_by_id:
            error("GAP_DUPLICATE", gid, "duplicate gap id")
        gap_by_id[gid] = gap
        if not isinstance(gap.get("question"), str) or len(gap.get("question", "").strip()) < 8:
            error("GAP_QUESTION", gid, "question must be descriptive")
        if gap.get("status") not in GAP_STATUSES:
            error("GAP_STATUS", gid, f"invalid status {gap.get('status')!r}")
        valid_score = True
        for field in ("information_value", "collection_cost"):
            value = gap.get(field)
            if not isinstance(value, int) or value < 1 or value > 5:
                error("GAP_SCORE_RANGE", f"{gid}.{field}", "must be integer 1..5")
                valid_score = False
        if gap.get("status") == "open" and valid_score:
            scores[gid] = gap_score(gap)
            open_gaps.append(gap)

    ranked = sorted(
        open_gaps,
        key=lambda item: (
            -scores[item["id"]],
            -int(item["information_value"]),
            int(item["collection_cost"]),
            item["id"],
        ),
    )
    ranked_ids = [item["id"] for item in ranked]
    supplied_ranked = data.get("ranked_gap_ids")
    if not isinstance(supplied_ranked, list) or any(not isinstance(x, str) for x in supplied_ranked):
        error("RANKED_GAPS_TYPE", "ranked_gap_ids", "must be a list of string ids")
    elif supplied_ranked != ranked_ids:
        error("NONDETERMINISTIC_GAP_RANKING", "ranked_gap_ids", f"expected {ranked_ids}, got {supplied_ranked}")

    if recommendation == "proceed-to-v2-handoff" and open_gaps:
        warning("OPEN_GAPS_AT_HANDOFF", "evidence_gaps", "open evidence gaps remain; ensure they are non-blocking/contextual before v2 handoff")

    return _result(diagnostics, corpus_id, ranked_ids, scores)


def _result(diagnostics: list[dict[str, str]], corpus_id: str | None, ranked_gap_ids: list[str], scores: dict[str, int]) -> dict[str, Any]:
    errors = [item for item in diagnostics if item["severity"] == "error"]
    warnings = [item for item in diagnostics if item["severity"] == "warning"]
    status = "fail" if errors else "pass-with-warnings" if warnings else "pass"
    return {
        "status": status,
        "schema_version": SCHEMA_VERSION,
        "corpus_id": corpus_id,
        "ranked_gap_ids": ranked_gap_ids,
        "gap_scores": {key: scores[key] for key in sorted(scores)},
        "diagnostics": diagnostics,
        "errors": [f"[{item['code']}] {item['subject']}: {item['evidence']}" for item in errors],
        "warnings": [f"[{item['code']}] {item['subject']}: {item['evidence']}" for item in warnings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate research-aware evidence before v2 hypothesis-pool handoff.")
    parser.add_argument("--input", required=True, help="Path to research-discovery JSON")
    parser.add_argument("--json-output", help="Optional path for the machine-readable result")
    args = parser.parse_args(argv)
    result = validate(read_json(Path(args.input)))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"pass", "pass-with-warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
