#!/usr/bin/env python3
"""Post-cleanup structural validator with stable machine-readable diagnostics."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import ast
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

CACHE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox", ".cache", "node_modules", "dist", "build"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".7z", ".rar"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
PLACEHOLDER_PATTERNS = [
    re.compile(r"(?m)^\s*TO" + r"DO(?:\b|:)", re.I),
    re.compile(r"(?m)^\s*REPLACE ME\b", re.I),
    re.compile(r"\[TO" + r"DO:", re.I),
]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name == "SKILL.md"


def add(checks: list[dict[str, Any]], code: str, status: str, subject: str, evidence: dict[str, Any], severity: str, fixes: list[str] | None = None) -> None:
    checks.append({
        "code": code,
        "status": status,
        "subject": subject,
        "evidence": evidence,
        "severity": severity,
        "supported_fixes": fixes or [],
    })


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            data = ("symlink:" + os.readlink(path)).encode("utf-8", errors="surrogateescape")
        elif path.is_file():
            data = path.read_bytes()
        else:
            continue
        h.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0" + data + b"\0")
    return h.hexdigest()


def check_skill_root(root: Path, checks: list[dict[str, Any]]) -> None:
    skill_files = [p for p in root.rglob("SKILL.md") if p.is_file() and not p.is_symlink()]
    if len(skill_files) != 1:
        add(checks, "skill/root-count", "fail", "SKILL.md", {"count": len(skill_files)}, "error", ["keep exactly one root SKILL.md"])
        return
    skill_md = skill_files[0]
    if skill_md.parent != root:
        add(checks, "skill/root-location", "fail", rel(skill_md, root), {}, "error", ["move SKILL.md to target root"])
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        add(checks, "skill/frontmatter", "fail", "SKILL.md", {"frontmatter": "missing"}, "error", ["add valid YAML-style frontmatter"])
        return
    front = match.group(1)
    name = re.search(r"^name:\s*(\S.*?)\s*$", front, re.M)
    desc = re.search(r"^description:\s*(\S.*?)\s*$", front, re.M)
    add(checks, "skill/name", "pass" if name else "fail", "SKILL.md", {"present": bool(name)}, "error" if not name else "info", ["add non-empty name"] if not name else [])
    add(checks, "skill/description", "pass" if desc else "fail", "SKILL.md", {"present": bool(desc)}, "error" if not desc else "info", ["add non-empty description"] if not desc else [])


def check_placeholders(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink() or not path.is_file() or not is_text(path):
            continue
        if "assets" in path.parts and path.name.endswith(".template"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS):
            add(checks, "hygiene/placeholder", "warn", rel(path, root), {}, "warning", ["confirm marker is intentional or replace it"])


def check_package_hygiene(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        relpath = rel(path, root)
        parts = set(path.relative_to(root).parts)
        if any(part in CACHE_PARTS for part in parts) and (path.is_file() or path.is_symlink()):
            add(checks, "hygiene/generated-path", "fail", relpath, {}, "error", ["remove generated/cache/build residue"])
        if path.is_file() and path.suffix.lower() in ARCHIVE_SUFFIXES:
            add(checks, "hygiene/archive", "fail", relpath, {}, "error", ["move package/archive outside target"])
        if path.is_symlink():
            try:
                resolved = path.resolve(strict=False)
                outside = not resolved.is_relative_to(root.resolve(strict=True))
            except (OSError, RuntimeError):
                outside = True
                resolved = path
            add(
                checks,
                "path/symlink-escape" if outside else "path/symlink-present",
                "fail" if outside else "warn",
                relpath,
                {"resolved": str(resolved), "outside_target": outside},
                "error" if outside else "warning",
                ["replace symlink with a real in-package resource or review manually"],
            )


def check_markdown_links(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*.md"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for link in LINK_PATTERN.findall(text):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = link.split("#", 1)[0].strip()
            if not target:
                continue
            candidate = (path.parent / target).resolve(strict=False)
            try:
                candidate.relative_to(root.resolve(strict=True))
            except ValueError:
                add(checks, "link/outside-target", "warn", rel(path, root), {"link": link}, "warning", ["use an explicit external URL or in-package path"])
                continue
            if not candidate.exists():
                add(checks, "link/broken-local", "fail", rel(path, root), {"link": link}, "error", ["restore target or update link"])


def check_python_scripts(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*.py"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            add(checks, "python/syntax", "fail", rel(path, root), {"error": str(exc)}, "error", ["repair Python syntax"])


def validate(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    check_skill_root(root, checks)
    check_placeholders(root, checks)
    check_package_hygiene(root, checks)
    check_markdown_links(root, checks)
    check_python_scripts(root, checks)
    errors = [c for c in checks if c["status"] == "fail"]
    warnings = [c for c in checks if c["status"] == "warn"]
    return {
        "receipt_version": 2,
        "target": str(root),
        "status": "pass" if not errors else "fail",
        "stage": "validation",
        "checks": checks,
        "summary": {"error_count": len(errors), "warning_count": len(warnings), "check_count": len(checks)},
        "hashes": {"target_tree_sha256": tree_hash(root)},
    }


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cleanup package structure.")
    parser.add_argument("--target", required=True, help="Target skill folder.")
    parser.add_argument("--output", help="Optional JSON output path; must be outside target.")
    parser.add_argument("--allow-warnings", action="store_true", help="Compatibility flag; warnings are non-blocking by default.")
    args = parser.parse_args()

    root = Path(args.target).resolve(strict=True)
    if not root.is_dir():
        raise SystemExit(f"target is not a directory: {root}")

    report = validate(root)
    if args.output:
        output = Path(args.output).resolve(strict=False)
        if output == root or root in output.parents:
            raise SystemExit("output must be outside the target package")
        write_json_atomic(output, report)
        print(f"wrote validation: {output}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
