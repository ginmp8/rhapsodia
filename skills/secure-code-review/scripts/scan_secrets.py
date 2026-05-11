#!/usr/bin/env python3
"""Scan files and directories for likely hardcoded secrets and unsafe secret handling."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv",
    "node_modules", "dist", "build", "target", "bin", "obj", "coverage",
    ".pytest_cache", ".mypy_cache", "__pycache__"
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go", ".rb", ".php",
    ".rs", ".swift", ".kt", ".kts", ".scala", ".sh", ".bash", ".zsh", ".ps1",
    ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf", ".env", ".properties",
    ".tf", ".tfvars", ".hcl", ".xml", ".html", ".md", ".txt", ".sql", ".dockerfile"
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"(?i)your[_ -]?(api[_ -]?key|token|secret|password)"),
    re.compile(r"(?i)(example|sample|dummy|fake|test|placeholder|changeme|replace[_ -]?me)"),
]

PATTERNS = [
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "critical"),
    ("aws_access_key_id", re.compile(r"\b(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|ASIA)[A-Z0-9]{16}\b"), "high"),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "high"),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "high"),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"), "high"),
    ("stripe_live_key", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"), "critical"),
    ("generic_assignment", re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|secret[_-]?key|client[_-]?secret|connection[_-]?string|token)\b\s*[:=]\s*['\"]?([^'\"\s]{6,})"), "medium"),
    ("authorization_header", re.compile(r"(?i)[\'\"]?authorization[\'\"]?\s*[:=]\s*[\'\"]?(bearer\s+[A-Za-z0-9._\-+/=]{8,})"), "high"),
    ("database_uri", re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql|amqp)://[^\s:@/]+:[^\s@/]+@[^\s]+"), "high"),
]

ASSIGNMENT_VALUE_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|secret[_-]?key|client[_-]?secret|token)\b\s*[:=]\s*['\"]?([^'\"\s]{12,})"
)


@dataclass
class Finding:
    path: str
    line: int
    severity: str
    rule: str
    evidence: str


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = {ch: text.count(ch) for ch in set(text)}
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def is_probably_placeholder(value: str) -> bool:
    lowered = value.strip().strip("'\"")
    return any(pattern.search(lowered) for pattern in PLACEHOLDER_PATTERNS)


def is_text_file(path: Path) -> bool:
    if path.name == "Dockerfile":
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name.startswith(".")


def iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if is_text_file(root):
            yield root
        return

    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        base = Path(current_root)
        for filename in filenames:
            path = base / filename
            if is_text_file(path):
                yield path


def redact(text: str, max_len: int = 120) -> str:
    text = text.rstrip("\n")
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    for line_number, line in enumerate(content.splitlines(), start=1):
        for rule_name, pattern, severity in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue

            candidate = match.group(0)
            if rule_name == "generic_assignment":
                value = match.group(2)
                if is_probably_placeholder(value):
                    continue
                entropy = shannon_entropy(value)
                if len(value) >= 20 and entropy >= 3.2:
                    sev = "high"
                else:
                    sev = severity
            else:
                sev = severity

            findings.append(
                Finding(
                    path=str(path),
                    line=line_number,
                    severity=sev,
                    rule=rule_name,
                    evidence=redact(candidate),
                )
            )

        entropy_match = ASSIGNMENT_VALUE_RE.search(line)
        if entropy_match:
            value = entropy_match.group(2)
            if not is_probably_placeholder(value) and len(value) >= 24 and shannon_entropy(value) >= 3.6:
                findings.append(
                    Finding(
                        path=str(path),
                        line=line_number,
                        severity="high",
                        rule="high_entropy_secret_assignment",
                        evidence=redact(line.strip()),
                    )
                )

    deduped: dict[tuple[str, int, str, str], Finding] = {}
    for finding in findings:
        key = (finding.path, finding.line, finding.severity, finding.rule)
        deduped[key] = finding
    return sorted(deduped.values(), key=lambda item: (item.path, item.line, item.rule))


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return dict(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="File or directory to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        parser.error(f"Path does not exist: {root}")

    all_findings: list[Finding] = []
    for file_path in iter_files(root):
        all_findings.extend(scan_file(file_path))

    payload = {
        "target": str(root),
        "summary": summarize(all_findings),
        "findings": [asdict(finding) for finding in all_findings],
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Target: {payload['target']}")
    if not all_findings:
        print("No likely secret findings.")
        return 0

    print("Summary:")
    for severity, count in payload["summary"].items():
        print(f"  {severity}: {count}")

    print("\nFindings:")
    for finding in all_findings:
        print(f"- [{finding.severity}] {finding.path}:{finding.line} {finding.rule}: {finding.evidence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
