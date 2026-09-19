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
PAGE_DIRS = {"sources": "source", "entities": "entity", "concepts": "concept", "syntheses": "synthesis"}


def add(findings, layer, code, status, subject, evidence=None):
    findings.append({"layer": layer, "code": code, "status": status, "subject": subject, "evidence": evidence or {}})


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


def validate(workspace: Path, strict: bool) -> tuple[int, dict]:
    workspace = workspace.resolve(strict=True)
    wiki = workspace / "wiki"
    findings = []
    semantic = []
    schema_path = workspace / "WIKI_SCHEMA.md"
    schema_version = None
    if not schema_path.is_file():
        add(findings, "structural", "schema/missing", "fail" if strict else "warn", "WIKI_SCHEMA.md")
    else:
        m = SCHEMA_RE.search(schema_path.read_text(encoding="utf-8"))
        if m:
            schema_version = m.group(1)
            add(findings, "structural", "schema/version", "pass", "WIKI_SCHEMA.md", {"schema_version": schema_version})
        else:
            add(findings, "structural", "schema/version-missing", "fail" if strict else "warn", "WIKI_SCHEMA.md")

    manifest_path = workspace / ".llm-wiki" / "source-manifest.json"
    manifest = load_json(manifest_path, {"sources": {}, "paths": {}})

    pages = []
    page_texts: dict[Path, str] = {}
    stems: dict[str, list[Path]] = {}
    if wiki.exists():
        for p in sorted(wiki.rglob("*.md")):
            stems.setdefault(p.stem.casefold(), []).append(p)
            if p.name in {"index.md", "log.md"}:
                continue
            try:
                rel_dir = p.relative_to(wiki).parts[0]
            except Exception:
                continue
            if rel_dir in PAGE_DIRS:
                pages.append(p)
                page_texts[p] = p.read_text(encoding="utf-8")

    if strict and not manifest_path.exists() and any(p.relative_to(wiki).parts[0] == "sources" for p in pages):
        add(findings, "structural", "provenance/source-manifest-missing", "fail", manifest_path.relative_to(workspace).as_posix())

    ids: dict[str, str] = {}
    index_text = (wiki / "index.md").read_text(encoding="utf-8") if (wiki / "index.md").is_file() else ""
    if not (wiki / "index.md").is_file():
        add(findings, "structural", "index/missing", "fail" if strict else "warn", "wiki/index.md")
    if not (wiki / "log.md").is_file():
        add(findings, "structural", "log/missing", "fail" if strict else "warn", "wiki/log.md")
    else:
        log_text = (wiki / "log.md").read_text(encoding="utf-8")
        if log_text.strip() and not LOG_RE.search(log_text):
            add(findings, "structural", "log/no-parseable-entry", "warn", "wiki/log.md")

    for page in pages:
        rel = page.relative_to(workspace).as_posix()
        text = page_texts.get(page, page.read_text(encoding="utf-8"))
        try:
            meta, _ = parse_frontmatter(text)
        except ValueError as exc:
            add(findings, "structural", "page/frontmatter-invalid", "fail", rel, {"error": str(exc)})
            continue
        if not meta:
            add(findings, "structural", "page/frontmatter-missing", "fail" if strict else "warn", rel)
            continue
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
        source_ids = meta.get("source_ids", [])
        if expected_type == "source" and len(source_ids) != 1:
            add(findings, "structural", "page/source-cardinality", "fail", rel, {"count": len(source_ids)})
        for sid in source_ids:
            if sid not in manifest.get("sources", {}):
                add(findings, "structural", "page/unknown-source-id", "fail", rel, {"source_id": sid})
        reviewed = set(meta.get("reviewed_source_ids", []))
        unresolved = sorted(set(source_ids) - reviewed)
        if unresolved and expected_type != "source":
            add(semantic, "semantic", "semantic/stale-candidate", "needs-review", rel, {"unreviewed_source_ids": unresolved})
        if meta.get("conflict_ids") and meta.get("status") not in {"conflicted", "mixed", "superseded"}:
            add(semantic, "semantic", "semantic/conflict-status-review", "needs-review", rel, {"conflict_ids": meta.get("conflict_ids")})
        rel_wiki = page.relative_to(wiki).as_posix()
        if rel_wiki not in index_text and page.stem not in index_text:
            add(findings, "structural", "index/page-unlisted", "warn", rel)

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
        rel = page.relative_to(workspace).as_posix()
        rel_wiki = page.relative_to(wiki).as_posix()
        indexed = rel_wiki in index_text or page.stem in index_text
        if indexed:
            continue
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
        p = workspace / rel
        if not p.exists():
            add(findings, "structural", "source/path-missing", "warn", rel, {"source_id": pentry.get("source_id")})
        elif p.is_file():
            observed = f"sha256:{sha256_file(p)}"
            if observed != pentry.get("source_id"):
                add(findings, "structural", "source/path-modified", "fail", rel, {"expected": pentry.get("source_id"), "observed": observed})

    hard = sum(1 for f in findings if f["status"] == "fail")
    warns = sum(1 for f in findings if f["status"] == "warn")
    report = {
        "receipt_version": 1,
        "stage": "lint-validation",
        "status": "fail" if hard else ("warn" if warns or semantic else "pass"),
        "schema_version": schema_version,
        "structural_evidence": findings,
        "semantic_editorial_judgment": semantic,
        "metrics": {"pages_checked": len(pages), "hard_errors": hard, "warnings": warns, "semantic_review_candidates": len(semantic)},
        "limitations": [
            "Structural checks do not decide factual truth, entity equivalence, source authority, or whether a conflict is semantically resolved.",
            "Stale-claim findings are candidates derived from declared provenance sets; semantic relevance still requires source review.",
            "Orphan detection is a structural candidate based on explicit index/link evidence; it never authorizes automatic page deletion.",
        ],
    }
    return (1 if hard else 0), report


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate wiki structural integrity and emit semantic-review candidates separately.")
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--json")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    code, report = validate(Path(args.workspace), args.strict)
    if args.json:
        out = Path(args.json).resolve(strict=False)
        raw_root = (Path(args.workspace).resolve(strict=True) / "raw").resolve(strict=False)
        wiki_root = (Path(args.workspace).resolve(strict=True) / "wiki").resolve(strict=False)
        schema_path = (Path(args.workspace).resolve(strict=True) / "WIKI_SCHEMA.md").resolve(strict=False)
        if out == schema_path or out == raw_root or raw_root in out.parents or out == wiki_root or wiki_root in out.parents:
            raise SystemExit("lint receipt output aliases source or maintained wiki content")
        atomic_write_json(out, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
