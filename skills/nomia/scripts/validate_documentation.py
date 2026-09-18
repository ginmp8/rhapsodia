#!/usr/bin/env python3
"""Validate local Markdown links in Nomia documentation with normalized relative paths."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from nomia_utils import atomic_write_text

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_DIRS = ("references", "examples")


def normalize_target(raw: str) -> str | None:
    value = raw.strip().strip("<>")
    if not value or value.startswith("#") or "://" in value or value.startswith("mailto:"):
        return None
    value = value.split("#", 1)[0].strip()
    if not value:
        return None
    return value


def markdown_files(root: Path) -> list[Path]:
    files = [root / "SKILL.md"]
    for directory in MARKDOWN_DIRS:
        base = root / directory
        if base.is_dir():
            files.extend(sorted(base.rglob("*.md")))
    return [path for path in files if path.is_file()]


def validate_documentation(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    checked_links = 0
    files = markdown_files(root)
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
    parser = argparse.ArgumentParser(description="Validate local Markdown links in the Nomia package.")
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
