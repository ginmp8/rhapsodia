#!/usr/bin/env python3
"""Static trust intake for an existing skill directory or ZIP. Never executes target code."""

from __future__ import annotations

import argparse
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SOURCE_CLASSES = {"trusted-owned", "trusted-local", "external-untrusted-skill"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".ps1", ".js", ".ts", ".toml", ".ini", ".cfg"}
EXECUTABLE_SUFFIXES = {".py", ".sh", ".ps1", ".js", ".ts", ".cmd", ".bat", ".exe", ".dll", ".so", ".dylib"}
SENSITIVE_NAMES = [
    re.compile(r"(^|[._-])\.env($|[._-])", re.IGNORECASE),
    re.compile(r"private[._-]?key", re.IGNORECASE),
    re.compile(r"(^|[._-])(secret|credential|token)s?($|[._-])", re.IGNORECASE),
]
PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("network-access", re.compile(r"\b(urllib\.request|requests\.|httpx\.|fetch\s*\(|curl\s+|wget\s+|https?://)", re.IGNORECASE), "requires-review"),
    ("shell-or-subprocess", re.compile(r"\b(subprocess\.|os\.system\s*\(|child_process|powershell\s+-|cmd\s+/c)", re.IGNORECASE), "requires-review"),
    ("environment-or-secret-access", re.compile(r"\b(os\.environ|os\.getenv|process\.env|secret|credential|api[_-]?key|access[_-]?token)\b", re.IGNORECASE), "requires-review"),
    ("permission-escalation", re.compile(r"\b(sudo\b|chmod\s+777|setfacl\b|runas\b)", re.IGNORECASE), "requires-review"),
    ("instruction-override", re.compile(r"\b(ignore|bypass|override)\b.{0,40}\b(previous|system|safety|policy|instruction)", re.IGNORECASE), "requires-review"),
    ("dynamic-code-execution", re.compile(r"\b(eval|exec)\s*\(", re.IGNORECASE), "requires-review"),
]
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")


def _finding(severity: str, category: str, path: str, evidence: str) -> dict[str, str]:
    return {"severity": severity, "category": category, "path": path, "evidence": evidence[:240]}


def _safe_zip_member(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:", name)


def _scan_text(rel: str, text: str, findings: list[dict[str, str]]) -> None:
    if PRIVATE_KEY_RE.search(text):
        findings.append(_finding("block", "private-key-material", rel, "private key marker found"))
    for category, pattern, severity in PATTERNS:
        if pattern.search(text):
            findings.append(_finding(severity, category, rel, f"pattern detected: {category}"))


def _status(findings: list[dict[str, str]]) -> str:
    if any(item["severity"] == "block" for item in findings):
        return "block"
    if any(item["severity"] == "requires-review" for item in findings):
        return "review"
    return "pass"


def _inspect_directory(target: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    files: list[str] = []
    skill_roots: list[str] = []
    for path in sorted(target.rglob("*")):
        rel = path.relative_to(target).as_posix()
        if path.is_symlink():
            findings.append(_finding("block", "symlink", rel, "symlink paths are not trusted during intake"))
            continue
        if not path.is_file():
            continue
        files.append(rel)
        if path.name == "SKILL.md":
            skill_roots.append(rel)
        if path.suffix.lower() in EXECUTABLE_SUFFIXES:
            findings.append(_finding("requires-review", "executable-surface", rel, "target-owned executable/script surface present"))
        if any(pattern.search(path.name) for pattern in SENSITIVE_NAMES):
            findings.append(_finding("block", "sensitive-file-name", rel, "sensitive-looking filename in untrusted package"))
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 2 * 1024 * 1024:
            try:
                _scan_text(rel, path.read_text(encoding="utf-8", errors="replace"), findings)
            except OSError as exc:
                findings.append(_finding("requires-review", "read-error", rel, str(exc)))
    if skill_roots != ["SKILL.md"]:
        findings.append(_finding("block", "ambiguous-skill-root", ".", f"expected exactly one root SKILL.md, found {skill_roots}"))
    return {"file_count": len(files), "skill_roots": skill_roots, "findings": findings}


def _inspect_zip(target: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    files: list[str] = []
    skill_roots: list[str] = []
    try:
        with zipfile.ZipFile(target) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = info.filename
                files.append(name)
                if not _safe_zip_member(name):
                    findings.append(_finding("block", "archive-path", name, "unsafe archive path"))
                    continue
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    findings.append(_finding("block", "symlink", name, "archive symlink is not trusted during intake"))
                if PurePosixPath(name).name == "SKILL.md":
                    skill_roots.append(name)
                suffix = PurePosixPath(name).suffix.lower()
                if suffix in EXECUTABLE_SUFFIXES:
                    findings.append(_finding("requires-review", "executable-surface", name, "target-owned executable/script surface present"))
                if any(pattern.search(PurePosixPath(name).name) for pattern in SENSITIVE_NAMES):
                    findings.append(_finding("block", "sensitive-file-name", name, "sensitive-looking filename in untrusted package"))
                if suffix in TEXT_SUFFIXES and info.file_size <= 2 * 1024 * 1024:
                    try:
                        text = zf.read(info).decode("utf-8", errors="replace")
                        _scan_text(name, text, findings)
                    except (OSError, KeyError, RuntimeError) as exc:
                        findings.append(_finding("requires-review", "read-error", name, str(exc)))
    except zipfile.BadZipFile:
        return {"file_count": 0, "skill_roots": [], "findings": [_finding("block", "archive-format", str(target), "not a readable ZIP")]}
    roots = {str(PurePosixPath(item).parent) for item in skill_roots}
    if len(skill_roots) != 1 or len(roots) != 1:
        findings.append(_finding("block", "ambiguous-skill-root", ".", f"expected one packaged SKILL.md, found {skill_roots}"))
    return {"file_count": len(files), "skill_roots": skill_roots, "findings": findings}


def inspect_target(target: Path, source_class: str = "external-untrusted-skill") -> dict[str, Any]:
    target = Path(target).resolve()
    if source_class not in SOURCE_CLASSES:
        raise ValueError(f"unsupported source class: {source_class}")
    if not target.exists():
        return {"status": "block", "source_class": source_class, "target": str(target), "findings": [_finding("block", "missing-target", str(target), "target does not exist")]}
    raw = _inspect_directory(target) if target.is_dir() else _inspect_zip(target) if target.is_file() and target.suffix.lower() == ".zip" else {
        "file_count": 0,
        "skill_roots": [],
        "findings": [_finding("block", "unsupported-target", str(target), "target must be a skill directory or ZIP")],
    }
    findings = raw["findings"]
    status = _status(findings)
    # Trusted sources still surface review findings, but source trust can authorize a caller
    # to proceed after explicit policy checks. This helper never executes target code.
    return {
        "status": status,
        "source_class": source_class,
        "target": str(target),
        "static_only": True,
        "target_code_executed": False,
        "file_count": raw["file_count"],
        "skill_roots": raw["skill_roots"],
        "findings": findings,
        "counts": {
            "block": sum(1 for item in findings if item["severity"] == "block"),
            "requires_review": sum(1 for item in findings if item["severity"] == "requires-review"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Statically inspect an existing skill before target-owned code is executed.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--source-class", choices=sorted(SOURCE_CLASSES), default="external-untrusted-skill")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = inspect_target(Path(args.target), source_class=args.source_class)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
