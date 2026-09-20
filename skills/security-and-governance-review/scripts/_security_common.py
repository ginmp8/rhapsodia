#!/usr/bin/env python3
"""Shared deterministic helpers for Security and Governance Review scripts."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

RUBRIC_VERSION = "SGR-2.0"
REPORT_VERSION = "security-review-report-1"
EVIDENCE_RECEIPT_VERSION = "security-evidence-receipt-1"

CLASSIFICATIONS = {
    "confirmed",
    "suspicious-pattern",
    "governance-risk",
    "needs-verification",
    "not-applicable",
}
SEVERITIES = {"critical", "high", "medium", "low", "informational"}
CONFIDENCES = {"high", "medium", "low"}

SECRET_PATTERNS = [
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("connection-string-password", re.compile(r"(?i)(?:password|pwd)\s*=\s*[^;\s'\"]+")),
    (
        "credential-assignment",
        re.compile(r"(?i)\b(api[_-]?key|client[_-]?secret|secret|token|password|passwd|pwd)\b\s*[:=]\s*['\"]([^'\"]{8,})['\"]"),
    ),
]

UNREAD_NAME_RE = re.compile(
    r"(^|/)(?:"
    r"\.env(?:\..*)?|\.npmrc|\.pypirc|\.netrc|\.git-credentials|kubeconfig|"
    r"credentials?(?:\..*)?|application_default_credentials\.json|"
    r"service[-_]?account[^/]*\.json|\.docker/config\.json|"
    r"id_(?:rsa|dsa|ecdsa|ed25519)|.*private[_-]?key.*|.*\.pem|.*\.p12|.*\.pfx"
    r")$",
    re.IGNORECASE,
)
HASH_ONLY_RE = re.compile(
    r"(^|/)(?:fixtures?|golden|expected(?:[-_ ]?outputs?)?)(/|$)|(^|/).*expected[-_ ]?output.*$",
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_id(*parts: object, prefix: str = "F") -> str:
    raw = "\x1f".join("" if p is None else str(p) for p in parts).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:10].upper()}"


def redact_text(text: str) -> str:
    """Deterministically redact recognized secret-like material without echoing any portion of its value."""
    redacted = text
    for name, pattern in SECRET_PATTERNS:
        replacement = "[masked private key block]" if name == "private-key-block" else "[masked secret]"
        if name == "credential-assignment":
            def repl(match: re.Match[str]) -> str:
                return f"{match.group(1)}=[masked secret]"
            redacted = pattern.sub(repl, redacted)
        else:
            redacted = pattern.sub(replacement, redacted)
    return redacted


def contains_secret_like(text: str) -> bool:
    return any(pattern.search(text) for _, pattern in SECRET_PATTERNS)


def protected_status(relative_path: str) -> str | None:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if UNREAD_NAME_RE.search(normalized):
        return "protected-unread"
    if HASH_ONLY_RE.search(normalized):
        return "protected-hash-only"
    return None


def output_aliases_target(target: Path, output: Path) -> bool:
    """Return True when writing output would mutate the reviewed target itself."""
    target_resolved = target.resolve(strict=False)
    output_resolved = output.resolve(strict=False)
    if target.is_dir():
        try:
            output_resolved.relative_to(target_resolved)
        except ValueError:
            return False
        return True
    return output_resolved == target_resolved


def require_external_output(target: Path, output: Path) -> None:
    """Reject output aliases so read-only review helpers cannot modify their target."""
    if output_aliases_target(target, output):
        scope = "target directory" if target.is_dir() else "target file"
        raise ValueError(f"output path must not alias or be inside the {scope}: {output}")
