#!/usr/bin/env python3
"""Deterministic, read-only static triage for security/governance review.

The scanner never executes target code or installs dependencies. Recognized secret
values are never emitted. Findings are triage evidence and do not by themselves
prove a vulnerability, CVE, exploitability, or concrete exposure.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

from _security_common import RUBRIC_VERSION, SECRET_PATTERNS, protected_status, redact_text, require_external_output, sha256_bytes, stable_id

BLOCKED_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".venv", "venv", "node_modules", "dist", "build"}
TEXT_EXTENSIONS = {".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".ps1", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".dockerfile", ".lock", ".cs", ".java", ".go", ".rs", ".rb"}
MANIFEST_NAMES = {"requirements.txt", "pyproject.toml", "poetry.lock", "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.json", "gemfile", "gemfile.lock", "go.mod", "go.sum", "cargo.toml", "cargo.lock", "packages.lock.json", "directory.packages.props", "dockerfile"}
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
AGENT_FILE_PATTERNS = re.compile(r"(?i)(^|/)(SKILL\.md|agent\.md|.*\.agent\.md|agents/.*\.ya?ml)$")
GOVERNANCE_KEYWORDS = re.compile(r"(?i)\b(allowlist|denylist|approval|audit|policy|permission|human[- ]in[- ]the[- ]loop|stop condition|fallback|fail[- ]closed|rate limit|tool boundary|handoff)\b")
AUTHORITY_KEYWORDS = re.compile(r"(?i)\b(terminalCommand|editFiles|delete|publish|send_email|calendar|browser|network|subprocess|shell|execute|write|archive|trash|github|drive|mcp)\b")
NEGATED_GOVERNANCE = re.compile(r"(?i)\b(without|no|missing|lacks?|absent)\b[^\n]{0,48}\b(approval|policy|permission|audit|stop condition|fail[- ]closed)\b")


@dataclass(frozen=True)
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
    risk: str
    recommendation: str
    validation: str


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS or path.name.lower() in MANIFEST_NAMES:
        return True
    try:
        with path.open("rb") as fh:
            return b"\x00" not in fh.read(2048)
    except OSError:
        return False


def iter_files(target: Path, max_bytes: int) -> Iterable[Path]:
    if target.is_file():
        if not target.is_symlink() and protected_status(target.name) is None and target.stat().st_size <= max_bytes and is_probably_text(target):
            yield target
        return
    for current, dirs, files in os.walk(target, topdown=True, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in BLOCKED_DIR_NAMES)
        for name in sorted(files):
            path = Path(current, name)
            try:
                relative = path.relative_to(target).as_posix()
                if path.is_symlink() or protected_status(relative) is not None or path.stat().st_size > max_bytes:
                    continue
            except (OSError, ValueError):
                continue
            if is_probably_text(path):
                yield path


def evidence_fingerprint(line: str, pattern: str) -> str:
    return f"pattern={pattern}; content=[redacted]; source_line_sha256={sha256_bytes(line.encode('utf-8'))[:16]}"


def add(findings: list[Finding], *, mode: str, classification: str, severity: str, confidence: str, path: str, line: Optional[int], title: str, evidence: str, risk: str, recommendation: str, validation: str) -> None:
    fid = stable_id(mode, classification, severity, path, line, title)
    findings.append(Finding(fid, mode, classification, severity, confidence, path, line, title, evidence, risk, recommendation, validation))


def scan_file(path: Path, root: Path, findings: list[Finding]) -> None:
    relative = path.relative_to(root).as_posix() if path != root else path.name
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    lines = text.splitlines()
    if path.name.lower() in MANIFEST_NAMES:
        add(findings, mode="dependency-risk-review", classification="needs-verification", severity="informational", confidence="high", path=relative, line=None,
            title="dependency manifest requires external/current vulnerability evidence",
            evidence=f"manifest={relative}; source_file_sha256={sha256_bytes(path.read_bytes())}",
            risk="Static manifest presence does not establish whether dependencies are vulnerable, unsupported, or policy-compliant.",
            recommendation="Resolve exact dependency/source identity and use an approved scanner or authoritative current source before making vulnerability/CVE claims.",
            validation="Record package/version plus scanner/advisory identity; otherwise keep the conclusion as needs-verification.")

    if AGENT_FILE_PATTERNS.search(relative):
        has_authority = AUTHORITY_KEYWORDS.search(text) is not None
        governance_text = NEGATED_GOVERNANCE.sub("", text)
        has_governance = GOVERNANCE_KEYWORDS.search(governance_text) is not None
        if has_authority and not has_governance:
            add(findings, mode="llm-agent-governance-review", classification="governance-risk", severity="medium", confidence="medium", path=relative, line=None,
                title="authority terms without visible governance controls",
                evidence="authority-capable actions detected; explicit approval/policy/audit/stop/fail-closed controls not detected",
                risk="An agent may receive broader effective authority than intended or fail open when authorization is ambiguous.",
                recommendation="Verify the authority matrix and add explicit mutation scope, approval gates, audit requirements, and fail-closed stop conditions where required.",
                validation="Re-run static triage and manually verify each read/write/execute/delete/send/publish authority against its authorization rule.")

    for idx, line in enumerate(lines, start=1):
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                severity = "critical" if name == "private-key-block" else "high"
                add(findings, mode="secret-handling-review", classification="suspicious-pattern", severity=severity, confidence="medium", path=relative, line=idx,
                    title=f"suspected secret pattern: {name}", evidence=evidence_fingerprint(line, name),
                    risk="The source contains a credential-shaped value; authenticity, scope, and exposure are not established by pattern matching alone.",
                    recommendation="Verify through an authorized secret-management/source-of-truth path without printing the value. If real, revoke/rotate and remove it from the package.",
                    validation="Confirm source identity and credential status through an approved mechanism; never copy the full value into the report.")
        for name, pattern in SENSITIVE_LOG_PATTERNS:
            if pattern.search(line):
                add(findings, mode="secret-handling-review", classification="suspicious-pattern", severity="medium", confidence="medium", path=relative, line=idx,
                    title=f"sensitive logging pattern: {name}", evidence=evidence_fingerprint(line, name),
                    risk="Runtime logs may disclose authentication or session material if the referenced field contains live sensitive data.",
                    recommendation="Redact at field boundaries and avoid full request/response logging for sensitive operations.",
                    validation="Run redaction tests with fake credentials and verify no complete secret value appears in logs or reports.")
        stripped = line.strip()
        if relative.startswith("references/") and stripped.startswith("- `") and stripped.endswith("."):
            continue
        for name, pattern in DANGEROUS_SCRIPT_PATTERNS:
            if pattern.search(line):
                severity = "high" if name in {"shell-true", "os-system", "curl-pipe-shell", "broad-delete", "eval-or-exec"} else "medium"
                add(findings, mode="script-security-review", classification="suspicious-pattern", severity=severity, confidence="medium", path=relative, line=idx,
                    title=f"script safety pattern: {name}", evidence=redact_text(line.strip())[:240],
                    risk="The construct can become unsafe when influenced by untrusted input or broad filesystem authority; exploitability is not proven by syntax alone.",
                    recommendation="Manually trace input/control flow and prefer structured arguments, canonical path checks, timeouts, dry-run or safe extraction as applicable.",
                    validation="Use a safe fixture to test traversal/injection boundaries and confirm the dangerous primitive cannot receive untrusted input.")


def sorted_findings(findings: list[Finding]) -> list[Finding]:
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}
    return sorted(findings, key=lambda f: (order.get(f.severity, 99), f.path, -1 if f.line is None else f.line, f.id))


def write_markdown(findings: list[Finding], target: Path) -> str:
    findings = sorted_findings(findings)
    lines = [f"# Static Security Triage: {target}", "", f"Rubric: {RUBRIC_VERSION}", "", "Read-only static triage; findings are supporting evidence, not final vulnerability confirmation.", "", f"Total findings: {len(findings)}", ""]
    if not findings:
        return "\n".join(lines + ["No findings from bundled static patterns.", ""])
    for f in findings:
        loc = f"{f.path}:{f.line}" if f.line else f.path
        lines += [f"## {f.id} {f.title}", "", f"- **Mode:** {f.mode}", f"- **Classification:** {f.classification}", f"- **Severity:** {f.severity}", f"- **Confidence:** {f.confidence}", f"- **Location:** {loc}", f"- **Evidence:** `{f.evidence}`", f"- **Risk:** {f.risk}", f"- **Recommendation:** {f.recommendation}", f"- **Validation:** {f.validation}", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only deterministic security/governance static triage.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--output")
    ap.add_argument("--max-bytes", type=int, default=512_000)
    args = ap.parse_args()
    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"target not found: {target}")
    if args.output:
        try:
            require_external_output(target, Path(args.output))
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    root = target if target.is_dir() else target.parent
    findings: list[Finding] = []
    for path in iter_files(target, args.max_bytes):
        scan_file(path, root, findings)
    findings = sorted_findings(findings)
    if args.format == "json":
        payload = {
            "scanner_version": 2,
            "rubric_version": RUBRIC_VERSION,
            "target": str(target),
            "total_findings": len(findings),
            "findings": [asdict(f) for f in findings],
            "limitations": [
                "static pattern triage only",
                "no dependency installation or vulnerability database lookup",
                "recognized secret values are never emitted",
                "protected sensitive paths, symlinks, large files, and binaries are skipped",
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
