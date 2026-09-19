#!/usr/bin/env python3
"""Deterministically scan text-like files for likely credential exposure."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = 1
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024

IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv",
    "node_modules", "dist", "build", "target", "bin", "obj", "coverage",
    ".pytest_cache", ".mypy_cache", "__pycache__",
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go", ".rb", ".php",
    ".rs", ".swift", ".kt", ".kts", ".scala", ".sh", ".bash", ".zsh", ".ps1",
    ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf", ".env", ".properties",
    ".tf", ".tfvars", ".hcl", ".xml", ".html", ".md", ".txt", ".sql", ".dockerfile",
    ".pem", ".key", ".crt", ".cer",
}

SYNTHETIC_PATTERNS = [
    re.compile(r"(?i)your[_ -]?(api[_ -]?key|token|secret|password)"),
    re.compile(r"(?i)(example|sample|dummy|fake|test|synthetic|changeme|replace[_ -]?me)"),
]

# rule, regex, severity, confidence, evidence kind, priority
PATTERNS = [
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "critical", "likely", "private-key", 10),
    ("aws_access_key_id", re.compile(r"\b(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|ASIA)[A-Z0-9]{16}\b"), "high", "likely", "provider-token", 20),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "high", "likely", "provider-token", 20),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "high", "likely", "provider-token", 20),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"), "high", "likely", "provider-token", 20),
    ("stripe_live_key", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"), "critical", "likely", "provider-token", 20),
    ("authorization_header", re.compile(r"(?i)[\'\"]?authorization[\'\"]?\s*[:=]\s*[\'\"]?(bearer\s+[A-Za-z0-9._\-+/=]{8,})"), "high", "likely", "authorization", 30),
    ("database_uri", re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql|amqp)://[^\s:@/]+:[^\s@/]+@[^\s]+"), "high", "likely", "database-uri", 30),
    ("generic_assignment", re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|secret[_-]?key|client[_-]?secret|connection[_-]?string|token)\b\s*[:=]\s*[\'\"]?([^\'\"\s]{6,})"), "medium", "possible", "assignment", 80),
]

ASSIGNMENT_VALUE_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|secret[_-]?key|client[_-]?secret|token)\b\s*[:=]\s*[\'\"]?([^\'\"\s]{12,})"
)

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass(frozen=True)
class Finding:
    id: str
    path: str
    line: int
    severity: str
    confidence: str
    rule: str
    evidence: str


@dataclass(frozen=True)
class Skipped:
    path: str
    reason: str


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts: dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def is_probably_synthetic(value: str) -> bool:
    normalized = value.strip().strip("'\"")
    return any(pattern.search(normalized) for pattern in SYNTHETIC_PATTERNS)


def is_text_file(path: Path) -> bool:
    if path.name in {"Dockerfile", "Containerfile"}:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name.startswith(".")


def relative_name(path: Path, root: Path, root_is_file: bool) -> str:
    if root_is_file:
        return path.name
    return path.relative_to(root).as_posix()


def finding_id(path: str, line: int, rule: str) -> str:
    material = f"{path}\n{line}\n{rule}".encode("utf-8")
    return "scr-" + hashlib.sha256(material).hexdigest()[:16]


def safe_evidence(rule: str, evidence_kind: str, match: re.Match[str]) -> str:
    if evidence_kind == "private-key":
        return "private key block marker present"
    if evidence_kind == "provider-token":
        return f"{rule} value <redacted>"
    if evidence_kind == "authorization":
        return "authorization bearer value <redacted>"
    if evidence_kind == "database-uri":
        return "database URI contains embedded credentials <redacted>"
    if evidence_kind == "assignment":
        name = match.group(1)
        return f"{name}=<redacted>"
    return "credential-like value <redacted>"


def overlaps(span: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < other_end and other_start < end for other_start, other_end in spans)


def scan_line(rel_path: str, line_number: int, line: str) -> list[Finding]:
    candidates: list[tuple[int, tuple[int, int], Finding]] = []
    specific_spans: list[tuple[int, int]] = []

    for rule_name, pattern, severity, confidence, evidence_kind, priority in PATTERNS:
        match = pattern.search(line)
        if not match:
            continue

        if rule_name == "generic_assignment":
            value = match.group(2)
            if is_probably_synthetic(value) or overlaps(match.span(), specific_spans):
                continue
            if len(value) >= 20 and shannon_entropy(value) >= 3.2:
                severity = "high"
        else:
            specific_spans.append(match.span())

        candidates.append(
            (
                priority,
                match.span(),
                Finding(
                    id=finding_id(rel_path, line_number, rule_name),
                    path=rel_path,
                    line=line_number,
                    severity=severity,
                    confidence=confidence,
                    rule=rule_name,
                    evidence=safe_evidence(rule_name, evidence_kind, match),
                ),
            )
        )

    entropy_match = ASSIGNMENT_VALUE_RE.search(line)
    if entropy_match:
        value = entropy_match.group(2)
        span = entropy_match.span()
        if (
            not is_probably_synthetic(value)
            and len(value) >= 24
            and shannon_entropy(value) >= 3.6
            and not overlaps(span, specific_spans)
        ):
            candidates.append(
                (
                    90,
                    span,
                    Finding(
                        id=finding_id(rel_path, line_number, "high_entropy_secret_assignment"),
                        path=rel_path,
                        line=line_number,
                        severity="high",
                        confidence="possible",
                        rule="high_entropy_secret_assignment",
                        evidence=f"{entropy_match.group(1)}=<redacted>",
                    ),
                )
            )

    # Prefer a more specific rule when two detections overlap the same source value.
    accepted: list[tuple[int, tuple[int, int], Finding]] = []
    for candidate in sorted(candidates, key=lambda item: (item[0], item[1][0], item[2].rule)):
        _, span, _ = candidate
        if any(overlaps(span, [existing_span]) for _, existing_span, _ in accepted):
            continue
        accepted.append(candidate)

    return [item[2] for item in accepted]


def iter_candidates(root: Path, root_is_file: bool) -> Iterable[Path]:
    if root_is_file:
        if is_text_file(root):
            yield root
        return

    for current_root, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(current_root)
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in IGNORE_DIRS and not (base / d).is_symlink()
        )
        for filename in sorted(filenames):
            path = base / filename
            if is_text_file(path):
                yield path


def scan_target(root: Path, *, max_file_bytes: int) -> dict:
    root_is_file = root.is_file()
    findings: list[Finding] = []
    skipped: list[Skipped] = []
    considered = 0
    scanned = 0

    for path in iter_candidates(root, root_is_file):
        considered += 1
        rel_path = relative_name(path, root, root_is_file)

        if path.is_symlink():
            skipped.append(Skipped(rel_path, "symlink"))
            continue

        try:
            size = path.stat().st_size
        except OSError:
            skipped.append(Skipped(rel_path, "read-error"))
            continue

        if size > max_file_bytes:
            skipped.append(Skipped(rel_path, "too-large"))
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            skipped.append(Skipped(rel_path, "read-error"))
            continue

        scanned += 1
        for line_number, line in enumerate(content.splitlines(), start=1):
            findings.extend(scan_line(rel_path, line_number, line))

    deduped: dict[str, Finding] = {finding.id: finding for finding in findings}
    canonical_findings = sorted(
        deduped.values(),
        key=lambda item: (
            SEVERITY_ORDER[item.severity], item.path, item.line, item.rule, item.id
        ),
    )
    canonical_skipped = sorted(skipped, key=lambda item: (item.path, item.reason))

    summary = {
        severity: sum(1 for finding in canonical_findings if finding.severity == severity)
        for severity in ("critical", "high", "medium", "low")
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "partial" if canonical_skipped else "complete",
        "target": str(root),
        "summary": summary,
        "scan_stats": {
            "files_considered": considered,
            "files_scanned": scanned,
            "files_skipped": len(canonical_skipped),
            "findings": len(canonical_findings),
        },
        "skipped": [asdict(item) for item in canonical_skipped],
        "findings": [asdict(item) for item in canonical_findings],
    }


def render_text(payload: dict) -> str:
    lines = [
        f"Target: {payload['target']}",
        f"Status: {payload['status']}",
        "Summary:",
    ]
    for severity in ("critical", "high", "medium", "low"):
        lines.append(f"  {severity}: {payload['summary'][severity]}")

    stats = payload["scan_stats"]
    lines.append(
        "Coverage: "
        f"considered={stats['files_considered']} scanned={stats['files_scanned']} "
        f"skipped={stats['files_skipped']}"
    )

    if payload["skipped"]:
        lines.append("Skipped:")
        for item in payload["skipped"]:
            lines.append(f"- {item['path']}: {item['reason']}")

    lines.append("Findings:")
    if not payload["findings"]:
        lines.append("- none in scanned coverage")
    else:
        for finding in payload["findings"]:
            lines.append(
                f"- [{finding['severity']}/{finding['confidence']}] "
                f"{finding['path']}:{finding['line']} {finding['rule']} "
                f"({finding['id']}): {finding['evidence']}"
            )
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, text: str, *, input_root: Path) -> None:
    path = path.expanduser()
    if path.exists() and path.is_symlink():
        raise ValueError(f"Refusing symbolic-link output path: {path}")

    if input_root.is_file():
        try:
            if path.resolve(strict=False) == input_root.resolve(strict=True):
                raise ValueError("Output path aliases the input file")
        except OSError as exc:
            raise ValueError(f"Could not resolve output/input path safely: {exc}") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="File or directory to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="Optional output file written atomically")
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=DEFAULT_MAX_FILE_BYTES,
        help=f"Maximum candidate file size to scan (default: {DEFAULT_MAX_FILE_BYTES})",
    )
    args = parser.parse_args()

    if args.max_file_bytes < 1:
        parser.error("--max-file-bytes must be >= 1")

    authored_root = Path(args.path).expanduser()
    if authored_root.is_symlink():
        parser.error(f"Refusing symbolic-link input target: {authored_root}")
    if not authored_root.exists():
        parser.error(f"Path does not exist: {authored_root}")

    root = authored_root.resolve()
    payload = scan_target(root, max_file_bytes=args.max_file_bytes)

    if args.format == "json":
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    else:
        rendered = render_text(payload)

    if args.output:
        try:
            atomic_write(Path(args.output), rendered, input_root=root)
        except ValueError as exc:
            parser.error(str(exc))
        except OSError as exc:
            parser.error(f"Could not write output safely: {exc}")
    else:
        sys.stdout.write(rendered)
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
