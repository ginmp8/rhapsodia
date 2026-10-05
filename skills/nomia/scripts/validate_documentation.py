#!/usr/bin/env python3
"""Validate Nomia Markdown links plus long-document context-loading previews."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from nomia_utils import atomic_write_text

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
MARKDOWN_DIRS = ("references", "examples")
PREVIEW_HEADINGS = {"at a glance", "summary", "quick reference", "overview"}
NAV_HEADINGS = {"contents", "table of contents", "section map"}


def normalize_target(raw: str) -> str | None:
    value = raw.strip().strip("<>")
    if not value or value.startswith("#") or "://" in value or value.startswith("mailto:"):
        return None
    value = value.split("#", 1)[0].strip()
    if not value:
        return None
    return value


def markdown_files(root: Path) -> list[Path]:
    files = [root / "SKILL.md", root / "CHANGELOG.md"]
    for directory in MARKDOWN_DIRS:
        base = root / directory
        if base.is_dir():
            files.extend(sorted(base.rglob("*.md")))
    return [path for path in files if path.is_file()]


def _context_preview_files(root: Path) -> list[Path]:
    files = [root / "CHANGELOG.md"]
    refs = root / "references"
    if refs.is_dir():
        files.extend(sorted(refs.rglob("*.md")))
    return [path for path in files if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 100]


def _section_items(lines: list[str], heading: str) -> list[str]:
    start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == f"## {heading}".lower():
            start = index + 1
            break
    if start is None:
        return []
    items: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.startswith("- "):
            items.append(line[2:].strip())
    return items


def _validate_context_preview(path: Path, root: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) <= 100:
        return []
    rel = path.relative_to(root).as_posix()
    top40 = "\n".join(lines[:40])
    lower = top40.lower()
    if "context-preview-exception:" in lower:
        return []
    errors: list[str] = []
    for signal in ("**purpose:**", "**load when:**", "**decision impact:**"):
        if signal not in lower:
            errors.append(f"long Markdown preview is missing {signal} within first 40 lines: {rel}")
    headings_top40 = {match.group(1).strip().lower() for match in H2_RE.finditer(top40)}
    if not (headings_top40 & PREVIEW_HEADINGS):
        errors.append(f"long Markdown is missing a preview heading within first 40 lines: {rel}")
    nav = headings_top40 & NAV_HEADINGS
    if not nav:
        errors.append(f"long Markdown is missing Contents/section map within first 40 lines: {rel}")
        return errors
    nav_heading = next(iter(sorted(nav)))
    actual = [match.group(1).strip() for match in H2_RE.finditer("\n".join(lines))]
    material = [heading for heading in actual if heading.lower() not in PREVIEW_HEADINGS | NAV_HEADINGS]
    listed = _section_items(lines[:40], nav_heading)
    if listed != material:
        errors.append(f"long Markdown Contents drift in {rel}: expected {material}, found {listed}")
    return errors


def validate_documentation(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    checked_links = 0
    files = markdown_files(root)
    for preview_file in _context_preview_files(root):
        errors.extend(_validate_context_preview(preview_file, root))
    for source in files:
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw = match.group(1)
            target = normalize_target(raw)
            if target is None:
                continue
            checked_links += 1
            candidate = (source.parent / target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"documentation link escapes skill root: {source.relative_to(root)} -> {raw}")
                continue
            if not candidate.exists():
                errors.append(f"documentation link is missing: {source.relative_to(root)} -> {raw}")
    return {
        "target": str(root),
        "status": "pass" if not errors else "fail",
        "files_checked": len(files),
        "links_checked": checked_links,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Nomia Markdown links and long-document context-loading previews.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate_documentation(Path(args.target))
    if args.json_output:
        output = Path(args.json_output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(output, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"status: {result['status']}")
    print(f"files_checked: {result['files_checked']}")
    print(f"links_checked: {result['links_checked']}")
    for error in result["errors"]:
        print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
