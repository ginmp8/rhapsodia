#!/usr/bin/env python3
"""Validate deterministic structural integrity of a skill package or small technical artifact tree."""
from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".template"}
IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build"}
PLACEHOLDERS = [r"\[" + "TO" + "DO", "TO" + "DO:", "FI" + "XME", "REPLACE" + "_ME", "this is a " + "placeholder", "replace with " + "actual"]
REF_RE = re.compile(r"`([^`]+\.(?:md|py|json|yaml|yml|template|sh|js|ts|txt))`|\(([^)]+\.(?:md|py|json|yaml|yml|template|sh|js|ts|txt))\)")


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def diagnostic(severity: str, code: str, path: str, message: str, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"severity": severity, "code": code, "subject": path, "path": path, "message": message, "evidence": evidence or {}}


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, Any]] = []
    files = list(iter_files(root))
    skill_md = root / "SKILL.md"
    if skill_md.exists():
        text = read(skill_md)
        if not text.startswith("---\n"):
            findings.append(diagnostic("error", "skill/frontmatter-missing", "SKILL.md", "missing yaml frontmatter"))
        elif "\n---" not in text[4:]:
            findings.append(diagnostic("error", "skill/frontmatter-unterminated", "SKILL.md", "unterminated yaml frontmatter"))
    else:
        findings.append(diagnostic("warning", "skill/entrypoint-missing", ".", "SKILL.md not found; validating as generic artifact tree"))

    bash = shutil.which("bash")
    for path in files:
        suffix = path.suffix.lower()
        if suffix not in TEXT_EXTS:
            continue
        text = read(path)
        relative = rel(root, path)
        is_template = "/templates/" in f"/{relative}" or suffix == ".template"
        if not is_template:
            for pattern in PLACEHOLDERS:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    findings.append(diagnostic("error", "content/unresolved-scaffold", relative, f"unresolved scaffold marker: {pattern}", {"pattern": pattern}))
                    break
        if suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                findings.append(diagnostic("error", "json/invalid", relative, f"invalid json: {exc}", {"line": exc.lineno, "column": exc.colno}))
        if suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                findings.append(diagnostic("error", "python/syntax", relative, f"python syntax error: {exc}", {"line": exc.lineno, "offset": exc.offset}))
        if suffix == ".sh":
            if bash:
                result = subprocess.run([bash, "-n", str(path)], capture_output=True, text=True)
                if result.returncode != 0:
                    findings.append(diagnostic("error", "shell/syntax", relative, "shell syntax error: " + result.stderr.strip()[:240], {"exit_code": result.returncode}))
            else:
                findings.append(diagnostic("warning", "environment/bash-unavailable", relative, "bash unavailable; shell syntax check not run"))

    for path in files:
        if path.suffix.lower() not in {".md", ".template"}:
            continue
        text = read(path)
        relative = rel(root, path)
        for match in REF_RE.finditer(text):
            ref = match.group(1) or match.group(2)
            if ref.startswith(("http://", "https://", "#")):
                continue
            clean = ref.split("#", 1)[0]
            if "*" in clean or "?" in clean:
                continue
            local_prefixes = ("references/", "scripts/", "assets/", "examples/", "evals/", "tests/", "./")
            if not clean.startswith(local_prefixes):
                continue
            candidate = (path.parent / clean).resolve() if clean.startswith(".") else (root / clean).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                findings.append(diagnostic("error", "reference/escape", relative, f"referenced path escapes target: {ref}"))
                continue
            if not candidate.exists():
                findings.append(diagnostic("error", "reference/missing", relative, f"referenced file missing: {ref}", {"reference": ref}))

    findings = sorted(findings, key=lambda item: (item["severity"], item["code"], item["path"], item["message"]))
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    return {
        "receipt_version": 1,
        "status": "pass" if errors == 0 else "fail",
        "target": str(root),
        "file_count": len(files),
        "errors": errors,
        "warnings": warnings,
        "passed": errors == 0,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill/test artifact integrity deterministically.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()
    result = validate(Path(args.path))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"VALIDATION: {result['status'].upper()}")
        print(f"Files: {result['file_count']} Errors: {result['errors']} Warnings: {result['warnings']}")
        for finding in result["findings"]:
            print(f"- {finding['severity'].upper()} {finding['code']} {finding['path']}: {finding['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
