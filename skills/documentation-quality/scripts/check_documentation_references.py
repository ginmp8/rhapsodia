#!/usr/bin/env python3
"""Check local Markdown references with stable machine-readable diagnostics.

This helper verifies local Markdown links and, optionally, file-like paths inside
inline code spans. It does not validate external URLs, anchors, command behavior,
or semantic accuracy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

RECEIPT_VERSION = 1
STAGE = "documentation-reference-check"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_SPAN_PATTERN = re.compile(r"`([^`]+)`")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)(.*)$")
FILE_LIKE_PATTERN = re.compile(
    r"(?:^|\s)((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:md|py|sh|json|ya?ml|txt|template))"
)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


@dataclass(frozen=True)
class MissingReference:
    source_file: str
    reference: str
    resolved_path: str
    kind: str


@dataclass(frozen=True)
class SkippedReference:
    source_file: str
    reference: str
    reason: str


def iter_markdown_files(paths: list[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
            yield path
        elif path.is_dir():
            for item in path.rglob("*.md"):
                if item.is_file():
                    yield item


def normalize_reference(reference: str) -> str:
    ref = reference.strip().split("#", 1)[0]
    return ref.strip("'\" ")


def is_external(reference: str) -> bool:
    stripped = reference.strip()
    return stripped.startswith(EXTERNAL_PREFIXES) or not stripped


def resolve_reference(source_file: Path, reference: str, root: Path | None) -> Path:
    ref = normalize_reference(reference)
    if root and ref.startswith("/"):
        return (root / ref.lstrip("/")).resolve()
    return (source_file.parent / ref).resolve()


def iter_non_fenced_lines(text: str) -> Iterable[str]:
    in_fence = False
    fence_marker = ""
    fence_length = 0
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker, info = match.groups()
            marker_char = marker[0]
            marker_length = len(marker)
            if not in_fence:
                in_fence = True
                fence_marker = marker_char
                fence_length = marker_length
            elif marker_char == fence_marker and marker_length >= fence_length and not info.strip():
                in_fence = False
                fence_marker = ""
                fence_length = 0
            continue
        if not in_fence:
            yield line


def check_links(md_file: Path, root: Path | None) -> tuple[list[MissingReference], list[SkippedReference]]:
    missing: list[MissingReference] = []
    skipped: list[SkippedReference] = []
    text = md_file.read_text(encoding="utf-8")
    for line in iter_non_fenced_lines(text):
        for match in LINK_PATTERN.finditer(line):
            raw = match.group(1).strip()
            if is_external(raw):
                skipped.append(SkippedReference(str(md_file), raw, "external_or_anchor"))
                continue
            if "*" in raw:
                skipped.append(SkippedReference(str(md_file), raw, "glob_pattern"))
                continue
            resolved = resolve_reference(md_file, raw, root)
            if not resolved.exists():
                missing.append(MissingReference(str(md_file), raw, str(resolved), "markdown_link"))
    return missing, skipped


def check_code_spans(md_file: Path, root: Path | None) -> tuple[list[MissingReference], list[SkippedReference]]:
    missing: list[MissingReference] = []
    skipped: list[SkippedReference] = []
    text = md_file.read_text(encoding="utf-8")
    for span in CODE_SPAN_PATTERN.findall(text):
        for match in FILE_LIKE_PATTERN.finditer(span):
            raw = match.group(1).strip()
            if "*" in raw or raw.startswith("path/to/") or raw.startswith("target-package/"):
                skipped.append(SkippedReference(str(md_file), raw, "illustrative_or_pattern"))
                continue
            resolved = resolve_reference(md_file, raw, root)
            if not resolved.exists() and root is not None:
                root_candidate = (root / normalize_reference(raw)).resolve()
                if root_candidate.exists():
                    resolved = root_candidate
            if not resolved.exists():
                missing.append(MissingReference(str(md_file), raw, str(resolved), "code_span_path"))
    return missing, skipped


def _diagnostic_for_missing(item: MissingReference) -> dict[str, object]:
    code = (
        "docs/ref/missing-markdown-link"
        if item.kind == "markdown_link"
        else "docs/ref/missing-code-span-path"
    )
    return {
        "code": code,
        "status": "fail",
        "severity": "error",
        "subject": item.source_file,
        "evidence": {
            "reference": item.reference,
            "resolved_path": item.resolved_path,
            "kind": item.kind,
        },
        "supported_fixes": [
            "correct the reference",
            "add the missing local artifact if it is required",
            "mark the path as illustrative when it is intentionally not local",
        ],
    }


def _diagnostic_for_skipped(item: SkippedReference) -> dict[str, object]:
    return {
        "code": f"docs/ref/skipped-{item.reason.replace('_', '-')}",
        "status": "skip",
        "severity": "info",
        "subject": item.source_file,
        "evidence": {"reference": item.reference, "reason": item.reason},
        "supported_fixes": [],
    }


def build_receipt(
    files: list[Path],
    missing: list[MissingReference],
    skipped: list[SkippedReference],
) -> dict[str, object]:
    missing = sorted(missing, key=lambda x: (x.source_file, x.kind, x.reference, x.resolved_path))
    skipped = sorted(skipped, key=lambda x: (x.source_file, x.reason, x.reference))
    checks = [_diagnostic_for_missing(item) for item in missing]
    checks.extend(_diagnostic_for_skipped(item) for item in skipped)
    errors = len(missing)
    return {
        "receipt_version": RECEIPT_VERSION,
        "status": "fail" if errors else "pass",
        "stage": STAGE,
        "checks": checks,
        "errors": errors,
        "warnings": 0,
        "metrics": {
            "files_checked": len(files),
            "missing_references": len(missing),
            "skipped_references": len(skipped),
        },
        # Backward-compatible fields retained for existing consumers.
        "files_checked": [str(p) for p in files],
        "missing_count": len(missing),
        "missing": [asdict(item) for item in missing],
        "skipped": [asdict(item) for item in skipped],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local documentation references in Markdown files.")
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to inspect")
    parser.add_argument("--root", help="Optional project or skill root used for root-relative references")
    parser.add_argument(
        "--check-code-spans",
        action="store_true",
        help="Also check file-like paths inside inline code spans",
    )
    parser.add_argument("--json-output", help="Optional path to write JSON results")
    args = parser.parse_args()

    input_paths = [Path(p).resolve() for p in args.paths]
    root = Path(args.root).resolve() if args.root else None
    files = sorted(set(iter_markdown_files(input_paths)))

    missing: list[MissingReference] = []
    skipped: list[SkippedReference] = []
    for md_file in files:
        link_missing, link_skipped = check_links(md_file, root)
        missing.extend(link_missing)
        skipped.extend(link_skipped)
        if args.check_code_spans:
            code_missing, code_skipped = check_code_spans(md_file, root)
            missing.extend(code_missing)
            skipped.extend(code_skipped)

    result = build_receipt(files, missing, skipped)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
