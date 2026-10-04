#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wiki_common import atomic_write_json, load_json, parse_frontmatter, sha256_file  # noqa: E402

SCHEMA_RE = re.compile(r"(?mi)^\s*schema_version\s*:\s*['\"]?([^'\"\s]+)")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
LOG_RE = re.compile(r"(?m)^## \[(\d{4}-\d{2}-\d{2})\] (initialize|ingest|query-persist|lint|schema-change) \| .+$")
PAGE_DIRS = {"sources": "source", "entities": "entity", "concepts": "concept", "syntheses": "synthesis", "claims": "claim"}
LINEAGE_FIELDS = (
    "derived_from_source_ids",
    "revision_of_source_ids",
    "quoted_from_source_ids",
    "primary_source_ids",
    "alternate_source_ids",
)
CLAIM_REF_FIELDS = ("depends_on_claim_ids", "supersedes_claim_ids")
ENTITY_REF_FIELDS = ("alias_page_ids", "possible_same_entity_page_ids", "merged_into_page_ids", "split_from_page_ids")
VALUE_STATES = {"known", "unknown", "none"}


def _severity(status: str) -> str:
    return {"fail": "error", "warn": "warning", "needs-review": "review", "pass": "info"}.get(status, "info")


def add(findings, layer, code, status, subject, evidence=None, repairability=None):
    findings.append(
        {
            "layer": layer,
            "code": code,
            "rule_id": code,
            "status": status,
            "severity": _severity(status),
            "subject": subject,
            "focus": subject,
            "repairability": repairability or ("semantic-review" if layer == "semantic" else ("none" if status == "pass" else "mechanical-candidate")),
            "evidence": evidence or {},
        }
    )


def _resolve_wikilink(wiki: Path, source_page: Path, target: str, stems: dict[str, list[Path]]) -> bool | None:
    target = target.strip()
    if "/" in target or target.endswith(".md"):
        cand = target if target.endswith(".md") else target + ".md"
        p1 = (source_page.parent / cand).resolve(strict=False)
        p2 = (wiki / cand).resolve(strict=False)
        return p1.exists() or p2.exists()
    matches = stems.get(Path(target).stem.casefold(), [])
    if len(matches) == 1:
        return True
    if len(matches) == 0:
        return False
    return None


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 1.0


def validate(workspace: Path, strict: bool) -> tuple[int, dict]:
    workspace = workspace.resolve(strict=True)
    wiki = workspace / "wiki"
    findings: list[dict] = []
    semantic: list[dict] = []
    schema_path = workspace / "WIKI_SCHEMA.md"
    schema_version = None
    if not schema_path.is_file():
        add(findings, "structural", "schema/missing", "fail" if strict else "warn", "WIKI_SCHEMA.md")
    else:
        match = SCHEMA_RE.search(schema_path.read_text(encoding="utf-8"))
        if match:
            schema_version = match.group(1)
            add(findings, "structural", "schema/version", "pass", "WIKI_SCHEMA.md", {"schema_version": schema_version})
        else:
            add(findings, "structural", "schema/version-missing", "fail" if strict else "warn", "WIKI_SCHEMA.md")

    manifest_path = workspace / ".llm-wiki" / "source-manifest.json"
    manifest = load_json(manifest_path, {"sources": {}, "paths": {}})
    known_sources = set(manifest.get("sources", {}))

    pages: list[Path] = []
    page_texts: dict[Path, str] = {}
    stems: dict[str, list[Path]] = {}
    if wiki.exists():
        for page in sorted(wiki.rglob("*.md")):
            stems.setdefault(page.stem.casefold(), []).append(page)
            if page.name in {"index.md", "log.md"}:
                continue
            try:
                rel_dir = page.relative_to(wiki).parts[0]
            except Exception:
                continue
            if rel_dir in PAGE_DIRS:
                pages.append(page)
                page_texts[page] = page.read_text(encoding="utf-8")

    if strict and not manifest_path.exists() and any(p.relative_to(wiki).parts[0] == "sources" for p in pages):
        add(findings, "structural", "provenance/source-manifest-missing", "fail", manifest_path.relative_to(workspace).as_posix())

    index_path = wiki / "index.md"
    log_path = wiki / "log.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    if not index_path.is_file():
        add(findings, "structural", "index/missing", "fail" if strict else "warn", "wiki/index.md")
    if not log_path.is_file():
        add(findings, "structural", "log/missing", "fail" if strict else "warn", "wiki/log.md")
    else:
        log_text = log_path.read_text(encoding="utf-8")
        if log_text.strip() and not LOG_RE.search(log_text):
            add(findings, "structural", "log/no-parseable-entry", "warn", "wiki/log.md")

    ids: dict[str, str] = {}
    page_meta: dict[Path, dict] = {}
    indexed_pages: set[Path] = set()
    pages_with_sources = 0
    pages_with_reviewed_sources = 0
    claim_pages = 0
    temporal_claims = 0
    lineage_relations = 0

    # First pass: parse, bind page identities, validate source provenance and schema-local fields.
    for page in pages:
        rel = page.relative_to(workspace).as_posix()
        text = page_texts[page]
        try:
            meta, _ = parse_frontmatter(text)
        except ValueError as exc:
            add(findings, "structural", "page/frontmatter-invalid", "fail", rel, {"error": str(exc)})
            continue
        if not meta:
            add(findings, "structural", "page/frontmatter-missing", "fail" if strict else "warn", rel)
            continue
        page_meta[page] = meta
        expected_type = PAGE_DIRS[page.relative_to(wiki).parts[0]]
        page_id = meta.get("page_id")
        if not page_id:
            add(findings, "structural", "page/id-missing", "fail", rel)
        elif page_id in ids:
            add(findings, "structural", "page/id-duplicate", "fail", rel, {"other": ids[page_id], "page_id": page_id})
        else:
            ids[page_id] = rel
        if meta.get("page_type") != expected_type:
            add(findings, "structural", "page/type-mismatch", "fail", rel, {"expected": expected_type, "observed": meta.get("page_type")})
        if schema_version and meta.get("wiki_schema_version") != schema_version:
            add(findings, "structural", "page/schema-version-mismatch", "fail", rel, {"expected": schema_version, "observed": meta.get("wiki_schema_version")})
        if expected_type == "claim" and schema_version != "llm-wiki/3":
            add(findings, "structural", "claim/requires-schema-v3", "fail", rel, {"schema_version": schema_version})

        source_ids = meta.get("source_ids", []) or []
        reviewed = set(meta.get("reviewed_source_ids", []) or [])
        if source_ids:
            pages_with_sources += 1
            if set(source_ids).issubset(reviewed):
                pages_with_reviewed_sources += 1
        if expected_type == "source" and len(source_ids) != 1:
            add(findings, "structural", "page/source-cardinality", "fail", rel, {"count": len(source_ids)})
        if expected_type == "claim":
            claim_pages += 1
            if not source_ids:
                add(findings, "structural", "claim/source-missing", "fail" if strict else "warn", rel)
            value_state = meta.get("value_state")
            if value_state not in VALUE_STATES:
                add(findings, "structural", "claim/value-state-invalid", "fail", rel, {"observed": value_state, "allowed": sorted(VALUE_STATES)})
            has_point = bool(meta.get("point_in_time"))
            has_interval = bool(meta.get("valid_from") or meta.get("valid_to"))
            if has_point and has_interval:
                add(findings, "structural", "claim/temporal-shape-invalid", "fail", rel, {"reason": "point_in_time is mutually exclusive with valid_from/valid_to"})
            if has_point or has_interval:
                temporal_claims += 1
        for sid in source_ids:
            if sid not in known_sources:
                add(findings, "structural", "page/unknown-source-id", "fail", rel, {"source_id": sid})
        unresolved = sorted(set(source_ids) - reviewed)
        if unresolved and expected_type != "source":
            add(semantic, "semantic", "semantic/stale-candidate", "needs-review", rel, {"unreviewed_source_ids": unresolved})
        if meta.get("conflict_ids") and meta.get("status") not in {"conflicted", "mixed", "superseded"}:
            add(semantic, "semantic", "semantic/conflict-status-review", "needs-review", rel, {"conflict_ids": meta.get("conflict_ids")})

        for field in LINEAGE_FIELDS:
            refs = meta.get(field, []) or []
            lineage_relations += len(refs)
            for sid in refs:
                if sid not in known_sources:
                    add(findings, "structural", "source-lineage/unknown-source-id", "fail", rel, {"field": field, "source_id": sid})

        rel_wiki = page.relative_to(wiki).as_posix()
        if rel_wiki in index_text or page.stem in index_text:
            indexed_pages.add(page)
        else:
            add(findings, "structural", "index/page-unlisted", "warn", rel)

    # Second pass: references that require the complete page-id set.
    claim_ids = {pid for pid, rel in ids.items() if rel.startswith("wiki/claims/")}
    for page, meta in page_meta.items():
        rel = page.relative_to(workspace).as_posix()
        for subject_id in meta.get("subject_page_ids", []) or []:
            if subject_id not in ids:
                add(findings, "structural", "claim/unknown-subject-page-id", "fail", rel, {"page_id": subject_id})
        for field in CLAIM_REF_FIELDS:
            for claim_id in meta.get(field, []) or []:
                if claim_id not in claim_ids:
                    add(findings, "structural", "claim/unknown-claim-id", "fail", rel, {"field": field, "claim_id": claim_id})

        if meta.get("page_type") == "entity":
            entity_ids = {pid for pid, target_rel in ids.items() if target_rel.startswith("wiki/entities/")}
            current_id = meta.get("page_id")
            merged_into = meta.get("merged_into_page_ids", []) or []
            if len(merged_into) > 1:
                add(findings, "structural", "entity/multiple-merge-targets", "fail", rel, {"page_ids": merged_into})
            for field in ENTITY_REF_FIELDS:
                for target_id in meta.get(field, []) or []:
                    if target_id == current_id:
                        add(findings, "structural", "entity/self-reference", "fail", rel, {"field": field, "page_id": target_id})
                    elif target_id not in entity_ids:
                        add(findings, "structural", "entity/unknown-related-page-id", "fail", rel, {"field": field, "page_id": target_id})

        text = page_texts[page]
        for target in MD_LINK_RE.findall(text):
            if "://" in target or target.startswith("mailto:") or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            resolved = (page.parent / target).resolve(strict=False)
            if not resolved.exists():
                add(findings, "structural", "link/broken-markdown", "fail", rel, {"target": target})
        for target in WIKI_LINK_RE.findall(text):
            result = _resolve_wikilink(wiki, page, target, stems)
            if result is False:
                add(findings, "structural", "link/broken-wikilink", "fail", rel, {"target": target})
            elif result is None:
                add(findings, "structural", "link/ambiguous-wikilink", "warn", rel, {"target": target})

    for page in pages:
        if page in indexed_pages:
            continue
        rel = page.relative_to(workspace).as_posix()
        rel_wiki = page.relative_to(wiki).as_posix()
        inbound = False
        for other, other_text in page_texts.items():
            if other == page:
                continue
            if rel_wiki in other_text or page.stem in other_text:
                inbound = True
                break
        if not inbound:
            add(findings, "structural", "page/orphan-candidate", "warn", rel, {"reason": "no index entry or obvious inbound link"})

    for sid, entry in sorted(manifest.get("sources", {}).items()):
        snapshot = workspace / entry.get("snapshot", "")
        if not snapshot.is_file():
            add(findings, "structural", "snapshot/missing", "fail", sid, {"snapshot": entry.get("snapshot")})
        else:
            observed = sha256_file(snapshot)
            if observed != entry.get("sha256"):
                add(findings, "structural", "snapshot/hash-mismatch", "fail", sid, {"expected": entry.get("sha256"), "observed": observed})
    for rel, pentry in sorted(manifest.get("paths", {}).items()):
        source_path = workspace / rel
        if not source_path.exists():
            add(findings, "structural", "source/path-missing", "warn", rel, {"source_id": pentry.get("source_id")})
        elif source_path.is_file():
            observed = f"sha256:{sha256_file(source_path)}"
            if observed != pentry.get("source_id"):
                add(findings, "structural", "source/path-modified", "fail", rel, {"expected": pentry.get("source_id"), "observed": observed})

    hard = sum(1 for f in findings if f["status"] == "fail")
    warns = sum(1 for f in findings if f["status"] == "warn")
    broken_links = sum(1 for f in findings if f["code"] in {"link/broken-markdown", "link/broken-wikilink"})
    orphan_candidates = sum(1 for f in findings if f["code"] == "page/orphan-candidate")
    stale_candidates = sum(1 for f in semantic if f["code"] == "semantic/stale-candidate")
    conflict_pages = sum(1 for meta in page_meta.values() if meta.get("conflict_ids"))
    metrics = {
        "pages_checked": len(pages),
        "hard_errors": hard,
        "warnings": warns,
        "semantic_review_candidates": len(semantic),
        "provenance_coverage": _ratio(pages_with_sources, len(pages)),
        "reviewed_source_coverage": _ratio(pages_with_reviewed_sources, pages_with_sources),
        "claim_pages": claim_pages,
        "temporal_qualified_claims": temporal_claims,
        "lineage_relations": lineage_relations,
        "index_coverage": _ratio(len(indexed_pages), len(pages)),
        "stale_candidates": stale_candidates,
        "broken_links": broken_links,
        "orphan_candidates": orphan_candidates,
        "pages_with_conflicts": conflict_pages,
    }
    report = {
        "receipt_version": 2,
        "stage": "lint-validation",
        "status": "fail" if hard else ("warn" if warns or semantic else "pass"),
        "schema_version": schema_version,
        "structural_evidence": findings,
        "semantic_editorial_judgment": semantic,
        "metrics": metrics,
        "limitations": [
            "Structural checks do not decide factual truth, entity equivalence, source authority, source independence, or whether a conflict is semantically resolved.",
            "Coverage and health metrics are structural indicators/candidate counts, not factual truth or confidence scores.",
            "Stale-claim and dependency findings identify review candidates; semantic relevance still requires source review.",
            "Orphan detection is a structural candidate based on explicit index/link evidence; it never authorizes automatic page deletion.",
        ],
    }
    return (1 if hard else 0), report


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate wiki structural integrity and emit localizable structural/semantic diagnostics separately.")
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--json")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    code, report = validate(Path(args.workspace), args.strict)
    if args.json:
        out = Path(args.json).resolve(strict=False)
        root = Path(args.workspace).resolve(strict=True)
        raw_root = (root / "raw").resolve(strict=False)
        wiki_root = (root / "wiki").resolve(strict=False)
        schema_path = (root / "WIKI_SCHEMA.md").resolve(strict=False)
        if out == schema_path or out == raw_root or raw_root in out.parents or out == wiki_root or wiki_root in out.parents:
            raise SystemExit("lint receipt output aliases source or maintained wiki content")
        atomic_write_json(out, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
