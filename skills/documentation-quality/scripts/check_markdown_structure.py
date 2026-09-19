#!/usr/bin/env python3
"""Check objective Markdown structure properties with stable diagnostics.

The checker intentionally covers only mechanical properties. It does not score
information architecture, prose clarity, semantic accuracy, or visual quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

RECEIPT_VERSION = 1
STAGE = "markdown-structure-check"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK_TEXT_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
AMBIGUOUS_LINK_TEXT = {"here", "this", "click here", "read more"}
FENCE_RE = re.compile(r"^\s*(```+|~~~+)(.*)$")


def iter_markdown_files(paths: list[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
            yield path
        elif path.is_dir():
            for item in path.rglob("*.md"):
                if item.is_file():
                    yield item


def diagnostic(
    code: str,
    severity: str,
    subject: str,
    evidence: dict[str, object],
    supported_fixes: list[str],
) -> dict[str, object]:
    return {
        "code": code,
        "status": "fail" if severity == "error" else "warn",
        "severity": severity,
        "subject": subject,
        "evidence": evidence,
        "supported_fixes": supported_fixes,
    }


def analyze_file(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[dict[str, object]] = []
    headings: list[tuple[int, int, str]] = []
    in_fence = False
    fence_marker = ""
    fence_length = 0
    fence_start = 0

    for line_no, line in enumerate(lines, start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker, info = fence_match.groups()
            marker_char = marker[0]
            marker_length = len(marker)
            if not in_fence:
                in_fence = True
                fence_marker = marker_char
                fence_length = marker_length
                fence_start = line_no
                if not info.strip():
                    findings.append(
                        diagnostic(
                            "docs/fence/language-missing",
                            "warning",
                            str(path),
                            {"line": line_no},
                            ["add a language tag when the fenced content language is known"],
                        )
                    )
            elif marker_char == fence_marker and marker_length >= fence_length and not info.strip():
                in_fence = False
                fence_marker = ""
                fence_length = 0
                fence_start = 0
            continue

        if in_fence:
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            headings.append((line_no, level, heading_match.group(2).strip()))

        for link_match in LINK_TEXT_RE.finditer(line):
            label = " ".join(link_match.group(1).strip().lower().split())
            if label in AMBIGUOUS_LINK_TEXT:
                findings.append(
                    diagnostic(
                        "docs/link/ambiguous-text",
                        "warning",
                        str(path),
                        {"line": line_no, "label": link_match.group(1), "target": link_match.group(2)},
                        ["replace ambiguous link text with a descriptive label"],
                    )
                )

    if in_fence:
        findings.append(
            diagnostic(
                "docs/fence/unclosed",
                "error",
                str(path),
                {"line": fence_start, "marker": fence_marker},
                ["close the fenced code block with the same marker type"],
            )
        )

    h1_lines = [line_no for line_no, level, _ in headings if level == 1]
    if len(h1_lines) != 1:
        findings.append(
            diagnostic(
                "docs/heading/h1-count",
                "warning",
                str(path),
                {"count": len(h1_lines), "lines": h1_lines},
                ["use one level-1 heading per standalone Markdown document"],
            )
        )

    previous_level: int | None = None
    previous_line: int | None = None
    for line_no, level, title in headings:
        if previous_level is not None and level > previous_level + 1:
            findings.append(
                diagnostic(
                    "docs/heading/level-skip",
                    "warning",
                    str(path),
                    {
                        "line": line_no,
                        "level": level,
                        "title": title,
                        "previous_line": previous_line,
                        "previous_level": previous_level,
                    },
                    ["use sequential heading levels without skipping levels"],
                )
            )
        previous_level = level
        previous_line = line_no

    return findings


def build_receipt(files: list[Path], checks: list[dict[str, object]]) -> dict[str, object]:
    checks = sorted(
        checks,
        key=lambda item: (
            str(item["subject"]),
            str(item["code"]),
            int(item.get("evidence", {}).get("line", 0)),
        ),
    )
    errors = sum(1 for item in checks if item["severity"] == "error")
    warnings = sum(1 for item in checks if item["severity"] == "warning")
    return {
        "receipt_version": RECEIPT_VERSION,
        "status": "fail" if errors else "pass",
        "stage": STAGE,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "files_checked": len(files),
            "errors": errors,
            "warnings": warnings,
        },
        "files_checked": [str(path) for path in files],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check objective Markdown structure properties.")
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to inspect")
    parser.add_argument("--json-output", help="Optional path to write JSON results")
    args = parser.parse_args()

    files = sorted(set(iter_markdown_files([Path(p).resolve() for p in args.paths])))
    checks: list[dict[str, object]] = []
    for path in files:
        checks.extend(analyze_file(path))

    result = build_receipt(files, checks)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
