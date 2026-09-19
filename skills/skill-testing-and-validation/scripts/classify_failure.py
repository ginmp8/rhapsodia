#!/usr/bin/env python3
"""Deterministically classify command failures with stable evidence codes."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CATEGORIES = ("build", "test", "lint", "validator", "environment", "configuration", "packaging", "unknown")
GATES = ("build", "test", "lint", "validator", "packaging")
PATTERNS: dict[str, list[tuple[str, str]]] = {
    "environment": [
        ("environment/command-missing", r"command not found|is not recognized as an internal or external command"),
        ("environment/file-missing", r"No such file or directory"),
        ("environment/permission", r"Permission denied|read-only file system"),
        ("environment/network", r"network is unreachable|Temporary failure in name resolution|could not resolve host"),
        ("environment/timeout", r"timed out|timeout expired"),
        ("environment/memory", r"out of memory|MemoryError"),
        ("environment/dependency-missing", r"No module named [\w.]+|Cannot find module ['\"]|module not found"),
    ],
    "configuration": [
        ("configuration/invalid", r"invalid config|configuration error|malformed .*config"),
        ("configuration/missing", r"missing required .*config|could not find .*config|missing environment variable|No project file was found"),
        ("configuration/json", r"JSONDecodeError"),
        ("configuration/yaml", r"YAML.*(?:error|invalid)|yaml.*(?:error|invalid)"),
        ("configuration/toml", r"TOML.*(?:error|invalid)|toml.*(?:error|invalid)"),
    ],
    "packaging": [
        ("packaging/archive", r"skill\.zip|archive|package validation|exceeds the .*upload limit"),
        ("packaging/entrypoint", r"SKILL\.md not found|frontmatter"),
    ],
    "validator": [
        ("validator/failed", r"validation failed|validator"),
        ("validator/schema", r"schema|required field|unresolved scaffold|referenced file .*missing|placeholder"),
    ],
    "build": [
        ("build/compiler", r"\bCS\d{4}\b|\bTS\d{4}\b|NETSDK\d+|MSB\d+|compilation failed|failed to compile|CompileError"),
        ("build/syntax", r"SyntaxError|py_compile"),
        ("build/symbol", r"cannot find symbol|undefined: |type .* is not assignable"),
    ],
    "lint": [
        ("lint/tool", r"eslint|prettier|ruff|black|gofmt|rustfmt|dotnet format|shellcheck|markdownlint|yamllint|format check"),
    ],
    "test": [
        ("test/assertion", r"AssertionError|Expected|Actual|expected .* actual"),
        ("test/summary", r"\bFAILED\b|\d+ failed|tests? failed|FAILURES|^FAIL "),
        ("test/framework", r"pytest|jest|vitest|xUnit|NUnit|MSTest"),
    ],
}


def find_evidence(text: str, category: str) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for code, pattern in PATTERNS.get(category, []):
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            evidence.append({"category": category, "code": code, "pattern": pattern, "match": match.group(0)[:160]})
    return evidence


def summarize(text: str, max_lines: int = 25) -> list[str]:
    interesting: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.search(r"error|fail|exception|expected|actual|not found|denied|invalid|syntax|traceback|\bCS\d{4}\b|\bTS\d{4}\b", stripped, re.IGNORECASE):
            interesting.append(stripped[:240])
        if len(interesting) >= max_lines:
            break
    return interesting


def classify(text: str, gate: str | None = None, exit_code: int | None = None) -> dict[str, Any]:
    all_evidence = {category: find_evidence(text, category) for category in PATTERNS}
    if all_evidence["environment"]:
        category = "environment"
    elif all_evidence["configuration"]:
        category = "configuration"
    elif gate in GATES:
        category = gate
    else:
        category = next((item for item in ("packaging", "validator", "build", "lint", "test") if all_evidence[item]), "unknown")
    evidence = all_evidence.get(category, [])
    if gate == category and not evidence and category in GATES:
        evidence = [{"category": category, "code": f"{category}/gate-context", "pattern": "<gate-context>", "match": "non-zero exit classified by explicit gate"}]
    code = evidence[0]["code"] if evidence else "unknown/unclassified"
    legacy_matches = [{"category": item["category"], "pattern": item["pattern"]} for values in all_evidence.values() for item in values]
    return {
        "classification_version": 1,
        "category": category,
        "code": code,
        "gate": gate,
        "exit_code": exit_code,
        "evidence": evidence,
        "matches": legacy_matches,
        "summary": summarize(text),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify command failure output deterministically.")
    parser.add_argument("logfile", nargs="?", help="Path to a log file. Reads stdin if omitted.")
    parser.add_argument("--gate", choices=GATES)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()
    text = Path(args.logfile).read_text(encoding="utf-8", errors="replace") if args.logfile else sys.stdin.read()
    result = classify(text, gate=args.gate, exit_code=args.exit_code)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"CATEGORY: {result['category']}")
        print(f"CODE: {result['code']}")
        for line in result["summary"]:
            print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
