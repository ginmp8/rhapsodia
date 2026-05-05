#!/usr/bin/env python3
"""Static helper for skill-change-gate.

Checks mechanical package properties for an after target and, optionally, a before
folder. This script is evidence for structural facts only; the skill still makes
the final semantic gate decision.
"""
from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


@dataclass
class Finding:
    severity: str
    area: str
    message: str


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"(?<!!)(?:\[[^\]]+\]\(([^)]+)\))")
SCAFFOLD_WORDS = ["TO" + "DO", "FIX" + "ME", "T" + "BD", "PLACE" + "HOLDER", "X" + "XX"]
SCAFFOLD_RE = re.compile(r"\b(" + "|".join(SCAFFOLD_WORDS) + r")\b", re.IGNORECASE)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def root_skill_md(target: Path, findings: list[Finding]) -> Path | None:
    candidate = target / "SKILL.md"
    nested = [p for p in target.rglob("SKILL.md") if p != candidate and ".git" not in p.parts]
    if not candidate.exists():
        findings.append(Finding("blocking", "package", "root SKILL.md is missing"))
        if nested:
            findings.append(Finding("blocking", "package", f"found nested SKILL.md files without root: {len(nested)}"))
        return None
    if nested:
        findings.append(Finding("material", "package", f"nested SKILL.md files exist and may indicate ambiguous package roots: {len(nested)}"))
    return candidate


def parse_frontmatter(text: str, findings: list[Finding]) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        findings.append(Finding("blocking", "frontmatter", "SKILL.md is missing YAML frontmatter delimited by ---"))
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            findings.append(Finding("blocking", "frontmatter", f"invalid frontmatter line: {line}"))
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    for required in ("name", "description"):
        if not data.get(required):
            findings.append(Finding("blocking", "frontmatter", f"missing required frontmatter field: {required}"))
    if data.get("name") and not NAME_RE.match(data["name"]):
        findings.append(Finding("blocking", "frontmatter", "frontmatter name is not lowercase hyphen-case"))
    if data.get("description") and len(data["description"].split()) < 20:
        findings.append(Finding("material", "activation", "frontmatter description may be too short for reliable activation"))
    return data


def iter_files(root: Path) -> Iterable[Path]:
    ignored_parts = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    for path in root.rglob("*"):
        if any(part in ignored_parts for part in path.parts):
            continue
        yield path


def check_links(root: Path, text: str, findings: list[Finding]) -> None:
    for raw in LINK_RE.findall(text):
        link = raw.split("#", 1)[0].strip()
        if not link or re.match(r"^[a-z]+://", link) or link.startswith("mailto:"):
            continue
        if link.startswith("#"):
            continue
        target = (root / link).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            findings.append(Finding("blocking", "references", f"local markdown link escapes package: {raw}"))
            continue
        if not target.exists():
            findings.append(Finding("blocking", "references", f"local markdown link does not resolve: {raw}"))


def check_hygiene(root: Path, findings: list[Finding]) -> None:
    forbidden_names = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    forbidden_suffixes = {".zip", ".pyc", ".pyo"}
    sensitive_patterns = re.compile(r"(?i)(secret|credential|password|token|apikey|api_key|private[_-]?key)")
    for path in iter_files(root):
        rel = path.relative_to(root)
        if path.is_symlink():
            findings.append(Finding("blocking", "package", f"symlink is not allowed: {rel}"))
        if any(part in forbidden_names for part in rel.parts):
            findings.append(Finding("material", "package", f"cache or repository artifact should not be packaged: {rel}"))
        if path.suffix in forbidden_suffixes:
            findings.append(Finding("material", "package", f"generated/archive artifact should not be packaged: {rel}"))
        if sensitive_patterns.search(str(rel)):
            findings.append(Finding("blocking", "safety", f"sensitive-looking file path included: {rel}"))


def check_placeholders(root: Path, findings: list[Finding]) -> None:
    for path in iter_files(root):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json"}:
            continue
        text = read_text(path)
        if SCAFFOLD_RE.search(text) and "template" not in path.parts:
            findings.append(Finding("material", "content", f"scaffold marker remains in {path.relative_to(root)}"))


def check_python_scripts(root: Path, findings: list[Finding]) -> None:
    scripts = root / "scripts"
    if not scripts.exists():
        return
    for script in scripts.glob("*.py"):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            findings.append(Finding("blocking", "scripts", f"python script does not compile: {script.name}: {exc.msg}"))


def compare_before_after(before: Path, after: Path, findings: list[Finding]) -> None:
    before_skill = before / "SKILL.md"
    after_skill = after / "SKILL.md"
    if not before_skill.exists() or not after_skill.exists():
        return
    b = read_text(before_skill)
    a = read_text(after_skill)
    b_data: list[Finding] = []
    a_data: list[Finding] = []
    b_front = parse_frontmatter(b, b_data)
    a_front = parse_frontmatter(a, a_data)
    if b_front.get("name") and a_front.get("name") and b_front["name"] != a_front["name"]:
        findings.append(Finding("material", "identity", f"skill name changed from {b_front['name']} to {a_front['name']}"))
    if b_front.get("description") and a_front.get("description"):
        before_words = len(b_front["description"].split())
        after_words = len(a_front["description"].split())
        if after_words < max(15, int(before_words * 0.45)):
            findings.append(Finding("material", "activation", "frontmatter description was sharply shortened; verify activation recall and boundaries"))


def status_from(findings: list[Finding]) -> str:
    if any(f.severity == "blocking" for f in findings):
        return "fail"
    if any(f.severity == "material" for f in findings):
        return "pass-with-warnings"
    return "pass"


def run(target: Path, before: Path | None = None) -> dict[str, object]:
    findings: list[Finding] = []
    if not target.exists() or not target.is_dir():
        findings.append(Finding("blocking", "package", "target does not exist or is not a directory"))
        return {"status": "fail", "findings": [asdict(f) for f in findings]}
    skill = root_skill_md(target, findings)
    if skill is not None:
        text = read_text(skill)
        parse_frontmatter(text, findings)
        check_links(target, text, findings)
    check_hygiene(target, findings)
    check_placeholders(target, findings)
    check_python_scripts(target, findings)
    if before is not None:
        if not before.exists() or not before.is_dir():
            findings.append(Finding("blocking", "evidence", "before path does not exist or is not a directory"))
        else:
            compare_before_after(before, target, findings)
    return {
        "status": status_from(findings),
        "target": str(target),
        "before": str(before) if before else None,
        "findings": [asdict(f) for f in findings],
        "note": "static helper output; semantic gate decision still requires skill review",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run static checks for a candidate skill change.")
    parser.add_argument("--target", required=True, help="after/candidate skill folder")
    parser.add_argument("--before", help="optional before skill folder for shallow comparison")
    parser.add_argument("--json", help="optional JSON report path")
    args = parser.parse_args(argv)
    result = run(Path(args.target).resolve(), Path(args.before).resolve() if args.before else None)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.json:
        Path(args.json).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["status"] in {"pass", "pass-with-warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
