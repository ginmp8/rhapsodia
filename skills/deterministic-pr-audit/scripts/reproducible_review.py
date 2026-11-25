"""Frozen normative scope and explicit semantic reconciliation (no CI inputs).

All findings are analyst evidence leads, not automatic semantic judgments.
The separate immutable plan prevents a grading run from changing its own rubric;
its creation time and semantic completeness still require reviewer discipline.
"""
from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

from audit_core import AuditError, digest, extract_requirements, read_json, require_schema

PLAN_SCHEMA = "pr-audit/obligation-plan/v1"
HISTORY_SCHEMA = "pr-audit/audit-history/v1"
PLAN_FIELDS = ("kind", "quote", "subject", "polarity")


def norm(value: str) -> str:
    return " ".join(value.split())


def descriptor(item: dict) -> dict:
    return {k: norm(item[k]).casefold() if k == "subject" else norm(item[k]) for k in PLAN_FIELDS}


def obligation_id(criterion: str, item: dict) -> str:
    return "OBL-" + digest([criterion, descriptor(item)])


def freeze_plan(source: dict, requirements: dict, draft: dict) -> dict:
    # Local import avoids a dependency cycle with the legacy scorer.
    from implementation_review import GAP_KINDS, polarity_subjects
    if requirements != extract_requirements(source, canonical_ids=True):
        raise AuditError("Obligation plan requires canonical frozen requirements")
    texts = {c["id"]: norm(c["text"]) for c in requirements["criteria"]}
    if set(draft) != {"criteria"} or not isinstance(draft["criteria"], dict) or set(draft["criteria"]) != set(texts):
        raise AuditError("Obligation plan must enumerate every canonical AC/REQ exactly once")
    normative = " ".join(norm(t) for t in [source["issue"]["body"],
                      *(c["body"] for c in source["issue"]["comments"]),
                      *(s["body"] for s in source["spec_files"])])
    result = {}
    for ident, text in texts.items():
        items = draft["criteria"][ident]
        if not isinstance(items, list) or not items:
            raise AuditError(f"{ident}: frozen obligation plan cannot be empty, including unknown criteria")
        seen, paired, rows = set(), set(), []
        for item in items:
            if not isinstance(item, dict) or set(item) != set(PLAN_FIELDS) or not all(isinstance(v, str) for v in item.values()):
                raise AuditError(f"{ident}: plan descriptors must contain only {', '.join(PLAN_FIELDS)} (no candidate verdicts)")
            d = descriptor(item)
            if (d["kind"] not in GAP_KINDS or d["polarity"] not in ("positive", "negative", "none") or
                    not d["subject"] or not d["quote"] or
                    (d["quote"] not in text and not (ident.startswith("REQ-") and d["quote"] in normative))):
                raise AuditError(f"{ident}: invalid frozen normative obligation")
            key = (d["kind"], d["subject"], d["polarity"])
            if key in seen:
                raise AuditError(f"{ident}: duplicate frozen obligation {key}")
            seen.add(key)
            if d["kind"] == "mandatory_test" and d["polarity"] != "none":
                if d["subject"] in polarity_subjects(text) and (d["subject"] not in d["quote"].casefold() or
                        not re.search(r"\bpositive\s+and\s+negative\s+tests\b", d["quote"], re.I)):
                    raise AuditError(f"{ident}: polarity quote must name the subject and required tests")
                paired.add((d["subject"], d["polarity"]))
            rows.append({"id": obligation_id(ident, d), **d})
        required = {(s, p) for s in polarity_subjects(text) for p in ("positive", "negative")}
        if not required.issubset(paired):
            raise AuditError(f"{ident}: frozen plan lacks explicit test polarity coverage {sorted(required - paired)}")
        if not required and re.search(r"\bpositive\s+and\s+negative\b", text, re.I):
            positive = {s for s, p in paired if p == "positive"}
            negative = {s for s, p in paired if p == "negative"}
            if not positive or positive != negative:
                raise AuditError(f"{ident}: frozen plan requires paired test subjects")
        result[ident] = sorted(rows, key=lambda x: x["id"])
    return {"schema": PLAN_SCHEMA, "requirements_digest": digest(requirements),
            "spec_digest": requirements["spec_digest"], "criteria": result}


def validate_plan(source: dict, requirements: dict, plan: dict) -> None:
    require_schema(plan, PLAN_SCHEMA)
    try:
        draft = {"criteria": {ident: [{k: item[k] for k in PLAN_FIELDS} for item in items]
                             for ident, items in plan["criteria"].items()}}
    except (KeyError, TypeError, AttributeError) as exc:
        raise AuditError("Malformed frozen obligation plan") from exc
    if plan != freeze_plan(source, requirements, draft):
        raise AuditError("Frozen obligation plan identity or canonical descriptors differ")


def scaffold(plan: dict, ident: str) -> list[dict]:
    return [{**{k: item[k] for k in PLAN_FIELDS}, "verdict": "UNKNOWN", "anchor": "",
             "witness": "Not yet adjudicated against the pinned candidate source."} for item in plan["criteria"][ident]]


def validate_scope(review: dict, plan: dict) -> None:
    if review.get("obligation_plan_digest") != digest(plan):
        raise AuditError("Review is not bound to the separately frozen obligation plan")
    for ident, row in review["criteria"].items():
        try:
            actual = sorted(({"id": obligation_id(ident, item), **{k: item[k] for k in PLAN_FIELDS}}
                             for item in row["coverage"]), key=lambda x: x["id"])
        except (KeyError, TypeError, AttributeError) as exc:
            raise AuditError(f"{ident}: malformed coverage descriptors") from exc
        if actual != plan["criteria"][ident]:
            raise AuditError(f"{ident}: obligation scope drift; use the frozen plan even for UNKNOWN rows")


def markdown_inventory(content: str) -> dict:
    """Read historical report headings only; never certify their source/spec identity."""
    from implementation_review import STATES
    h = re.search(r"^# Code-delivery audit — ([\w.-]+/[\w.-]+) PR #(\d+)\s*$", content, re.M)
    head = re.search(r"^- \*\*HEAD:\*\* `([a-f0-9]{40})`\s*$", content, re.M)
    if not h or not head:
        raise AuditError("Prior Markdown report lacks repository/PR/HEAD identity")
    rows = []
    for m in re.finditer(r"^### ((?:AC|REQ|CHK)-[\w-]+) — (\w+)\s*\n+(\S[^\n]*)", content, re.M):
        if m[2] not in STATES:
            raise AuditError("Invalid prior Markdown verdict")
        rows.append({"id": m[1], "status": m[2], "text": m[3]})
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise AuditError("Prior Markdown report has missing or duplicate criterion headings")
    return {"repository": h[1], "pr_number": int(h[2]), "identity": {"head_sha": head[1]}, "rows": rows}


def prepare_history(search: str, paths: list[str]) -> dict:
    reports = []
    for path in paths:
        p = Path(path)
        if p.suffix.lower() == ".json":
            content, fmt = read_json(p), "json"
        elif p.suffix.lower() == ".md":
            content, fmt = p.read_text(encoding="utf-8"), "markdown"
            markdown_inventory(content)
        else:
            raise AuditError("Prior audit must be an implementation-grade.json or Markdown report")
        reports.append({"format": fmt, "content": content})
    return {"schema": HISTORY_SCHEMA, "search": search, "reports": reports, "resolutions": {}}


def history_identity(history: dict) -> str:
    require_schema(history, HISTORY_SCHEMA)
    if (set(history) != {"schema", "search", "reports", "resolutions"} or
            not isinstance(history["search"], str) or len(history["search"].strip()) < 20 or
            not isinstance(history["reports"], list) or not isinstance(history["resolutions"], dict)):
        raise AuditError("Audit history requires explicit search/availability, prior reports and resolutions")
    for item in history["reports"]:
        if not isinstance(item, dict) or set(item) != {"format", "content"} or item["format"] not in ("json", "markdown"):
            raise AuditError("Malformed prior audit inventory")
        if not isinstance(item["content"], dict if item["format"] == "json" else str):
            raise AuditError("Malformed prior audit content")
    # Only resolutions may change after initialization. New reports require a
    # new review scaffold with the SAME obligation plan, not silent omission.
    return digest({k: history[k] for k in ("schema", "search", "reports")})


def _anchor(ref: dict) -> str:
    return f"{ref['path']}:L{ref['line_start']}-L{ref['line_end']}"


def reconcile(source: dict, requirements: dict, review: dict, plan: dict, history: dict) -> dict:
    """Discover prior disagreements and shared-code counterexample leads.

    A lead never changes a verdict. Resolution is a source-anchored analyst
    decision; same-file overlap alone cannot prove semantic applicability.
    """
    from implementation_review import GRADE_SCHEMA, STATES
    inventory_digest = history_identity(history)
    rows = review["criteria"]
    texts = {c["id"]: norm(c["text"]) for c in requirements["criteria"]}
    head = source["pull_request"]["head_sha"]
    leads, inspected, seen = {}, [], set()

    def add(lead: dict) -> None:
        lead = {**lead, "current_row_digest": digest(rows[lead["criterion"]])}
        lead_id = "REC-" + digest(lead)
        leads[lead_id] = {"id": lead_id, **lead}

    for item in history["reports"]:
        if not isinstance(item, dict) or set(item) != {"format", "content"}:
            raise AuditError("Malformed prior audit")
        fmt, content = item["format"], item["content"]
        key = digest(item)
        if key in seen:
            continue
        seen.add(key)
        if fmt == "markdown" and isinstance(content, str):
            previous = markdown_inventory(content)
        elif fmt == "json" and isinstance(content, dict):
            require_schema(content, GRADE_SCHEMA)
            previous = content
        else:
            raise AuditError("Unsupported prior audit format")
        identity = previous["identity"]
        if (previous["repository"].casefold() != source["repository"].casefold() or
                previous["pr_number"] != source["pull_request"]["number"] or identity["head_sha"] != head):
            inspected.append({"digest": key, "format": fmt, "disposition": "different_target_or_head"})
            continue
        if fmt == "json" and identity.get("requirements_digest") != digest(requirements):
            inspected.append({"digest": key, "format": fmt, "disposition": "different_normative_digest"})
            continue
        old = previous["rows"]
        if not isinstance(old, list) or any(not isinstance(r, dict) or not isinstance(r.get("id"), str) or
                r.get("status") not in STATES or not isinstance(r.get("text"), str) for r in old) or len({r["id"] for r in old}) != len(old):
            raise AuditError("Invalid prior audit criterion inventory")
        matched = 0
        for r in old:
            ident = r["id"]
            if ident not in rows or norm(r["text"]) != texts[ident]:
                continue
            matched += 1
            row = rows[ident]
            if r["status"] != row["status"]:
                add({"kind": "prior_verdict", "criterion": ident, "prior_report_digest": key,
                     "prior_status": r["status"], "current_status": row["status"],
                     "identity": "same_normative_digest" if fmt == "json" else "same_head_and_criterion_text_only"})
            elif fmt == "json" and previous.get("obligation_plan_digest") == digest(plan):
                # Same criterion verdict can conceal different individual obligations.
                prior_obs = {obligation_id(ident, o): o["verdict"] for o in r.get("coverage", [])}
                for o in row["coverage"]:
                    oid = obligation_id(ident, o)
                    if oid in prior_obs and prior_obs[oid] != o["verdict"]:
                        add({"kind": "prior_obligation", "criterion": ident, "obligation_id": oid,
                             "prior_report_digest": key, "prior_status": prior_obs[oid], "current_status": o["verdict"]})
        inspected.append({"digest": key, "format": fmt, "disposition": "compared_matching_criteria",
                          "matched_criteria": matched, "prior_criteria": len(old), "current_criteria": len(rows),
                          "scope_identity": "normative_digest" if fmt == "json" else "provisional_markdown_text",
                          "plan_identity": "same" if previous.get("obligation_plan_digest") == digest(plan) else "different_or_unavailable"})

    # Deduplicate shared counterexamples at the actual source span. Flag only
    # COMPLETE rows with overlapping affirmative references; a shared path is
    # a review lead, not automatic propagation of a penalty.
    gaps = {}
    for ident, row in rows.items():
        anchors = {o["anchor"] for o in row["coverage"] if o["verdict"] == "GAP"}
        for ref in row["evidence"]:
            if ref["role"] == "counterexample" and _anchor(ref) in anchors:
                key = (ref["path"], ref["blob_sha"], ref["line_start"], ref["line_end"])
                gaps.setdefault(key, set()).add(ident)
    for ident, row in rows.items():
        if row["status"] != "COMPLETE":
            continue
        positive = [r for r in row["evidence"] if r["role"] != "counterexample"]
        for (path, sha, start, end), owners in sorted(gaps.items()):
            if ident in owners:
                continue
            overlap = sorted({_anchor(r) for r in positive if r["path"] == path and r["blob_sha"] == sha
                              and r["line_start"] <= end and start <= r["line_end"]})
            if overlap:
                add({"kind": "shared_counterexample", "criterion": ident, "gap_criteria": sorted(owners),
                     "path": path, "blob_sha": sha, "line_start": start, "line_end": end,
                     "overlapping_anchors": overlap})
    resolutions = history["resolutions"]
    if not set(resolutions).issubset(leads):
        raise AuditError("Stale or unknown reconciliation resolution; rederive leads from current review")
    for key, resolution in resolutions.items():
        if (not isinstance(resolution, dict) or set(resolution) != {"anchor", "rationale"} or
                not isinstance(resolution["rationale"], str) or len(resolution["rationale"].strip()) < 60 or
                resolution["anchor"] not in {_anchor(r) for r in rows[leads[key]["criterion"]]["evidence"]}):
            raise AuditError(f"{key}: resolution needs an inspected current criterion anchor and specific contrary-evidence rationale")
    return {"history_digest": digest(history), "inventory_digest": inventory_digest, "search": history["search"], "prior_reports": inspected,
            "leads": [leads[k] for k in sorted(leads)], "resolutions": deepcopy(resolutions),
            "unresolved": sorted(set(leads) - set(resolutions))}


def review_closure(review: dict, reconciliation: dict, provenance: str, source: dict) -> dict:
    unknown = {ident: sorted(obligation_id(ident, o) for o in row["coverage"] if o["verdict"] == "UNKNOWN")
               for ident, row in review["criteria"].items()}
    unknown = {ident: ids for ident, ids in unknown.items() if ids}
    unverified = sorted(ident for ident, row in review["criteria"].items() if row["status"] == "UNVERIFIED")
    state = ("UNRECONCILED" if reconciliation["unresolved"] else "INCOMPLETE" if unknown or unverified else
             "PROVISIONAL" if provenance != "git_commit_verified" or source.get("capture", {}).get("issue_completeness") != "verified_by_pagination"
             else "REVIEW_COMPLETE")
    return {"state": state, "unverified_criteria": unverified, "unknown_obligations": unknown,
            "unknown_obligation_count": sum(map(len, unknown.values())),
            "unresolved_reconciliation_count": len(reconciliation["unresolved"]),
            "obligation_count": sum(len(r["coverage"]) for r in review["criteria"].values())}
