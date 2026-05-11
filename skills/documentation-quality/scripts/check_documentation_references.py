#!/usr/bin/env python3
"""Check Markdown local links and optional code-span file references.

This helper is intentionally narrow: it verifies whether documentation points to
files that exist. It does not validate external URLs, anchors, command behavior,
or semantic accuracy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_SPAN_PATTERN = re.compile(r"`([^`]+)`")
FILE_LIKE_PATTERN = re.compile(
    r"(?:^|\s)((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:md|py|sh|json|ya?ml|txt|template))"
)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


@dataclass
class MissingReference:
    source_file: str
    reference: str
    resolved_path: str
    kind: str


@dataclass
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
    ref = ref.strip("'\" ")
    return ref


def is_external(reference: str) -> bool:
    stripped = reference.strip()
    return stripped.startswith(EXTERNAL_PREFIXES) or not stripped


def resolve_reference(source_file: Path, reference: str, root: Path | None) -> Path:
    ref = normalize_reference(reference)
    if root and ref.startswith(("/", "./")):
        return (root / ref.lstrip("/./")).resolve()
    return (source_file.parent / ref).resolve()


def check_links(md_file: Path, root: Path | None) -> tuple[list[MissingReference], list[SkippedReference]]:
    missing: list[MissingReference] = []
    skipped: list[SkippedReference] = []
    text = md_file.read_text(encoding="utf-8")
    for match in LINK_PATTERN.finditer(text):
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
            if not resolved.exists():
                missing.append(MissingReference(str(md_file), raw, str(resolved), "code_span_path"))
    return missing, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local documentation references in Markdown files.")
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to inspect")
    parser.add_argument("--root", help="Optional project or skill root used for root-relative references")
    parser.add_argument("--check-code-spans", action="store_true", help="Also check file-like paths inside inline code spans")
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

    result = {
        "files_checked": [str(p) for p in files],
        "missing_count": len(missing),
        "missing": [asdict(item) for item in missing],
        "skipped": [asdict(item) for item in skipped],
    }

    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        Path(args.json_output).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
