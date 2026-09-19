#!/usr/bin/env python3
"""Deterministic prompt lint with stable machine-readable diagnostics."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

VERSION = "2.0"

SCAFFOLD_PATTERNS = [
    re.compile(r"\b" + "TO" + r"DO\b", re.IGNORECASE),
    re.compile(r"\b" + "FIX" + r"ME\b", re.IGNORECASE),
    re.compile(r"\b" + "TB" + r"D\b", re.IGNORECASE),
    re.compile(r"\[\s*(replace|insert|fill|" + "to" + r"do|" + "tb" + r"d)[^\]]*\]", re.IGNORECASE),
    re.compile(r"lorem ipsum", re.IGNORECASE),
]

OUTPUT_FORMAT_PATTERNS = [
    re.compile(r"^#*\s*(output format|output contract)\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\b(return|respond|output)\b.+\b(json|markdown|table|list|schema|format|sections?)\b", re.IGNORECASE | re.DOTALL),
]

SUCCESS_PATTERNS = [
    re.compile(r"\bsuccess criteria\b", re.IGNORECASE),
    re.compile(r"\bacceptance criteria\b", re.IGNORECASE),
    re.compile(r"\bpass/fail\b", re.IGNORECASE),
    re.compile(r"\bvalidation\b", re.IGNORECASE),
    re.compile(r"\bhard gates?\b", re.IGNORECASE),
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


def _line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_newline = text.rfind("\n", 0, index)
    column = index + 1 if last_newline < 0 else index - last_newline
    return line, column


def finding(
    code: str,
    severity: str,
    subject: str,
    evidence: Any,
    *,
    line: int | None = None,
    column: int | None = None,
    supported_fixes: list[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "subject": subject,
        "evidence": evidence,
        "supported_fixes": supported_fixes or [],
    }
    if line is not None:
        item["line"] = line
    if column is not None:
        item["column"] = column
    return item


def lint_file(path: Path, require_output_format: bool, require_success_criteria: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "status": "pass",
        "findings": [],
        "metrics": {},
        "validator": {"name": "prompt_lint", "version": VERSION},
    }

    if not path.exists():
        result["findings"].append(finding("PROMPT_FILE_MISSING", "error", str(path), "file does not exist"))
        result["status"] = "fail"
        return result
    if not path.is_file():
        result["findings"].append(finding("PROMPT_PATH_NOT_FILE", "error", str(path), "path is not a file"))
        result["status"] = "fail"
        return result

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        result["findings"].append(finding("PROMPT_INVALID_UTF8", "error", str(path), str(exc)))
        result["status"] = "fail"
        return result

    lines = text.splitlines()
    result["metrics"] = {
        "characters": len(text),
        "lines": len(lines),
        "words": len(re.findall(r"\w+", text)),
    }

    if not text.strip():
        result["findings"].append(
            finding("PROMPT_EMPTY", "error", str(path), "file is empty", supported_fixes=["add the intended prompt content"])
        )

    hidden_count = 0
    for idx, ch in enumerate(text):
        category = unicodedata.category(ch)
        name = unicodedata.name(ch, "")
        if category == "Cf" or name in BIDI_NAMES:
            hidden_count += 1
            if hidden_count <= 20:
                line, col = _line_col(text, idx)
                result["findings"].append(
                    finding(
                        "PROMPT_HIDDEN_FORMAT_CHAR",
                        "error",
                        f"{path}:{line}:{col}",
                        name or category,
                        line=line,
                        column=col,
                        supported_fixes=["remove the hidden formatting character unless intentionally required and documented"],
                    )
                )
    if hidden_count > 20:
        result["findings"].append(
            finding("PROMPT_HIDDEN_FORMAT_CHAR_TRUNCATED", "warning", str(path), {"total": hidden_count, "reported": 20})
        )

    for pattern in SCAFFOLD_PATTERNS:
        for match in pattern.finditer(text):
            line, col = _line_col(text, match.start())
            result["findings"].append(
                finding(
                    "PROMPT_SCAFFOLD_MARKER",
                    "warning",
                    f"{path}:{line}",
                    match.group(0),
                    line=line,
                    column=col,
                    supported_fixes=["replace the scaffold marker with a real requirement or remove the unused section"],
                )
            )

    if require_output_format and not any(pattern.search(text) for pattern in OUTPUT_FORMAT_PATTERNS):
        result["findings"].append(
            finding(
                "PROMPT_OUTPUT_CONTRACT_MISSING",
                "warning",
                str(path),
                "no explicit output format/contract cue detected",
                supported_fixes=["define the required output structure, syntax, ordering, or error representation"],
            )
        )

    if require_success_criteria and not any(pattern.search(text) for pattern in SUCCESS_PATTERNS):
        result["findings"].append(
            finding(
                "PROMPT_SUCCESS_CRITERIA_MISSING",
                "warning",
                str(path),
                "no success/acceptance/validation cue detected",
                supported_fixes=["add observable success or acceptance criteria"],
            )
        )

    injection_phrase = re.search(r"ignore\s+(all\s+)?previous\s+instructions", text, re.IGNORECASE)
    if injection_phrase:
        line, col = _line_col(text, injection_phrase.start())
        result["findings"].append(
            finding(
                "PROMPT_INJECTION_PHRASE_PRESENT",
                "warning",
                f"{path}:{line}",
                injection_phrase.group(0),
                line=line,
                column=col,
                supported_fixes=["verify the phrase is quoted/example data rather than an operative directive"],
            )
        )

    severities = [x["severity"] for x in result["findings"]]
    if "error" in severities:
        result["status"] = "fail"
    elif "warning" in severities:
        result["status"] = "warn"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint prompt files for deterministic quality hazards.")
    parser.add_argument("paths", nargs="+", help="prompt or markdown files to inspect")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--require-output-format", action="store_true", help="warn if output format is not explicit")
    parser.add_argument("--require-success-criteria", action="store_true", help="warn if success/validation criteria are not explicit")
    parser.add_argument("--strict", action="store_true", help="treat warnings as a failing exit status")
    args = parser.parse_args()

    results = [lint_file(Path(p), args.require_output_format, args.require_success_criteria) for p in args.paths]
    if any(r["status"] == "fail" for r in results):
        exit_code = 1
    elif args.strict and any(r["status"] == "warn" for r in results):
        exit_code = 2
    else:
        exit_code = 0

    payload = {
        "schema_version": 2,
        "validator": {"name": "prompt_lint", "version": VERSION},
        "status": "fail" if exit_code else ("warn" if any(r["status"] == "warn" for r in results) else "pass"),
        "results": results,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        for result in results:
            print(f"{result['status'].upper()}: {result['path']}")
            for item in result["findings"]:
                where = f" line={item['line']}" if "line" in item else ""
                print(f"  {item['severity']}: {item['code']}:{where} {item['evidence']}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
