#!/usr/bin/env python3
"""Audit and compare token-efficiency changes for skill packages.

The estimator is approximate. It is intended for deterministic regression triage,
not model-token accounting.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml", ".template", ".skill"}
TEXT_NAMES = {"SKILL.md", "skill.md", "openai.yaml", "AGENTS.md", "CLAUDE.md"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
BINARY_SUFFIXES = {".zip", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".pptx", ".xlsx"}
WORD_RE = re.compile(r"\w+", re.U)
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]", re.U)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PROTECTED_RE = re.compile(
    r"```[\s\S]*?```|`[^`\n]+`|https?://[^\s)>\]]+|(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*|\$[A-Z_][A-Z0-9_]*|\b[\w.-]+/[\w./-]+"
)
TRACE_PATTERNS = [
    r"\bcitations?\b",
    r"\breferences?\b",
    r"\bsources?\b",
    r"\bline ranges?\b",
    r"\bfile paths?\b",
    r"\breport paths?\b",
    r"\bevidence\s*/\s*citation\b",
    r"\bevidence\s+(?:and|or)\s+citations?\b",
]
TRACE_RE = [re.compile(pattern, re.I) for pattern in TRACE_PATTERNS]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def is_text_file(path: Path) -> bool:
    return path.name in TEXT_NAMES or (
        path.suffix.lower() not in BINARY_SUFFIXES
        and (path.suffix.lower() in TEXT_SUFFIXES or ".template" in path.name)
    )


def iter_files(root: Path):
    root = root.resolve()
    if root.is_file():
        if is_text_file(root):
            yield root
        return
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        for name in sorted(names):
            path = Path(dirpath) / name
            if is_text_file(path):
                yield path


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception:
            return ""
    return ""


def estimate_tokens(text: str) -> int:
    tokens = TOKEN_RE.findall(text)
    words = sum(bool(re.fullmatch(r"[A-Za-z0-9_]+", token)) for token in tokens)
    non_ascii = sum(ord(char) > 127 for char in text)
    return max(1, round(words * 0.95 + (len(tokens) - words) * 0.75 + non_ascii * 0.3))


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)) if root.is_dir() else path.name


def missing_links(path: Path, text: str) -> list[str]:
    missing: list[str] = []
    for target in LINK_RE.findall(text):
        candidate = target.split("#", 1)[0].strip()
        if not candidate or "://" in candidate or target.startswith(("#", "mailto:")):
            continue
        if not (path.parent / candidate).exists():
            missing.append(target)
    return missing


def protected_regions(text: str) -> list[str]:
    return sorted(set(PROTECTED_RE.findall(text)))


def trace_hits(text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for pattern, regex in zip(TRACE_PATTERNS, TRACE_RE):
        count = len(regex.findall(text))
        if count:
            hits[pattern] = count
    return hits


def markdown_sections(text: str) -> dict[str, str]:
    """Return stable heading-path -> section text for Markdown-like files."""
    sections: dict[str, list[str]] = {"__preamble__": []}
    stack: list[tuple[int, str]] = []
    current = "__preamble__"
    for line in text.splitlines(keepends=True):
        match = HEADING_RE.match(line.rstrip("\n"))
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            stack = [(lvl, name) for lvl, name in stack if lvl < level]
            stack.append((level, title))
            current = " > ".join(name for _, name in stack)
            sections.setdefault(current, [])
        sections.setdefault(current, []).append(line)
    return {key: "".join(lines) for key, lines in sections.items() if "".join(lines).strip()}


def file_stat(root: Path, path: Path) -> dict[str, Any]:
    text = read_text(path)
    lines = text.splitlines()
    paragraphs = re.split(r"\n\s*\n", text)
    trace = trace_hits(text)
    return {
        "path": rel(root, path),
        "chars": len(text),
        "words": len(WORD_RE.findall(text)),
        "lines": len(lines),
        "estimated_tokens": estimate_tokens(text),
        "tables": sum(line.strip().startswith("|") and "|" in line.strip()[1:] for line in lines),
        "long_paragraphs": sum(len(WORD_RE.findall(paragraph)) >= 80 for paragraph in paragraphs),
        "scaffold_markers": len(re.findall(r"\b" + "TO" + "DO" + r"\b|\[" + "TO" + "DO", text, re.I)),
        "broken_links": missing_links(path, text),
        "protected_count": len(protected_regions(text)),
        "traceability_terms": sum(trace.values()),
        "traceability_detail": trace,
    }


def audit(target: str | Path) -> dict[str, Any]:
    root = Path(target).resolve()
    stats = [file_stat(root, path) for path in iter_files(root)]

    def total(key: str) -> int:
        return sum(item[key] for item in stats)

    totals = {
        "files": len(stats),
        "chars": total("chars"),
        "words": total("words"),
        "lines": total("lines"),
        "estimated_tokens": total("estimated_tokens"),
        "tables": total("tables"),
        "long_paragraphs": total("long_paragraphs"),
        "scaffold_markers": total("scaffold_markers"),
        "broken_links": sum(len(item["broken_links"]) for item in stats),
        "traceability_terms": total("traceability_terms"),
    }
    warnings: list[str] = []
    for key, message in [
        ("scaffold_markers", "scaffold markers found"),
        ("broken_links", "broken markdown links found"),
        ("long_paragraphs", "long paragraphs found"),
    ]:
        if totals[key]:
            warnings.append(f"{message}: {totals[key]}")
    if totals["tables"] > 20:
        warnings.append("many markdown table rows; lists may be cheaper")
    top_files = [
        {key: item[key] for key in ("path", "estimated_tokens", "chars", "lines")}
        for item in sorted(stats, key=lambda item: item["estimated_tokens"], reverse=True)[:10]
    ]
    return {"target": str(root), "files": stats, "totals": totals, "top_files": top_files, "warnings": warnings}


def text_map(target: str | Path) -> dict[str, str]:
    root = Path(target).resolve()
    return {rel(root, path): read_text(path) for path in iter_files(root)}


def trace_diff(before: dict[str, str], after: dict[str, str]) -> list[dict[str, Any]]:
    losses: list[dict[str, Any]] = []
    for name in sorted(set(before) & set(after)):
        before_hits = trace_hits(before[name])
        after_hits = trace_hits(after[name])
        lost = {key: count - after_hits.get(key, 0) for key, count in before_hits.items() if after_hits.get(key, 0) < count}
        if lost:
            losses.append({"path": name, "lost_traceability_terms": lost})
    return losses


def file_token_deltas(before: dict[str, str], after: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in sorted(set(before) & set(after)):
        b = estimate_tokens(before[name])
        a = estimate_tokens(after[name])
        delta = a - b
        rows.append(
            {
                "path": name,
                "before_estimated_tokens": b,
                "after_estimated_tokens": a,
                "token_delta": delta,
                "reduction_pct": round(((b - a) / b * 100) if b else 0, 2),
                "status": "increased" if delta > 0 else "decreased" if delta < 0 else "unchanged",
            }
        )
    return rows


def section_token_deltas(before: dict[str, str], after: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in sorted(set(before) & set(after)):
        if not (name.lower().endswith(".md") or name.lower().endswith(".md.template")):
            continue
        before_sections = markdown_sections(before[name])
        after_sections = markdown_sections(after[name])
        for section in sorted(set(before_sections) & set(after_sections)):
            b = estimate_tokens(before_sections[section])
            a = estimate_tokens(after_sections[section])
            delta = a - b
            if delta:
                rows.append(
                    {
                        "path": name,
                        "section": section,
                        "before_estimated_tokens": b,
                        "after_estimated_tokens": a,
                        "token_delta": delta,
                        "status": "increased" if delta > 0 else "decreased",
                    }
                )
    return rows


def compare(before_target: str | Path, after_target: str | Path) -> dict[str, Any]:
    before_audit = audit(before_target)
    after_audit = audit(after_target)
    before_text = text_map(before_target)
    after_text = text_map(after_target)

    protected_diffs: list[dict[str, Any]] = []
    for name in sorted(set(before_text) & set(after_text)):
        before_regions = set(protected_regions(before_text[name]))
        after_regions = set(protected_regions(after_text[name]))
        missing = sorted(before_regions - after_regions)[:20]
        added = sorted(after_regions - before_regions)[:20]
        if missing or added:
            protected_diffs.append({"path": name, "missing_after": missing, "added_after": added})

    trace_losses = trace_diff(before_text, after_text)
    file_deltas = file_token_deltas(before_text, after_text)
    section_deltas = section_token_deltas(before_text, after_text)
    increased_files = [item for item in file_deltas if item["token_delta"] > 0]
    increased_sections = [item for item in section_deltas if item["token_delta"] > 0]
    before_tokens = before_audit["totals"]["estimated_tokens"]
    after_tokens = after_audit["totals"]["estimated_tokens"]
    return {
        "comparison": {
            "before_estimated_tokens": before_tokens,
            "after_estimated_tokens": after_tokens,
            "token_delta": after_tokens - before_tokens,
            "reduction_pct": round(((before_tokens - after_tokens) / before_tokens * 100) if before_tokens else 0, 2),
            "improved": after_tokens < before_tokens,
        },
        "local_token_comparison": {
            "common_files_checked": len(set(before_text) & set(after_text)),
            "increased_files": len(increased_files),
            "increased_sections": len(increased_sections),
            "file_token_deltas": file_deltas,
            "section_token_deltas": section_deltas,
            "local_regressions": {
                "files": increased_files,
                "sections": increased_sections,
            },
        },
        "protected_region_comparison": {
            "common_files_checked": len(set(before_text) & set(after_text)),
            "files_missing_after": sorted(set(before_text) - set(after_text)),
            "files_added_after": sorted(set(after_text) - set(before_text)),
            "files_with_protected_diffs": len(protected_diffs),
            "diffs": protected_diffs[:20],
        },
        "traceability_comparison": {
            "before_terms": before_audit["totals"]["traceability_terms"],
            "after_terms": after_audit["totals"]["traceability_terms"],
            "term_delta": after_audit["totals"]["traceability_terms"] - before_audit["totals"]["traceability_terms"],
            "files_with_traceability_loss": len(trace_losses),
            "losses": trace_losses[:20],
        },
        "targets": [before_audit, after_audit],
    }


def to_markdown(report: dict[str, Any]) -> str:
    lines = ["# Token Refactor Audit", ""]
    comparison = report.get("comparison")
    if comparison:
        lines += [
            "## Comparison",
            f"- Before estimated tokens: {comparison['before_estimated_tokens']}",
            f"- After estimated tokens: {comparison['after_estimated_tokens']}",
            f"- Delta: {comparison['token_delta']}",
            f"- Reduction: {comparison['reduction_pct']}%",
            f"- Improved: {comparison['improved']}",
            "",
        ]
    local = report.get("local_token_comparison")
    if local:
        lines += [
            "## Local Token Comparison",
            f"- Common files checked: {local['common_files_checked']}",
            f"- Increased files: {local['increased_files']}",
            f"- Increased sections: {local['increased_sections']}",
            "",
        ]
        files = local["local_regressions"]["files"][:10]
        sections = local["local_regressions"]["sections"][:10]
        if files:
            lines += ["### File regressions"] + [
                f"- `{item['path']}`: {item['before_estimated_tokens']} -> {item['after_estimated_tokens']} ({item['token_delta']:+})"
                for item in files
            ] + [""]
        if sections:
            lines += ["### Section regressions"] + [
                f"- `{item['path']}` / {item['section']}: {item['before_estimated_tokens']} -> {item['after_estimated_tokens']} ({item['token_delta']:+})"
                for item in sections
            ] + [""]
    protected = report.get("protected_region_comparison")
    if protected:
        lines += [
            "## Protected Regions",
            f"- Common files checked: {protected['common_files_checked']}",
            f"- Files with protected diffs: {protected['files_with_protected_diffs']}",
            f"- Files missing after: {len(protected['files_missing_after'])}",
            f"- Files added after: {len(protected['files_added_after'])}",
            "",
        ]
    trace = report.get("traceability_comparison")
    if trace:
        lines += [
            "## Traceability Terms",
            f"- Before terms: {trace['before_terms']}",
            f"- After terms: {trace['after_terms']}",
            f"- Delta: {trace['term_delta']}",
            f"- Files with traceability loss: {trace['files_with_traceability_loss']}",
            "",
        ]
    for target in report["targets"]:
        totals = target["totals"]
        keys = [
            "files",
            "estimated_tokens",
            "chars",
            "words",
            "lines",
            "tables",
            "long_paragraphs",
            "scaffold_markers",
            "broken_links",
            "traceability_terms",
        ]
        lines += [f"## {target['target']}"]
        lines += [f"- {key.replace('_', ' ').title()}: {totals[key]}" for key in keys]
        lines += ["", "### Largest files"]
        lines += [f"- `{item['path']}`: {item['estimated_tokens']} est. tokens" for item in target["top_files"]]
        if target["warnings"]:
            lines += ["", "### Warnings"] + [f"- {warning}" for warning in target["warnings"]]
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit or compare token-efficiency for skill packages.")
    parser.add_argument("--target")
    parser.add_argument("--before")
    parser.add_argument("--after")
    parser.add_argument("--output")
    parser.add_argument("--markdown")
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="With --before/--after, return non-zero when any common file or matching Markdown section has token growth.",
    )
    args = parser.parse_args()
    if args.target and (args.before or args.after):
        parser.error("use --target or --before/--after, not both")
    if not args.target and not (args.before and args.after):
        parser.error("provide --target or both --before and --after")

    report = {"targets": [audit(args.target)]} if args.target else compare(args.before, args.after)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(to_markdown(report), encoding="utf-8")

    if args.fail_on_regression and "local_token_comparison" in report:
        local = report["local_token_comparison"]
        if local["increased_files"] or local["increased_sections"]:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
