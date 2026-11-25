"""Deterministic code-delivery grading from frozen, SHA-bound semantic adjudications.

No CI status, check exit code or PR description contributes to this score.
Review judgments are transparent INPUTS: source anchoring can be checked, but
semantic correctness still requires human/agent analysis and can vary unless
this exact ledger and its rubric are reused.
"""
from __future__ import annotations

import hashlib
from copy import deepcopy
import re
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import quote

from audit_core import (
    AuditError, REQUIREMENTS_SCHEMA, SOURCE_SCHEMA, assert_valid_path,
    digest, extract_requirements, git_bytes, require_schema, verify_commit_available,
)

from reproducible_review import validate_plan, scaffold, validate_scope, reconcile, review_closure, obligation_id, history_identity

REVIEW_SCHEMA = "pr-audit/implementation-review/v1"
COVERAGE_REVIEW_SCHEMA = "pr-audit/implementation-review/v2"
COVERAGE_POLICY = "symmetric-obligation-evidence-v2"
FROZEN_REVIEW_SCHEMA = "pr-audit/implementation-review/v3"
FROZEN_POLICY = "frozen-obligation-reconciliation-v3"
COVERAGE_SCHEMAS = (COVERAGE_REVIEW_SCHEMA, FROZEN_REVIEW_SCHEMA)
SNAPSHOTS_SCHEMA = "pr-audit/code-snapshots/v1"
GRADE_SCHEMA = "pr-audit/implementation-grade/v1"
ALGORITHM = "code-delivery-v1"
STATES = ("COMPLETE", "PARTIAL", "MISSING", "UNVERIFIED")
ROLES = ("entrypoint", "implementation", "guard", "result", "counterexample", "test")
MAX_FILES = 250
MAX_FILE_BYTES = 2_000_000


def blob_sha(content: bytes) -> str:
    """Git SHA-1 object identity, not a semantic proof of code correctness."""
    return hashlib.sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()


def init_review(source: dict, requirements: dict, *, coverage: bool = False, obligation_plan: dict | None = None,
                audit_history: dict | None = None) -> dict:
    require_schema(source, SOURCE_SCHEMA)
    require_schema(requirements, REQUIREMENTS_SCHEMA)
    if requirements["spec_digest"] != digest({
        "repository": source["repository"], "issue": source["issue"],
        "spec_files": source["spec_files"],
    }):
        raise AuditError("Review requirements are not bound to the current normative specification")
    frozen = obligation_plan is not None
    coverage = coverage or frozen
    if frozen != (audit_history is not None):
        raise AuditError("V3 initialization requires the frozen plan and explicit prior audit inventory together")
    if frozen:
        validate_plan(source, requirements, obligation_plan)
    if coverage and requirements != extract_requirements(source, canonical_ids=True):
        raise AuditError("Coverage review requires canonical requirements from the frozen original specification; capture with --require-coverage")
    return {
        "schema": FROZEN_REVIEW_SCHEMA if frozen else COVERAGE_REVIEW_SCHEMA if coverage else REVIEW_SCHEMA,
        **({"obligation_plan_digest": digest(obligation_plan),
            "history_inventory_digest": history_identity(audit_history)} if frozen else {}),
        "source_digest": digest(source),
        "requirements_digest": digest(requirements),
        "head_sha": source["pull_request"]["head_sha"],
        "algorithm": ALGORITHM,
        "criteria": {item["id"]: {"status": "UNVERIFIED", "rationale": "", "trace": "", "evidence": [], "remaining": [],
                                  **({"coverage": scaffold(obligation_plan, item["id"]) if frozen else []} if coverage else {})}
                     for item in requirements["criteria"]},
    }


def validate_review(source: dict, requirements: dict, review: dict, *, obligation_plan: dict | None = None,
                    audit_history: dict | None = None) -> None:
    require_schema(source, SOURCE_SCHEMA)
    require_schema(requirements, REQUIREMENTS_SCHEMA)
    frozen = review.get("schema") == FROZEN_REVIEW_SCHEMA
    coverage = review.get("schema") in COVERAGE_SCHEMAS
    if frozen != (obligation_plan is not None):
        raise AuditError("V3 review requires the separate frozen obligation plan; legacy review cannot use it")
    if not coverage:
        require_schema(review, REVIEW_SCHEMA)
    fields = {"schema", "source_digest", "requirements_digest", "head_sha", "algorithm", "criteria"}
    if frozen:
        fields.update(("obligation_plan_digest", "history_inventory_digest"))
    if set(review) != fields:
        raise AuditError("Code-review ledger forbids extra fields (including CI) and missing required fields")
    expected = init_review(source, requirements, coverage=coverage, obligation_plan=obligation_plan, audit_history=audit_history)
    for key in ("source_digest", "requirements_digest", "head_sha", "algorithm"):
        if review.get(key) != expected[key]:
            raise AuditError(f"Code-review ledger {key} differs from frozen source/rubric")
    rows = review.get("criteria")
    if not isinstance(rows, dict) or set(rows) != set(expected["criteria"]):
        raise AuditError("Code-review ledger must contain every AC/REQ exactly once")
    for ident, entry in rows.items():
        fields = {"status", "rationale", "trace", "evidence", "remaining"}
        if coverage:
            fields.add("coverage")
        if not isinstance(entry, dict) or set(entry) != fields:
            raise AuditError(f"{ident}: expected review fields {sorted(fields)}")
        status, rationale, trace, refs, remaining = (entry[key] for key in ("status", "rationale", "trace", "evidence", "remaining"))
        if status not in STATES:
            raise AuditError(f"{ident}: unsupported code-delivery status")
        if not isinstance(rationale, str) or not isinstance(trace, str) or not isinstance(refs, list) or not isinstance(remaining, list):
            raise AuditError(f"{ident}: invalid review fields")
        if not all(isinstance(item, str) and len(item.strip()) >= 10 for item in remaining):
            raise AuditError(f"{ident}: remaining behaviors require specific descriptions")
        if status != "UNVERIFIED" and (len(rationale.strip()) < 40 or len(trace.strip()) < 40):
            raise AuditError(f"{ident}: adjudicated state requires a substantive rationale and entrypoint-to-result trace")
        if status == "COMPLETE" and remaining:
            raise AuditError(f"{ident}: COMPLETE cannot have remaining required behavior")
        if status == "PARTIAL" and not remaining:
            raise AuditError(f"{ident}: PARTIAL must identify concrete missing behavior")
        if status == "MISSING" and not remaining:
            raise AuditError(f"{ident}: MISSING must identify the absent behavior")
        if status != "UNVERIFIED" and not refs:
            raise AuditError(f"{ident}: no source-backed evidence for an adjudicated state")
        roles = set()
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {"path", "blob_sha", "line_start", "line_end", "role", "claim"}:
                raise AuditError(f"{ident}: malformed source reference")
            assert_valid_path(ref["path"])
            if not isinstance(ref["blob_sha"], str) or not re.fullmatch("[a-f0-9]{40}", ref["blob_sha"]):
                raise AuditError(f"{ident}: source reference needs full Git blob SHA")
            a, b = ref["line_start"], ref["line_end"]
            if not all(isinstance(n, int) and not isinstance(n, bool) for n in (a, b)) or not 1 <= a <= b <= a + 79:
                raise AuditError(f"{ident}: source line span must be 1..80 lines")
            if ref["role"] not in ROLES or not isinstance(ref["claim"], str) or len(ref["claim"].strip()) < 20:
                raise AuditError(f"{ident}: invalid role or unsupported claim")
            roles.add(ref["role"])
        if status in ("COMPLETE", "PARTIAL") and "implementation" not in roles and "result" not in roles:
            raise AuditError(f"{ident}: source-code implementation/result trace required")
        if status == "MISSING" and "counterexample" not in roles:
            raise AuditError(f"{ident}: MISSING needs an observed negative code path, not an absence guess")

    if frozen:
        if review["history_inventory_digest"] != expected["history_inventory_digest"]:
            raise AuditError("Prior audit inventory changed after initialization; use a new review with the same frozen plan")
        validate_scope(review, obligation_plan)


ADJUDICATION_POLICY = "normative-gap-evidence-v1"
GAP_KINDS = ("behavior", "mandatory_test", "documentation", "delivery_config")


def validate_adjudication(source: dict, requirements: dict, review: dict) -> None:
    """Require a cited normative obligation and negative evidence for each penalty.

    This is a structural admission gate, not an automated semantic oracle. The
    reviewer must reconcile counterevidence and classify the actual obligation.
    Existing frozen v1 ledgers remain replayable without this opt-in gate.
    """
    normative = " ".join(" ".join(text.split()) for text in [
        source["issue"]["body"],
        *(c["body"] for c in source["issue"]["comments"]),
        *(s["body"] for s in source["spec_files"]),
    ])
    criteria = {c["id"]: c["text"] for c in requirements["criteria"]}
    for ident, row in review["criteria"].items():
        if row["status"] not in ("PARTIAL", "MISSING"):
            continue
        negative = {f"{r['path']}:L{r['line_start']}-L{r['line_end']}"
                    for r in row["evidence"] if r["role"] == "counterexample"}
        for remaining in row["remaining"]:
            parts = [p.strip() for p in remaining.split(" | ", 4)]
            if len(parts) != 5:
                raise AuditError(f"{ident}: adjudication gap needs kind | normative quote | counterexample anchor | observed gap | counterevidence reconciliation")
            kind, obligation, anchor, observed, reconciliation = parts
            if kind not in GAP_KINDS:
                raise AuditError(f"{ident}: unsupported normative gap kind: {kind}")
            quote_text = " ".join(obligation.split())
            if len(quote_text) < 12 or (quote_text not in criteria[ident] and quote_text not in normative):
                raise AuditError(f"{ident}: gap needs an exact quote from the frozen normative specification")
            if anchor not in negative:
                raise AuditError(f"{ident}: gap needs its own cited counterexample source anchor")
            if len(observed) < 20 or len(reconciliation) < 20:
                raise AuditError(f"{ident}: gap needs a specific observed result and counterevidence reconciliation")


def polarity_subjects(text: str) -> list[str]:
    """Recognize the explicit grammar 'X, Y and Z have positive and negative tests'.

    This is a narrow safeguard, not a natural-language completeness oracle.
    Other formulations must be decomposed by the reviewer under the protocol.
    """
    match = re.search(r"(?:^|[;.!?]\s*)([^;.!?]+?)\s+(?:have|has)\s+positive\s+and\s+negative\s+tests\b", text, re.I)
    if not match:
        return []
    return [part.strip().casefold() for part in re.split(r",\s*(?:and\s+)?|\s+and\s+", match.group(1), flags=re.I) if part.strip()]


def validate_coverage(source: dict, requirements: dict, review: dict) -> None:
    """Symmetric, structural admission gate for both completion and deficits.

    Witnesses are analyst observations, not executed tests. The gate cannot
    prove that the decomposition or described causal path is semantically true.
    """
    criteria = {c["id"]: c["text"] for c in requirements["criteria"]}
    normative = " ".join(" ".join(text.split()) for text in [
        source["issue"]["body"], *(c["body"] for c in source["issue"]["comments"]),
        *(s["body"] for s in source["spec_files"]),
    ])
    for ident, row in review["criteria"].items():
        obligations = row["coverage"]
        if not isinstance(obligations, list) or (row["status"] != "UNVERIFIED" and not obligations):
            raise AuditError(f"{ident}: every adjudicated criterion needs obligation coverage")
        if not obligations:
            continue
        text = " ".join(criteria[ident].split())
        anchors = {}
        for ref in row["evidence"]:
            anchor = f"{ref['path']}:L{ref['line_start']}-L{ref['line_end']}"
            anchors.setdefault(anchor, set()).add(ref["role"])
        seen = set()
        paired = set()
        outcomes = set()
        gap_anchors = set()
        fields = {"kind", "quote", "subject", "polarity", "verdict", "anchor", "witness"}
        for obligation in obligations:
            if not isinstance(obligation, dict) or set(obligation) != fields or not all(isinstance(v, str) for v in obligation.values()):
                raise AuditError(f"{ident}: malformed obligation coverage; expected {sorted(fields)}")
            kind, quote_text, subject, polarity, verdict, anchor, witness = (obligation[k].strip() for k in ("kind", "quote", "subject", "polarity", "verdict", "anchor", "witness"))
            if kind not in GAP_KINDS or polarity not in ("positive", "negative", "none") or verdict not in ("SATISFIED", "GAP", "UNKNOWN"):
                raise AuditError(f"{ident}: invalid obligation kind, polarity or verdict")
            quote_text = " ".join(quote_text.split())
            subject = " ".join(subject.split()).casefold()
            if (not quote_text or (quote_text not in text and not (ident.startswith("REQ-") and quote_text in normative))
                    or not subject or len(witness) < 40):
                raise AuditError(f"{ident}: coverage needs an exact criterion quote, subject and specific causal witness")
            key = (kind, subject, polarity)
            if key in seen:
                raise AuditError(f"{ident}: duplicate obligation coverage: {key}")
            seen.add(key)
            outcomes.add(verdict)
            if kind == "mandatory_test" and polarity != "none":
                if subject in polarity_subjects(text) and (subject not in quote_text.casefold() or
                        not re.search(r"\bpositive\s+and\s+negative\s+tests\b", quote_text, re.I)):
                    raise AuditError(f"{ident}: explicit test polarity witness must quote its named subject and test obligation")
                paired.add((subject, polarity))
            if verdict == "UNKNOWN":
                if anchor and anchor not in anchors:
                    raise AuditError(f"{ident}: unknown obligation anchor must cite inspected source")
                continue
            roles = anchors.get(anchor, set())
            if verdict == "GAP":
                if "counterexample" not in roles:
                    raise AuditError(f"{ident}: proven obligation gap requires counterexample anchor")
                gap_anchors.add((kind, anchor))
            elif kind == "mandatory_test":
                if not roles.intersection({"test", "result"}):
                    raise AuditError(f"{ident}: satisfied mandatory test requires a test/result anchor, not production code alone")
                # Three explicit observations, not mere test presence. Each
                # witness must describe the actual stimulus, causal reachability
                # through the tested branch, and externally asserted effect.
                parts = [v.strip() for v in witness.split(" | ", 2)]
                if len(parts) != 3 or any(len(part) < 12 for part in parts):
                    raise AuditError(f"{ident}: test witness needs input | reached predicate/path | asserted effect")
            elif not roles.intersection({"implementation", "result", "entrypoint", "guard", "test"}):
                raise AuditError(f"{ident}: satisfied obligation requires affirmative source evidence")
        if row["status"] != "UNVERIFIED":
            required = {(subject, polarity) for subject in polarity_subjects(text) for polarity in ("positive", "negative")}
            if not required.issubset(paired):
                raise AuditError(f"{ident}: missing explicit test polarity coverage: {sorted(required - paired)}")
            if re.search(r"\bpositive\s+and\s+negative\b", text, re.I) and not required:
                positives = {s for s, p in paired if p == "positive"}
                negatives = {s for s, p in paired if p == "negative"}
                if not positives or positives != negatives:
                    raise AuditError(f"{ident}: positive and negative test obligations require paired subjects")
        expected = ("COMPLETE" if outcomes == {"SATISFIED"} else
                    "MISSING" if outcomes == {"GAP"} else
                    "PARTIAL" if {"SATISFIED", "GAP"}.issubset(outcomes) else "UNVERIFIED")
        if row["status"] != expected:
            raise AuditError(f"{ident}: obligation verdicts imply {expected}, not {row['status']}")
        if expected in ("PARTIAL", "MISSING"):
            # Cross-link every proved gap with the existing typed remaining ledger.
            remaining_anchors = set()
            for remaining in row["remaining"]:
                kind, _, anchor, _, _ = [v.strip() for v in remaining.split(" | ", 4)]
                remaining_anchors.add((kind, anchor))
            if gap_anchors != remaining_anchors:
                raise AuditError(f"{ident}: obligation gaps and typed remaining anchors disagree")


def validate_snapshots(source: dict, snapshots: dict) -> dict[str, bytes]:
    require_schema(snapshots, SNAPSHOTS_SCHEMA)
    if snapshots.get("source_digest") != digest(source) or snapshots.get("head_sha") != source["pull_request"]["head_sha"]:
        raise AuditError("Source snapshots belong to a different issue or HEAD")
    files = snapshots.get("files")
    if not isinstance(files, list) or len(files) > MAX_FILES:
        raise AuditError("Invalid number of source snapshots")
    output = {}
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "blob_sha", "content"}:
            raise AuditError("Malformed source snapshot")
        path = assert_valid_path(item["path"])
        if path in output or not isinstance(item["content"], str):
            raise AuditError("Duplicate path or invalid source snapshot content")
        data = item["content"].encode("utf-8")
        if len(data) > MAX_FILE_BYTES or blob_sha(data) != item["blob_sha"]:
            raise AuditError(f"Source snapshot blob integrity failure: {path}")
        output[path] = data
    return output


def verify_code_refs(source: dict, review: dict, *, repo_path: str | Path | None = None,
                     snapshots: dict | None = None, allow_provisional: bool = False) -> str:
    head = source["pull_request"]["head_sha"]
    assessed = any(r["status"] != "UNVERIFIED" for r in review["criteria"].values())
    cited = assessed or (review.get("schema") in COVERAGE_SCHEMAS and
                         any(r["evidence"] for r in review["criteria"].values()))
    if repo_path is None and snapshots is None and cited and not allow_provisional:
        raise AuditError("SOURCE_REQUIRED: code grading requires pinned Git objects or complete hashed source-file snapshots; explicitly use --allow-provisional only for a source-traced connector review")
    if repo_path is not None:
        verify_commit_available(repo_path, head)
        provenance = "git_commit_verified"
    else:
        provenance = ("captured_blob_only_unverified_tree_membership" if snapshots else
                      "provisional_connector_refs_unverified" if allow_provisional and cited else
                      "no_source_code_reviewed")
    external = validate_snapshots(source, snapshots) if snapshots is not None else {}
    # Explicit fallback only: citation SHAs and line ranges are declared in the
    # review ledger but have NOT been independently checked against candidate HEAD.
    if provenance == "provisional_connector_refs_unverified":
        return provenance
    cache: dict[str, bytes] = {}
    for ident, entry in review["criteria"].items():
        for ref in entry["evidence"]:
            path = ref["path"]
            if path not in cache:
                if repo_path is not None:
                    # Always read immutable Git HEAD, not the working tree.
                    cache[path] = git_bytes(repo_path, "show", f"{head}:{path}")
                elif path in external:
                    cache[path] = external[path]
                else:
                    raise AuditError(f"{ident}: no frozen source blob for {path}")
            contents = cache[path]
            if blob_sha(contents) != ref["blob_sha"]:
                raise AuditError(f"{ident}: blob SHA mismatch at {head}:{path}")
            lines = contents.splitlines()
            if ref["line_end"] > len(lines):
                raise AuditError(f"{ident}: out-of-range source lines at {path}")
            if not any(line.strip() for line in lines[ref["line_start"] - 1:ref["line_end"]]):
                raise AuditError(f"{ident}: cited source span is empty at {path}")
    return provenance


def _percent(numerator: int, denominator: int) -> str | None:
    if not denominator:
        return None
    return str((Decimal(numerator) * 100 / Decimal(denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _group(ids: list[str], review: dict) -> dict:
    counts = {key: 0 for key in STATES}
    for ident in ids:
        counts[review["criteria"][ident]["status"]] += 1
    known = len(ids) - counts["UNVERIFIED"]
    # One vote per frozen acceptance criterion. A parent REQ is never an extra AC.
    partial_units = counts["COMPLETE"] * 2 + counts["PARTIAL"]
    return {
        "total": len(ids), "assessed": known, "counts": counts,
        "assessed_pct": _percent(known, len(ids)),
        # Always numeric. UNVERIFIED criteria contribute no credit: this is a
        # conservative evidence floor, never an imputed progress estimate.
        "numeric_delivery_grade_pct": _percent(partial_units, len(ids) * 2) if ids else "0.00",
        "numeric_delivery_grade_kind": "complete_review" if ids and known == len(ids) else "conservative_lower_bound",
        "functional_completion_assessed_pct": _percent(counts["COMPLETE"], known),
        "development_progress_assessed_pct": _percent(partial_units, known * 2),
        "functional_completion_lower_pct": _percent(counts["COMPLETE"], len(ids)),
        "functional_completion_upper_pct": _percent(counts["COMPLETE"] + counts["UNVERIFIED"], len(ids)),
        "development_progress_lower_pct": _percent(partial_units, len(ids) * 2),
        "development_progress_upper_pct": _percent(partial_units + 2 * counts["UNVERIFIED"], len(ids) * 2),
    }


def grade(source: dict, requirements: dict, review: dict, *, repo_path: str | Path | None = None,
          snapshots: dict | None = None, allow_provisional: bool = False,
          require_adjudication: bool = False, require_coverage: bool = False,
          obligation_plan: dict | None = None, audit_history: dict | None = None) -> dict:
    """Semantic coding judgments are frozen inputs; scores are deterministic and CI-free."""
    validate_review(source, requirements, review, obligation_plan=obligation_plan, audit_history=audit_history)
    frozen = review.get("schema") == FROZEN_REVIEW_SCHEMA
    coverage = review.get("schema") in COVERAGE_SCHEMAS
    if frozen != (audit_history is not None):
        raise AuditError("V3 review requires explicit audit history; legacy review cannot use it")
    if require_coverage and not coverage:
        raise AuditError("Coverage-gated audit requires a v2 review or v3 frozen review; initialize with --require-coverage or the separate plan/history")
    if require_adjudication or coverage:
        validate_adjudication(source, requirements, review)
    if coverage:
        validate_coverage(source, requirements, review)
    provenance = verify_code_refs(source, review, repo_path=repo_path, snapshots=snapshots,
                                  allow_provisional=allow_provisional)
    reconciliation = reconcile(source, requirements, review, obligation_plan, audit_history) if frozen else None
    closure = review_closure(review, reconciliation, provenance, source) if frozen else None
    ids = [item["id"] for item in requirements["criteria"]]
    ac = [ident for ident in ids if ident.startswith("AC-") or ident.startswith("CHK-")]
    parent = [ident for ident in ids if ident.startswith("REQ-")]
    chosen = ac if ac else parent
    rows = []
    for crit in requirements["criteria"]:
        ident = crit["id"]
        row = review["criteria"][ident]
        rows.append({"id": ident, "text": crit["text"], "status": row["status"],
                     "rationale": row["rationale"], "trace": row["trace"],
                     "remaining": row["remaining"], "evidence": row["evidence"],
                     **({"coverage": row["coverage"]} if coverage else {})})
    return {
        "schema": GRADE_SCHEMA, "algorithm": ALGORITHM,
        **({"adjudication_policy": FROZEN_POLICY if frozen else COVERAGE_POLICY if coverage else ADJUDICATION_POLICY} if require_adjudication or coverage else {}),
        **({"coverage_scope_digest": digest({ident: sorted([
            [obligation["kind"], " ".join(obligation["quote"].split()),
             " ".join(obligation["subject"].split()).casefold(), obligation["polarity"]]
            for obligation in row["coverage"]]) for ident, row in review["criteria"].items()})} if coverage else {}),
        **({"obligation_plan_digest": digest(obligation_plan), "reconciliation": reconciliation,
            "review_closure": closure} if frozen else {}),
        "identity": {"source_digest": digest(source), "requirements_digest": digest(requirements),
                     "review_digest": digest(review), "snapshots_digest": digest(snapshots) if snapshots else None,
                     "head_sha": source["pull_request"]["head_sha"]},
        "repository": source["repository"], "pr_number": source["pull_request"]["number"],
        "issue_number": source["issue"]["number"], "code_provenance": provenance,
        "source_evidence_level": ("git_verified" if provenance == "git_commit_verified" else
                                  "blob_integrity_checked" if snapshots is not None else
                                  "provisional_unchecked" if provenance == "provisional_connector_refs_unverified"
                                  else "no_code_review"),
        "ci_affects_grade": False, "rubric": {"COMPLETE": 1, "PARTIAL": "0.5", "MISSING": 0,
                                               "UNVERIFIED": "excluded from assessed-only; included in bounds"},
        "summary": _group(chosen, review),
        "acceptance_criteria": _group(ac, review),
        "parent_requirements": _group(parent, review),
        "rows": deepcopy(rows) if frozen else rows,
        "limitations": [
            *(["Symmetric obligation evidence is structurally validated for both positive completion and proven gaps. It is not a semantic oracle or evidence that tests ran."] if coverage else []),
            *(["Strict adjudication verifies gap structure, not semantic correctness. Scores are equal-weight normative AC conformance proxies, not measured implementation effort or percentage of code written. Mandatory test/documentation/configuration gaps are not necessarily runtime defects."] if require_adjudication else []),
            *(["Frozen plan and supplied prior-audit history are mechanically bound. Semantic decomposition, completeness of prior-audit discovery and resolution quality still require reviewer judgment. Shared source overlap is a review lead, not a propagated defect. Incomplete/unreconciled grades are diagnostic floors, not final implementation assessments."] if frozen else []),
            "Only identical frozen requirements, reviewed code judgments and algorithm replay identically; independent model re-adjudication can differ.",
            "Source-line and Git-blob identity validation does not prove the analyst's semantic claim or reachability; inspect the control flow.",
            "No CI status, generic test pass, diff size, self-reported issue ledger or PR checkbox enters this grade.",
            "Assessed-only percentages omit UNVERIFIED requirements; inspect coverage and lower/upper bounds before interpreting the grade.",
            "Numeric grade is the conservative issue-wide progress floor. With zero assessed criteria, 0/100 means zero DEMONSTRATED implementation, not zero implemented code; it is a diagnostic.",
            *(["PROVISIONAL: cited Git blobs and line spans were NOT checked against candidate HEAD; validate full blobs to upgrade provenance."] if provenance == "provisional_connector_refs_unverified" else []),
            *(["Captured code snapshots verify blob contents but do not independently prove Git commit tree membership."] if repo_path is None else []),
            *(["Normative issue completeness was not independently verified."] if source.get("capture", {}).get("issue_completeness") != "verified_by_pagination" else []),
        ],
    }


def markdown_grade(report: dict) -> str:
    require_schema(report, GRADE_SCHEMA)
    g = report["summary"]
    fmt = lambda p: "N/A" if p is None else f"{p}%"
    lines = [
        f"# Code-delivery audit — {report['repository']} PR #{report['pr_number']}", "",
        f"- **HEAD:** `{report['identity']['head_sha']}`",
        f"- **Numeric delivery grade (0–100, conservative floor):** {g['numeric_delivery_grade_pct']}/100",
        f"- **Grade basis:** {g['numeric_delivery_grade_kind']} ({report['source_evidence_level']})",
        *([f"- **Adjudication gate:** {report['adjudication_policy']} (structural only)"] if "adjudication_policy" in report else []),
        f"- **Development progress (assessed scope):** {fmt(g['development_progress_assessed_pct'])}",
        f"- **Functional completion (assessed scope):** {fmt(g['functional_completion_assessed_pct'])}",
        f"- **Requirements assessed:** {g['assessed']}/{g['total']} ({fmt(g['assessed_pct'])})",
        f"- **Issue-wide development range:** {fmt(g['development_progress_lower_pct'])}–{fmt(g['development_progress_upper_pct'])}",
        f"- **Issue-wide functional completion range:** {fmt(g['functional_completion_lower_pct'])}–{fmt(g['functional_completion_upper_pct'])}",
        "- **CI influence on all scores:** none", "",
        "**Interpretation:** no completion credit is invented for unknown criteria. With 0 assessed criteria, a numeric 0/100 is ONLY an evidence floor, not an assessment of how much code was built; do not use this diagnostic as a final review.", "",
        "The progress score counts `COMPLETE=1`, `PARTIAL=0.5`, `MISSING=0` for reviewed requirements. Functional completion counts only `COMPLETE`. An unreviewed criterion is **UNKNOWN, not missing**. Both scores are implementation assessments, not test-pass rates.", "",
        "## Acceptance-criteria inventory", "",
        "| Status | Count |", "|---|---:|",
    ]
    if "review_closure" in report:
        closure = report["review_closure"]
        state = closure["state"]
        lines[2:2] = [f"**Audit state: {state}.** {closure['unknown_obligation_count']} unknown obligations; {closure['unresolved_reconciliation_count']} unresolved reconciliation leads. "
                      + ("Diagnostic evidence floor; NOT a final audit." if state != "REVIEW_COMPLETE" else "All planned obligations adjudicated; not independent proof of semantic correctness."), ""]
    for state, count in report["acceptance_criteria"]["counts"].items():
        lines.append(f"| {state} | {count} |")
    lines += ["", "## Criterion-by-criterion code evidence", ""]
    for item in report["rows"]:
        lines += [f"### {item['id']} — {item['status']}", "", item["text"], ""]
        if item["rationale"]:
            lines += [f"**Reason:** {item['rationale']}", ""]
        if item["trace"]:
            lines += [f"**Code path:** {item['trace']}", ""]
        for ref in item["evidence"]:
            path = quote(ref["path"], safe="/")
            url = f"https://github.com/{report['repository']}/blob/{report['identity']['head_sha']}/{path}#L{ref['line_start']}-L{ref['line_end']}"
            lines.append(f"- `{ref['role']}` — [{ref['path']}:{ref['line_start']}-{ref['line_end']}]({url}), blob `{ref['blob_sha']}` — {ref['claim']}")
        for obligation in item.get("coverage", []):
            lines.append(f"- **Obligation ({obligation['kind']}, {obligation['polarity']}) — {obligation['verdict']}:** {obligation['subject']} | {obligation['quote']} | {obligation['anchor']} | {obligation['witness']}")
        for remaining in item["remaining"]:
            lines.append(f"- **Remaining:** {remaining}")
        lines.append("")
    if "reconciliation" in report:
        rec = report["reconciliation"]
        lines += ["## Reconciliation and unresolved coverage", "",
                  f"- Frozen obligation plan: `{report['obligation_plan_digest']}`",
                  f"- Prior audit search: {rec['search']}",
                  f"- Prior reports inspected: {len(rec['prior_reports'])}",
                  "- Unknown criteria: " + (", ".join(report["review_closure"]["unverified_criteria"]) or "none"), ""]
        for prior in rec["prior_reports"]:
            details = (f"; matched {prior['matched_criteria']}/{prior['prior_criteria']} prior criteria; plan {prior['plan_identity']}"
                       if "matched_criteria" in prior else "")
            lines.append(f"- Prior `{prior['digest']}` ({prior['format']}): {prior['disposition']}{details}")
        for lead in rec["leads"]:
            key = lead["id"]
            detail = (f"{lead['prior_status']} -> {lead['current_status']}" if lead["kind"].startswith("prior_") else
                      f"{lead['path']}:{lead['line_start']}-{lead['line_end']} shared with {', '.join(lead['gap_criteria'])}")
            lines.append(f"- `{key}` — {lead['criterion']} / {lead['kind']}: {detail}; " +
                         ("RESOLVED — " + rec["resolutions"][key]["rationale"] if key in rec["resolutions"] else "UNRESOLVED"))
        lines.append("")
    lines += ["## Limits of deterministic scoring", ""]
    lines.extend(f"- {value}" for value in report["limitations"])
    return "\n".join(lines) + "\n"


def compare_grades(left: dict, right: dict) -> dict:
    """Compare the exact same AC scope and rubric; ignore CI entirely."""
    require_schema(left, GRADE_SCHEMA)
    require_schema(right, GRADE_SCHEMA)
    if left.get("algorithm") != ALGORITHM or right.get("algorithm") != ALGORITHM:
        raise AuditError("Code-delivery reports use different algorithms")
    if left.get("adjudication_policy") != right.get("adjudication_policy"):
        raise AuditError("Not comparable: adjudication policies differ; re-adjudicate both candidates under one policy")
    if left["identity"]["requirements_digest"] != right["identity"]["requirements_digest"]:
        raise AuditError("Not comparable: normative requirements changed")
    a, b = {r["id"]: r["status"] for r in left["rows"]}, {r["id"]: r["status"] for r in right["rows"]}
    if set(a) != set(b):
        raise AuditError("Not comparable: acceptance criterion inventory differs")
    if left.get("adjudication_policy") == FROZEN_POLICY:
        if left.get("obligation_plan_digest") != right.get("obligation_plan_digest"):
            raise AuditError("Not comparable: frozen obligation plans differ")
        if any(r.get("review_closure", {}).get("state") not in ("REVIEW_COMPLETE", "PROVISIONAL") for r in (left, right)):
            raise AuditError("Not comparable: incomplete or unreconciled audit; resolve evidence before reporting progress")
        if left["identity"]["head_sha"] == right["identity"]["head_sha"]:
            def verdicts(report):
                return {(r["id"], obligation_id(r["id"], o)): o["verdict"] for r in report["rows"] for o in r.get("coverage", [])}
            if a != b or verdicts(left) != verdicts(right):
                raise AuditError("Same HEAD has divergent semantic verdicts; reconcile before reporting progress")
    if {k for k in a if a[k] == "UNVERIFIED"} != {k for k in b if b[k] == "UNVERIFIED"}:
        raise AuditError("Not comparable: assessed code coverage differs; review both candidates on a fixed common AC set")
    if left.get("adjudication_policy") == COVERAGE_POLICY and left.get("coverage_scope_digest") != right.get("coverage_scope_digest"):
        raise AuditError("Not comparable: obligation coverage scopes differ; freeze and reconcile the same scope")
    if left.get("adjudication_policy") == COVERAGE_POLICY and left["identity"]["head_sha"] == right["identity"]["head_sha"] and a != b:
        raise AuditError("Same HEAD has divergent semantic verdicts; reconcile obligation evidence before reporting progress")
    if not left["summary"]["assessed"] or not right["summary"]["assessed"]:
        raise AuditError("Not comparable: no code-observed requirements")
    before = Decimal(left["summary"]["development_progress_assessed_pct"])
    after = Decimal(right["summary"]["development_progress_assessed_pct"])
    return {
        "schema": "pr-audit/implementation-comparison/v1", "algorithm": ALGORITHM,
        "requirements_digest": left["identity"]["requirements_digest"],
        "assessed_count": left["summary"]["assessed"],
        "left": {"head_sha": left["identity"]["head_sha"], "progress_pct": str(before)},
        "right": {"head_sha": right["identity"]["head_sha"], "progress_pct": str(after)},
        "progress_delta_points": str((after - before).quantize(Decimal("0.01"))),
        "transitions": [{"id": ident, "before": a[ident], "after": b[ident]} for ident in sorted(a) if a[ident] != b[ident]],
        **({"review_states": [left["review_closure"]["state"], right["review_closure"]["state"]]}
           if left.get("adjudication_policy") == FROZEN_POLICY else {}),
        "scope": "Same frozen issue and assessed acceptance set; semantic adjudications remain review inputs, not runtime proof",
    }
