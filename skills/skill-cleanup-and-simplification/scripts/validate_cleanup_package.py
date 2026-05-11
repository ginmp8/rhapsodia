#!/usr/bin/env python3
"""Post-cleanup structural validator for skill packages."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

CACHE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox", ".cache"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".7z", ".rar"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTO" + r"DO\b", re.I),
    re.compile(r"\bREPLACE ME\b", re.I),
    re.compile(r"\[TO" + r"DO:", re.I),
]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name == "SKILL.md"


def check_skill_root(root: Path, errors: list[str], warnings: list[str]) -> None:
    skill_files = [p for p in root.rglob("SKILL.md") if p.is_file()]
    if len(skill_files) != 1:
        errors.append(f"expected exactly one SKILL.md, found {len(skill_files)}")
        return
    skill_md = skill_files[0]
    if skill_md.parent != root:
        errors.append(f"SKILL.md must be at target root, found {rel(skill_md, root)}")
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        errors.append("SKILL.md missing valid frontmatter block")
        return
    front = match.group(1)
    if not re.search(r"^name:\s*skill-cleanup-and-simplification\s*$", front, re.M):
        warnings.append("frontmatter name does not match expected skill-cleanup-and-simplification")
    if not re.search(r"^description:\s*\S", front, re.M):
        errors.append("frontmatter description is missing or empty")


def check_placeholders(root: Path, errors: list[str], warnings: list[str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or not is_text(path):
            continue
        if path.parts[-2:] and "assets" in path.parts and path.name.endswith(".template"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(text):
                warnings.append(f"placeholder marker in {rel(path, root)}")
                break


def check_package_hygiene(root: Path, errors: list[str], warnings: list[str]) -> None:
    for path in root.rglob("*"):
        parts = set(path.relative_to(root).parts)
        if any(part in CACHE_PARTS for part in parts):
            errors.append(f"cache path present: {rel(path, root)}")
        if path.is_file() and path.suffix.lower() in ARCHIVE_SUFFIXES:
            errors.append(f"archive should not be bundled inside target: {rel(path, root)}")


def check_markdown_links(root: Path, errors: list[str], warnings: list[str]) -> None:
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for link in LINK_PATTERN.findall(text):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = link.split("#", 1)[0].strip()
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                warnings.append(f"external relative link from {rel(path, root)}: {link}")
                continue
            if not candidate.exists():
                errors.append(f"broken local link in {rel(path, root)}: {link}")


def check_python_scripts(root: Path, errors: list[str], warnings: list[str]) -> None:
    for path in root.rglob("*.py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"python syntax error in {rel(path, root)}: {exc}")


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    check_skill_root(root, errors, warnings)
    check_placeholders(root, errors, warnings)
    check_package_hygiene(root, errors, warnings)
    check_markdown_links(root, errors, warnings)
    check_python_scripts(root, errors, warnings)
    return {
        "target": str(root),
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cleanup package structure.")
    parser.add_argument("--target", required=True, help="Target skill folder.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--allow-warnings", action="store_true", help="Return success when only warnings exist.")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"target is not a directory: {root}")

    report = validate(root)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
        print(f"wrote validation: {output}")
    else:
        print(payload)

    if report["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
