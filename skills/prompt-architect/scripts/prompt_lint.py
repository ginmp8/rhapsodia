#!/usr/bin/env python3
"""Deterministic lint checks for prompt files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SCAFFOLD_PATTERNS = [
    re.compile(r"\b" + "TO" + r"DO\b", re.IGNORECASE),
    re.compile(r"\b" + "FIX" + r"ME\b", re.IGNORECASE),
    re.compile(r"\b" + "TB" + r"D\b", re.IGNORECASE),
    re.compile(r"\[\s*(replace|insert|fill|" + "to" + r"do|" + "tb" + r"d)[^\]]*\]", re.IGNORECASE),
    re.compile(r"lorem ipsum", re.IGNORECASE),
]

OUTPUT_FORMAT_PATTERNS = [
    re.compile(r"^#*\s*output format\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\breturn\b.+\b(json|markdown|table|list|schema|format)\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"\brespond\b.+\b(json|markdown|table|list|schema|format)\b", re.IGNORECASE | re.DOTALL),
]

SUCCESS_PATTERNS = [
    re.compile(r"\bsuccess criteria\b", re.IGNORECASE),
    re.compile(r"\bverdict\b", re.IGNORECASE),
    re.compile(r"\bpass/fail\b", re.IGNORECASE),
    re.compile(r"\bvalidation\b", re.IGNORECASE),
]

BIDI_NAMES = {
    "LEFT-TO-RIGHT EMBEDDING",
    "RIGHT-TO-LEFT EMBEDDING",
    "POP DIRECTIONAL FORMATTING",
    "LEFT-TO-RIGHT OVERRIDE",
    "RIGHT-TO-LEFT OVERRIDE",
    "LEFT-TO-RIGHT ISOLATE",
    "RIGHT-TO-LEFT ISOLATE",
    "FIRST STRONG ISOLATE",
    "POP DIRECTIONAL ISOLATE",
}


def hidden_char_findings(text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for idx, ch in enumerate(text):
        category = unicodedata.category(ch)
        name = unicodedata.name(ch, "")
        if category == "Cf" or name in BIDI_NAMES:
            line = text.count("\n", 0, idx) + 1
            col = idx - text.rfind("\n", 0, idx)
            findings.append({"line": line, "column": col, "name": name or category})
    return findings


def lint_file(path: Path, require_output_format: bool, require_success_criteria: bool) -> dict[str, object]:
    result: dict[str, object] = {
        "path": str(path),
        "status": "pass",
        "errors": [],
        "warnings": [],
        "metrics": {},
    }

    if not path.exists():
        result["status"] = "fail"
        result["errors"].append("file does not exist")
        return result
    if not path.is_file():
        result["status"] = "fail"
        result["errors"].append("path is not a file")
        return result

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    result["metrics"] = {
        "characters": len(text),
        "lines": len(lines),
        "words": len(re.findall(r"\w+", text)),
    }

    if not text.strip():
        result["errors"].append("file is empty")

    hidden = hidden_char_findings(text)
    if hidden:
        result["errors"].append({"hidden_format_characters": hidden[:20], "count": len(hidden)})

    scaffold_hits = []
    for pattern in SCAFFOLD_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            scaffold_hits.append({"line": line, "match": match.group(0)})
    if scaffold_hits:
        result["warnings"].append({"scaffold_markers": scaffold_hits[:20], "count": len(scaffold_hits)})

    if require_output_format and not any(pattern.search(text) for pattern in OUTPUT_FORMAT_PATTERNS):
        result["warnings"].append("missing explicit output format cues")

    if require_success_criteria and not any(pattern.search(text) for pattern in SUCCESS_PATTERNS):
        result["warnings"].append("missing explicit success, validation, or verdict cues")

    if "ignore previous instructions" in text.lower():
        result["warnings"].append("contains an instruction-injection phrase; verify it is quoted as an example, not a directive")

    if result["errors"]:
        result["status"] = "fail"
    elif result["warnings"]:
        result["status"] = "warn"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint prompt files for deterministic quality hazards.")
    parser.add_argument("paths", nargs="+", help="prompt or markdown files to inspect")
    parser.add_argument("--json", action="store_true", help="emit json instead of text")
    parser.add_argument("--require-output-format", action="store_true", help="warn if output format is not explicit")
    parser.add_argument("--require-success-criteria", action="store_true", help="warn if validation or success criteria are not explicit")
    args = parser.parse_args()

    results = [lint_file(Path(p), args.require_output_format, args.require_success_criteria) for p in args.paths]
    exit_code = 1 if any(r["status"] == "fail" for r in results) else 0

    if args.json:
        print(json.dumps({"results": results}, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(f"{result['status'].upper()}: {result['path']}")
            for error in result["errors"]:
                print(f"  error: {error}")
            for warning in result["warnings"]:
                print(f"  warning: {warning}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
