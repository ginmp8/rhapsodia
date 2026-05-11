#!/usr/bin/env python3
"""Read-only static triage for skill security and governance review.

This script intentionally uses only the Python standard library, does not run target
code, does not install dependencies, and masks suspected secret values in output.
It is a triage helper; human review is still required.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

BLOCKED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}

SENSITIVE_NAME_PATTERNS = re.compile(
    r"(^|[._/-])(\.env|id_rsa|id_dsa|id_ecdsa|id_ed25519|credentials|credential|secret|secrets|private[_-]?key|token)([._/-]|$)",
    re.IGNORECASE,
)

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bash",
    ".zsh", ".ps1", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".env", ".dockerfile", ".lock", ".cs", ".java", ".go", ".rs", ".rb",
}

MANIFEST_NAMES = {
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.json",
    "gemfile",
    "gemfile.lock",
    "go.mod",
    "go.sum",
    "cargo.toml",
    "cargo.lock",
    "packages.lock.json",
    "directory.packages.props",
    "dockerfile",
}

SECRET_PATTERNS = [
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("connection-string-password", re.compile(r'(?i)(password|pwd)\s*=\s*[^;\s\'"]+')),
    (
        "credential-assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|client[_-]?secret|secret|token|password|passwd|pwd)\b\s*[:=]\s*['\"]([^'\"]{8,})['\"]"
        ),
    ),
]

DANGEROUS_SCRIPT_PATTERNS = [
    ("shell-true", re.compile(r"\bshell\s*=\s*True\b")),
    ("os-system", re.compile(r"\bos\.system\s*\(")),
    ("popen-shell", re.compile(r"\b(?:popen|Popen)\s*\(")),
    ("eval-or-exec", re.compile(r"\b(eval|exec)\s*\(")),
    ("curl-pipe-shell", re.compile(r"(?i)\b(curl|wget)\b[^\n|]*\|\s*(sh|bash)\b")),
    ("broad-delete", re.compile(r"\brm\s+-[rfRF]{1,4}\s+(?:/|\$\{|\$\w|\*)")),
    ("chmod-777", re.compile(r"\bchmod\s+777\b")),
    ("unsafe-yaml-load", re.compile(r"\byaml\.load\s*\(")),
    ("archive-extractall", re.compile(r"\b(?:extractall|extract)\s*\(")),
    ("pickle-load", re.compile(r"\bpickle\.loads?\s*\(")),
]

SENSITIVE_LOG_PATTERNS = [
    ("sensitive-print", re.compile(r"(?i)\bprint\s*\([^\n]*(token|secret|password|cookie|authorization|connectionstring|connection_string)")),
    ("sensitive-logger", re.compile(r"(?i)\blog(?:ger|ging)?\.[a-z]+\s*\([^\n]*(token|secret|password|cookie|authorization|connectionstring|connection_string)")),
]

AGENT_FILE_PATTERNS = re.compile(r"(?i)(^|/)(SKILL\.md|.*\.agent\.md|agents/.*\.ya?ml)$")
GOVERNANCE_KEYWORDS = re.compile(
    r"(?i)\b(allowlist|denylist|approval|audit|policy|permission|human[- ]in[- ]the[- ]loop|stop condition|fallback|fail[- ]closed|rate limit|tool boundary|handoff)\b"
)
AUTHORITY_KEYWORDS = re.compile(
    r"(?i)\b(terminalCommand|editFiles|delete|send_email|calendar|browser|network|subprocess|shell|execute|write|archive|trash|github|drive|mcp)\b"
)

@dataclass
class Finding:
    id: str
    mode: str
    classification: str
    severity: str
    confidence: str
    path: str
    line: Optional[int]
    title: str
    evidence: str
    recommendation: str


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name.lower() in MANIFEST_NAMES:
        return True
    try:
        with path.open("rb") as fh:
            chunk = fh.read(2048)
        if b"\x00" in chunk:
            return False
        return True
    except OSError:
        return False


def mask_secret(value: str) -> str:
    value = value.strip()
    if "PRIVATE KEY" in value:
        return "[masked private key block]"
    if len(value) <= 10:
        return "[masked secret]"
    return f"{value[:3]}...{value[-3:]}"


def mask_line(line: str) -> str:
    masked = line.rstrip("\n")
    for _, pattern in SECRET_PATTERNS:
        def repl(match: re.Match[str]) -> str:
            if match.lastindex and match.lastindex >= 2:
                return match.group(0).replace(match.group(2), mask_secret(match.group(2)))
            return mask_secret(match.group(0))
        masked = pattern.sub(repl, masked)
    return masked[:240]


def iter_files(target: Path, max_bytes: int) -> Iterable[Path]:
    if target.is_file():
        if not target.is_symlink() and target.stat().st_size <= max_bytes and is_probably_text(target):
            yield target
        return
    for current, dirs, files in os.walk(target, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in BLOCKED_DIR_NAMES and not SENSITIVE_NAME_PATTERNS.search(str(Path(current, d)))]
        for name in files:
            path = Path(current, name)
            if path.is_symlink():
                continue
            if SENSITIVE_NAME_PATTERNS.search(str(path)):
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            if is_probably_text(path):
                yield path


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def is_guidance_example(relative: str, line: str) -> bool:
    stripped = line.strip()
    return relative.startswith("references/") and stripped.startswith("- `") and stripped.endswith(".")


def add_finding(findings: List[Finding], mode: str, classification: str, severity: str, confidence: str, path: str, line: Optional[int], title: str, evidence: str, recommendation: str) -> None:
    findings.append(Finding(
        id=f"F-{len(findings)+1:03d}",
        mode=mode,
        classification=classification,
        severity=severity,
        confidence=confidence,
        path=path,
        line=line,
        title=title,
        evidence=evidence,
        recommendation=recommendation,
    ))


def scan_file(path: Path, root: Path, findings: List[Finding]) -> None:
    relative = rel(path, root)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    lines = text.splitlines()
    lower_name = path.name.lower()

    if lower_name in MANIFEST_NAMES:
        add_finding(
            findings,
            "dependency-risk-review",
            "evidence limitation",
            "informational",
            "medium",
            relative,
            None,
            "dependency manifest present",
            f"manifest detected: {relative}",
            "Review pinned versions, install hooks, registries, licenses, and vulnerability evidence with an approved scanner or current source.",
        )

    if AGENT_FILE_PATTERNS.search(relative):
        has_authority = AUTHORITY_KEYWORDS.search(text) is not None
        has_governance = GOVERNANCE_KEYWORDS.search(text) is not None
        if has_authority and not has_governance:
            add_finding(
                findings,
                "llm-agent-governance-review",
                "potential risk",
                "medium",
                "medium",
                relative,
                None,
                "authority terms without visible governance controls",
                "authority-related terms found, but governance terms such as approval, policy, audit, stop condition, or fail-closed were not detected",
                "Manually verify tool authority boundaries, explicit approval rules, audit trail requirements, and stop conditions.",
            )

    for idx, line in enumerate(lines, start=1):
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                severity = "critical" if name == "private-key-block" else "high"
                add_finding(
                    findings,
                    "secret-handling-review",
                    "potential risk",
                    severity,
                    "medium",
                    relative,
                    idx,
                    f"suspected secret pattern: {name}",
                    mask_line(line),
                    "Verify whether the value is real. If real, revoke or rotate it, remove it from the package, and add preventive secret scanning.",
                )
        for name, pattern in SENSITIVE_LOG_PATTERNS:
            if pattern.search(line):
                add_finding(
                    findings,
                    "secret-handling-review",
                    "potential risk",
                    "medium",
                    "medium",
                    relative,
                    idx,
                    f"sensitive logging pattern: {name}",
                    mask_line(line),
                    "Redact sensitive fields at field boundaries and add tests proving tokens, cookies, credentials, and connection strings are not logged.",
                )
        if is_guidance_example(relative, line):
            continue
        for name, pattern in DANGEROUS_SCRIPT_PATTERNS:
            if pattern.search(line):
                severity = "high" if name in {"shell-true", "os-system", "curl-pipe-shell", "broad-delete", "eval-or-exec"} else "medium"
                add_finding(
                    findings,
                    "script-security-review",
                    "potential risk",
                    severity,
                    "medium",
                    relative,
                    idx,
                    f"script safety pattern: {name}",
                    mask_line(line),
                    "Manually review exploitability. Prefer structured arguments, canonical path checks, dry-run modes, timeouts, and safe archive extraction.",
                )


def write_markdown(findings: List[Finding], target: Path) -> str:
    by_severity = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}
    sorted_findings = sorted(findings, key=lambda f: (by_severity.get(f.severity, 99), f.id))
    lines = [
        f"# Static Security Triage: {target}",
        "",
        "This is read-only static triage. Treat results as supporting evidence, not as final vulnerability confirmation.",
        "",
        f"Total findings: {len(sorted_findings)}",
        "",
    ]
    if not sorted_findings:
        lines.extend(["No findings from bundled static patterns.", ""])
        return "\n".join(lines)
    for f in sorted_findings:
        location = f"{f.path}:{f.line}" if f.line else f.path
        lines.extend([
            f"## {f.id} {f.title}",
            "",
            f"- **Mode:** {f.mode}",
            f"- **Classification:** {f.classification}",
            f"- **Severity:** {f.severity}",
            f"- **Confidence:** {f.confidence}",
            f"- **Location:** {location}",
            f"- **Evidence:** `{f.evidence}`",
            f"- **Recommendation:** {f.recommendation}",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only static security and governance triage for skill packages.")
    parser.add_argument("--target", required=True, help="File or directory to scan")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="Optional output file")
    parser.add_argument("--max-bytes", type=int, default=512_000, help="Maximum bytes per text file")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"target not found: {target}")

    root = target if target.is_dir() else target.parent
    findings: List[Finding] = []
    for path in iter_files(target, args.max_bytes):
        scan_file(path, root, findings)

    if args.format == "json":
        payload = {
            "target": str(target),
            "total_findings": len(findings),
            "findings": [asdict(f) for f in findings],
            "limitations": [
                "static pattern triage only",
                "no dependency installation or vulnerability database lookup",
                "secret values are masked and require manual verification",
                "blocked sensitive paths and large/binary files are skipped",
            ],
        }
        output = json.dumps(payload, indent=2, sort_keys=True)
    else:
        output = write_markdown(findings, target)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
