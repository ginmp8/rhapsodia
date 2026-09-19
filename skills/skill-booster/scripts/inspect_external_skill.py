#!/usr/bin/env python3
"""Static trust intake for an external skill directory or ZIP without executing target code."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True

TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".ps1", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
EXEC_SUFFIXES = {".py", ".sh", ".bash", ".zsh", ".ps1", ".js", ".ts", ".exe", ".dll", ".so", ".dylib", ".bin", ".jar"}
SENSITIVE_NAME_RE = re.compile(r"(^|[-_.])(secret|secrets|credential|credentials|token|tokens|password|passwd)([-_.]|$)|private[-_.]?key|^\.env($|\.)", re.I)
SECRET_VALUE_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^\s'\"]{12,}", re.I),
]
DANGEROUS_PATTERNS = [
    (re.compile(r"\brm\s+-rf\s+(?:/|~|\$HOME)"), "destructive recursive delete"),
    (re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh)\b", re.I), "download piped to shell"),
    (re.compile(r"\bsudo\b"), "privilege escalation request"),
    (re.compile(r"\bchmod\s+777\b"), "world-writable permission"),
    (re.compile(r"\b(?:Invoke-Expression|iex)\b", re.I), "dynamic PowerShell execution"),
]
HOST_COUPLING = {
    "functions.exec": "openai-private-tool",
    "tools.skills__": "openai-private-tool",
    "container.exec": "openai-private-tool",
    "sandbox:/mnt/data": "openai-sandbox-path",
    "/home/oai/": "openai-sandbox-path",
    "/mnt/data/": "openai-sandbox-path",
    ".claude/skills": "host-install-path",
    ".cursor/skills": "host-install-path",
    ".github/skills": "host-install-path",
    ".copilot/skills": "host-install-path",
    ".codex/skills": "host-install-path",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add(findings: list[dict], code: str, severity: str, path: str, detail: str, line: int | None = None) -> None:
    item = {"code": code, "severity": severity, "path": path, "detail": detail}
    if line is not None:
        item["line"] = line
    findings.append(item)


def scan_text(text: str, rel: str, findings: list[dict]) -> None:
    for no, line in enumerate(text.splitlines(), 1):
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(line):
                add(findings, "POSSIBLE_SECRET_VALUE", "block", rel, "possible embedded secret/private key; value intentionally redacted", no)
                break
        for pattern, detail in DANGEROUS_PATTERNS:
            if pattern.search(line):
                add(findings, "DANGEROUS_EXECUTION_PATTERN", "review", rel, detail, no)
        for token, kind in HOST_COUPLING.items():
            if token in line:
                add(findings, "HOST_COUPLING", "review", rel, f"{kind}: {token}", no)


def inspect_directory(root: Path) -> tuple[list[dict], list[dict], list[str]]:
    findings: list[dict] = []
    files: list[dict] = []
    skill_roots: list[str] = []
    root = root.resolve()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            try:
                resolved = path.resolve(strict=False)
                resolved.relative_to(root)
                detail = f"symlink within root -> {resolved}"
                severity = "review"
            except Exception:
                detail = "symlink escapes or cannot be proven inside root"
                severity = "block"
            add(findings, "SYMLINK", severity, rel, detail)
            continue
        if not path.is_file():
            continue
        if path.name == "SKILL.md":
            skill_roots.append(rel)
        item = {"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path), "executable_surface": path.suffix.lower() in EXEC_SUFFIXES or os.access(path, os.X_OK)}
        files.append(item)
        if SENSITIVE_NAME_RE.search(path.name):
            add(findings, "SENSITIVE_FILENAME", "review", rel, "sensitive-looking filename; inspect manually without exposing values")
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 2_000_000:
            try:
                scan_text(path.read_text(encoding="utf-8"), rel, findings)
            except UnicodeDecodeError:
                add(findings, "TEXT_DECODE", "review", rel, "text-like file is not valid UTF-8")
    return findings, files, skill_roots


def zip_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def inspect_zip(path: Path) -> tuple[list[dict], list[dict], list[str]]:
    findings: list[dict] = []
    files: list[dict] = []
    skill_roots: list[str] = []
    with zipfile.ZipFile(path) as zf:
        for info in sorted(zf.infolist(), key=lambda x: x.filename):
            name = info.filename.replace("\\", "/")
            parts = PurePosixPath(name).parts
            if info.is_dir():
                continue
            if name.startswith("/") or ".." in parts:
                add(findings, "UNSAFE_ARCHIVE_PATH", "block", name, "absolute or traversal archive path")
                continue
            if zip_is_symlink(info):
                add(findings, "ARCHIVE_SYMLINK", "block", name, "symlink member blocked during external intake")
                continue
            if name.endswith("/SKILL.md") or name == "SKILL.md":
                skill_roots.append(name)
            data = zf.read(info)
            rel = name
            suffix = Path(rel).suffix.lower()
            files.append({"path": rel, "size": len(data), "sha256": sha256_bytes(data), "executable_surface": suffix in EXEC_SUFFIXES})
            if SENSITIVE_NAME_RE.search(Path(rel).name):
                add(findings, "SENSITIVE_FILENAME", "review", rel, "sensitive-looking filename; inspect manually without exposing values")
            if suffix in TEXT_SUFFIXES and len(data) <= 2_000_000:
                try:
                    scan_text(data.decode("utf-8"), rel, findings)
                except UnicodeDecodeError:
                    add(findings, "TEXT_DECODE", "review", rel, "text-like file is not valid UTF-8")
    return findings, files, skill_roots


def inspect(target: Path) -> dict:
    target = target.expanduser().resolve()
    if not target.exists():
        return {"status": "fail", "decision": "block", "errors": [{"code": "TARGET_MISSING", "severity": "block", "path": str(target), "detail": "target does not exist"}]}
    source_kind = "zip" if target.is_file() and target.suffix.lower() == ".zip" else "directory" if target.is_dir() else "unsupported"
    if source_kind == "unsupported":
        return {"status": "fail", "decision": "block", "errors": [{"code": "TARGET_TYPE", "severity": "block", "path": str(target), "detail": "target must be a skill directory or .zip"}]}
    try:
        findings, files, skill_roots = inspect_zip(target) if source_kind == "zip" else inspect_directory(target)
    except zipfile.BadZipFile as exc:
        return {"status": "fail", "decision": "block", "errors": [{"code": "BAD_ZIP", "severity": "block", "path": str(target), "detail": str(exc)}]}

    if len(skill_roots) != 1:
        add(findings, "SKILL_ROOT_COUNT", "block", str(target), f"expected exactly one SKILL.md entrypoint, found {len(skill_roots)}")

    blocks = [f for f in findings if f["severity"] == "block"]
    reviews = [f for f in findings if f["severity"] == "review"]
    decision = "block" if blocks else "requires-review" if reviews else "pass"
    source_sha256 = sha256_file(target) if source_kind == "zip" else None
    return {
        "receipt_version": 1,
        "source_class": "external-untrusted-skill",
        "status": "fail" if blocks else "pass",
        "decision": decision,
        "target": str(target),
        "source_kind": source_kind,
        "source_sha256": source_sha256,
        "skill_entrypoints": skill_roots,
        "file_count": len(files),
        "executable_surface_count": sum(1 for f in files if f["executable_surface"]),
        "files": files,
        "findings": findings,
        "summary": {"block": len(blocks), "review": len(reviews)},
        "target_code_executed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Statically inspect an external skill directory or ZIP before target code execution.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()
    report = inspect(Path(args.target))
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_path:
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
