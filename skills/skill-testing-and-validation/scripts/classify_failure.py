#!/usr/bin/env python3
"""Classify build/test/lint/environment/configuration failures from command output."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = [
    ("environment", [r"command not found", r"No such file or directory", r"Permission denied", r"network is unreachable", r"Temporary failure in name resolution", r"timed out", r"out of memory", r"No module named pytest", r"Cannot find module ['\"]" ]),
    ("configuration", [r"invalid config", r"configuration error", r"missing required .*config", r"could not find .*config", r"JSONDecodeError", r"YAML", r"TOML", r"missing environment variable", r"No project file was found"]),
    ("build", [r"\bCS\d{4}\b", r"\bTS\d{4}\b", r"SyntaxError", r"py_compile", r"compilation failed", r"CompileError", r"cannot find symbol", r"undefined: ", r"failed to compile", r"type .* is not assignable", r"NETSDK\d+", r"MSB\d+"]),
    ("lint", [r"eslint", r"prettier", r"ruff", r"black", r"gofmt", r"rustfmt", r"dotnet format", r"shellcheck", r"markdownlint", r"yamllint", r"format check"]),
    ("packaging", [r"skill.zip", r"zip", r"archive", r"package validation", r"frontmatter", r"SKILL.md not found", r"exceeds the .*upload limit"]),
    ("validator", [r"validation failed", r"validator", r"schema", r"required field", r"unresolved scaffold", r"referenced file .*missing", r"placeholder"]),
    ("test", [r"\bFAILED\b", r"AssertionError", r"Expected", r"Actual", r"\d+ failed", r"tests? failed", r"FAIL ", r"FAILURES", r"pytest", r"jest", r"vitest", r"xUnit", r"NUnit", r"MSTest"]),
]


def classify(text: str) -> dict[str, object]:
    matches = []
    for category, patterns in PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                matches.append({"category": category, "pattern": pattern})
                break
    category = matches[0]["category"] if matches else "unknown"
    return {
        "category": category,
        "matches": matches,
        "summary": summarize(text),
    }


def summarize(text: str, max_lines: int = 25) -> list[str]:
    interesting = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.search(r"error|fail|exception|expected|actual|not found|denied|invalid|syntax|traceback|\bCS\d{4}\b|\bTS\d{4}\b", stripped, re.IGNORECASE):
            interesting.append(stripped[:240])
        if len(interesting) >= max_lines:
            break
    return interesting


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify command failure output.")
    parser.add_argument("logfile", nargs="?", help="Path to a log file. Reads stdin if omitted.")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    if args.logfile:
        text = Path(args.logfile).read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()
    result = classify(text)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"CATEGORY: {result['category']}")
        for line in result["summary"]:
            print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
