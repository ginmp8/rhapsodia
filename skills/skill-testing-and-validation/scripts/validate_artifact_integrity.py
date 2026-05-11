#!/usr/bin/env python3
"""Validate basic integrity of a skill package or small technical artifact tree."""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".template"}
IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build"}
PLACEHOLDERS = [r"\[" + "TO" + "DO", "TO" + "DO:", "FI" + "XME", "REPLACE" + "_ME", "this is a " + "placeholder", "replace with " + "actual"]
REF_RE = re.compile(r"`([^`]+\.(?:md|py|json|yaml|yml|template|sh|js|ts|txt))`|\(([^)]+\.(?:md|py|json|yaml|yml|template|sh|js|ts|txt))\)")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def validate(root: Path) -> dict:
    root = root.resolve()
    findings = []
    files = list(iter_files(root))
    skill_md = root / "SKILL.md"
    if skill_md.exists():
        text = read(skill_md)
        if not text.startswith("---\n"):
            findings.append({"severity": "error", "path": "SKILL.md", "message": "missing yaml frontmatter"})
        elif "\n---" not in text[4:]:
            findings.append({"severity": "error", "path": "SKILL.md", "message": "unterminated yaml frontmatter"})
    else:
        findings.append({"severity": "warning", "path": ".", "message": "SKILL.md not found; validating as generic artifact tree"})

    for path in files:
        suffix = path.suffix.lower()
        if suffix not in TEXT_EXTS:
            continue
        text = read(path)
        is_template = "/templates/" in rel(root, path) or suffix == ".template"
        if not is_template:
            for pattern in PLACEHOLDERS:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    findings.append({"severity": "error", "path": rel(root, path), "message": f"unresolved scaffold marker: {pattern}"})
                    break
        if suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                findings.append({"severity": "error", "path": rel(root, path), "message": f"invalid json: {exc}"})
        if suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                findings.append({"severity": "error", "path": rel(root, path), "message": f"python syntax error: {exc}"})
        if suffix == ".sh":
            result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
            if result.returncode != 0:
                findings.append({"severity": "error", "path": rel(root, path), "message": "shell syntax error: " + result.stderr.strip()[:240]})

    for path in files:
        if path.suffix.lower() not in {".md", ".template"}:
            continue
        text = read(path)
        for match in REF_RE.finditer(text):
            ref = match.group(1) or match.group(2)
            if ref.startswith(("http://", "https://", "#")):
                continue
            clean = ref.split("#", 1)[0]
            if "*" in clean or "?" in clean:
                continue
            local_prefixes = ("references/", "scripts/", "assets/", "examples/", "evals/", "./")
            if not clean.startswith(local_prefixes):
                continue
            candidate = (path.parent / clean).resolve() if clean.startswith(".") else (root / clean).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                continue
            if not candidate.exists():
                findings.append({"severity": "error", "path": rel(root, path), "message": f"referenced file missing: {ref}"})

    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    return {
        "target": str(root),
        "file_count": len(files),
        "errors": errors,
        "warnings": warnings,
        "passed": errors == 0,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill/test artifact integrity.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()
    result = validate(Path(args.path))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "PASSED" if result["passed"] else "FAILED"
        print(f"VALIDATION: {status}")
        print(f"Files: {result['file_count']} Errors: {result['errors']} Warnings: {result['warnings']}")
        for finding in result["findings"]:
            print(f"- {finding['severity'].upper()} {finding['path']}: {finding['message']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
