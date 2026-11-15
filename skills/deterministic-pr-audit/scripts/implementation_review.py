"""Deterministic code-delivery grading from frozen, SHA-bound semantic adjudications.

No CI status, check exit code or PR description contributes to this score.
Review judgments are transparent INPUTS: source anchoring can be checked, but
semantic correctness still requires human/agent analysis and can vary unless
this exact ledger and its rubric are reused.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import quote

from audit_core import (
    AuditError, REQUIREMENTS_SCHEMA, SOURCE_SCHEMA, assert_valid_path,
    digest, git_bytes, require_schema, verify_commit_available,
)

REVIEW_SCHEMA = "pr-audit/implementation-review/v1"
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


def init_review(source: dict, requirements: dict) -> dict:
    require_schema(source, SOURCE_SCHEMA)
    require_schema(requirements, REQUIREMENTS_SCHEMA)
    if requirements["spec_digest"] != digest({
        "repository": source["repository"], "issue": source["issue"],
        "spec_files": source["spec_files"],
    }):
        raise AuditError("Review requirements are not bound to the current normative specification")
    return {
        "schema": REVIEW_SCHEMA,
        "source_digest": digest(source),
        "requirements_digest": digest(requirements),
        "head_sha": source["pull_request"]["head_sha"],
        "algorithm": ALGORITHM,
        "criteria": {item["id"]: {"status": "UNVERIFIED", "rationale": "", "trace": "", "evidence": [], "remaining": []}
                     for item in requirements["criteria"]},
    }


def validate_review(source: dict, requirements: dict, review: dict) -> None:
    require_schema(source, SOURCE_SCHEMA)
    require_schema(requirements, REQUIREMENTS_SCHEMA)
    require_schema(review, REVIEW_SCHEMA)
    if set(review) != {"schema", "source_digest", "requirements_digest", "head_sha", "algorithm", "criteria"}:
        raise AuditError("Code-review ledger forbids extra fields (including CI) and missing required fields")
    expected = init_review(source, requirements)
    for key in ("source_digest", "requirements_digest", "head_sha", "algorithm"):
        if review.get(key) != expected[key]:
            raise AuditError(f"Code-review ledger {key} differs from frozen source/rubric")
    rows = review.get("criteria")
    if not isinstance(rows, dict) or set(rows) != set(expected["criteria"]):
        raise AuditError("Code-review ledger must contain every AC/REQ exactly once")
    for ident, entry in rows.items():
        if not isinstance(entry, dict) or set(entry) != {"status", "rationale", "trace", "evidence", "remaining"}:
            raise AuditError(f"{ident}: expected status/rationale/trace/evidence/remaining")
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
    if repo_path is None and snapshots is None and assessed and not allow_provisional:
        raise AuditError("SOURCE_REQUIRED: code grading requires pinned Git objects or complete hashed source-file snapshots; explicitly use --allow-provisional only for a source-traced connector review")
    if repo_path is not None:
        verify_commit_available(repo_path, head)
        provenance = "git_commit_verified"
    else:
        provenance = ("captured_blob_only_unverified_tree_membership" if snapshots else
                      "provisional_connector_refs_unverified" if allow_provisional and assessed else
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
          snapshots: dict | None = None, allow_provisional: bool = False) -> dict:
    """Semantic coding judgments are frozen inputs; scores are deterministic and CI-free."""
    validate_review(source, requirements, review)
    provenance = verify_code_refs(source, review, repo_path=repo_path, snapshots=snapshots,
                                  allow_provisional=allow_provisional)
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
                     "remaining": row["remaining"], "evidence": row["evidence"]})
    return {
        "schema": GRADE_SCHEMA, "algorithm": ALGORITHM,
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
        "rows": rows,
        "limitations": [
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
        for remaining in item["remaining"]:
            lines.append(f"- **Remaining:** {remaining}")
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
    if left["identity"]["requirements_digest"] != right["identity"]["requirements_digest"]:
        raise AuditError("Not comparable: normative requirements changed")
    a, b = {r["id"]: r["status"] for r in left["rows"]}, {r["id"]: r["status"] for r in right["rows"]}
    if set(a) != set(b):
        raise AuditError("Not comparable: acceptance criterion inventory differs")
    if {k for k in a if a[k] == "UNVERIFIED"} != {k for k in b if b[k] == "UNVERIFIED"}:
        raise AuditError("Not comparable: assessed code coverage differs; review both candidates on a fixed common AC set")
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
        "scope": "Same frozen issue and assessed acceptance set; semantic adjudications remain review inputs, not runtime proof",
    }
