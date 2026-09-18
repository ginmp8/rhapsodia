"""Detect secret-like content and unsafe symlinks without exposing matched values."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

MAX_SCAN_BYTES = 2 * 1024 * 1024
SAFE_ASSIGNMENT_VALUES = {
    "redacted",
    "redacted_example_value",
    "dummy",
    "dummy_value",
    "fake",
    "fake_value",
    "changeme",
    "<secret>",
    "<token>",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private key material",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    ),
    (
        "credential assignment",
        re.compile(
            r"\b(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET_ACCESS_KEY|AZURE_CLIENT_SECRET|"
            r"CLIENT_SECRET|API_KEY|ACCESS_TOKEN|AUTH_TOKEN|PASSWORD|CONNECTION_STRING)\b"
            r"\s*[:=]\s*[\"']?[^\s\"'#]{12,}",
            re.IGNORECASE,
        ),
    ),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("API token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
)


def _is_allowed_match(fragment: str) -> bool:
    if "=" not in fragment and ":" not in fragment:
        return False
    value = re.split(r"[:=]", fragment, maxsplit=1)[1].strip().strip("\"'").lower()
    return value in SAFE_ASSIGNMENT_VALUES or value.startswith("your_")


def scan_bytes(content: bytes, *, label: str) -> list[str]:
    if len(content) > MAX_SCAN_BYTES:
        return [f"content in {label} exceeds scan limit ({len(content)} > {MAX_SCAN_BYTES} bytes)"]
    if b"\x00" in content:
        return [f"binary content in {label} cannot be safely inspected"]
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [f"undecodable content in {label} cannot be safely inspected"]
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for finding_name, pattern in SENSITIVE_PATTERNS:
            matches = [match for match in pattern.finditer(line) if not _is_allowed_match(match.group(0))]
            if matches:
                findings.append(f"sensitive content in {label}:{line_number} ({finding_name})")
    return findings


def scan_paths(paths: Iterable[Path], root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            findings.append(f"symlink is not allowed in skill package: {relative}")
            continue
        if not path.is_file():
            continue
        try:
            findings.extend(scan_bytes(path.read_bytes(), label=relative))
        except OSError as exc:
            findings.append(f"unable to scan {relative}: {exc}")
    return findings


def scan_tree(root: Path) -> list[str]:
    return scan_paths((path for path in root.rglob("*") if path.is_file() or path.is_symlink()), root)
