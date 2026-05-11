#!/usr/bin/env python3
"""Create a simple structural inventory for a skill package.

The output is mechanical evidence only. It does not decide whether the
architecture is good, cohesive, or ready to publish.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

TOP_LEVEL_AREAS = [
    "agents",
    "references",
    "scripts",
    "assets",
    "examples",
    "evals",
]

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_text_file(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            data = f.read(4096)
        if b"\x00" in data:
            return False
        data.decode("utf-8")
        return True
    except Exception:
        return False


def count_lines(path: Path) -> int | None:
    if not is_text_file(path):
        return None
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except Exception:
        return None


def extract_frontmatter(skill_md: Path) -> dict[str, Any]:
    if not skill_md.exists() or not is_text_file(skill_md):
        return {}
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return {"present": False}
    end = text.find("\n---", 4)
    if end == -1:
        return {"present": False, "error": "unterminated frontmatter"}
    raw = text[4:end].strip()
    result: dict[str, Any] = {"present": True, "raw_line_count": len(raw.splitlines())}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def markdown_links(path: Path, root: Path) -> list[dict[str, str]]:
    if path.suffix.lower() != ".md" or not is_text_file(path):
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    links = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if "://" in target or target.startswith("mailto:") or target.startswith("#"):
            kind = "external-or-anchor"
            exists = "not-checked"
        else:
            clean = target.split("#", 1)[0]
            target_path = (path.parent / clean).resolve()
            try:
                target_path.relative_to(root.resolve())
                in_root = True
            except ValueError:
                in_root = False
            kind = "local" if in_root else "outside-root"
            exists = str(target_path.exists())
        links.append({"source": str(path.relative_to(root)), "target": target, "kind": kind, "exists": exists})
    return links


def inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = []
    area_counts = {area: 0 for area in TOP_LEVEL_AREAS}
    links = []
    skill_md_files = []

    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if path.name == "SKILL.md":
            skill_md_files.append(str(rel))
        area = rel.parts[0] if rel.parts else "root"
        if area in area_counts:
            area_counts[area] += 1
        info = {
            "path": str(rel),
            "area": area,
            "suffix": path.suffix,
            "size_bytes": path.stat().st_size,
            "line_count": count_lines(path),
            "sha256": sha256_file(path),
            "is_text": is_text_file(path),
        }
        files.append(info)
        links.extend(markdown_links(path, root))

    skill_md = root / "SKILL.md"
    total_size = sum(item["size_bytes"] for item in files)
    local_links = [link for link in links if link["kind"] == "local"]
    broken_local_links = [link for link in local_links if link["exists"] == "False"]

    return {
        "target": str(root),
        "skill_md_files": skill_md_files,
        "root_skill_md_present": skill_md.exists(),
        "frontmatter": extract_frontmatter(skill_md),
        "file_count": len(files),
        "total_size_bytes": total_size,
        "area_counts": area_counts,
        "files": files,
        "markdown_links": links,
        "broken_local_links": broken_local_links,
        "notes": [
            "inventory is mechanical evidence only",
            "architectural judgment requires reading the package contract and resources",
        ],
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# Skill Package Inventory: {data['target']}",
        "",
        "## Summary",
        "",
        f"- root `SKILL.md` present: {data['root_skill_md_present']}",
        f"- `SKILL.md` files found: {len(data['skill_md_files'])}",
        f"- file count: {data['file_count']}",
        f"- total size bytes: {data['total_size_bytes']}",
        f"- broken local markdown links: {len(data['broken_local_links'])}",
        "",
        "## Area counts",
        "",
    ]
    for area, count in data["area_counts"].items():
        lines.append(f"- {area}: {count}")
    lines.extend(["", "## Files", ""])
    for item in data["files"]:
        line_count = item["line_count"] if item["line_count"] is not None else "binary-or-unreadable"
        lines.append(f"- `{item['path']}` ({item['size_bytes']} bytes, {line_count} lines)")
    if data["broken_local_links"]:
        lines.extend(["", "## Broken local links", ""])
        for link in data["broken_local_links"]:
            lines.append(f"- `{link['source']}` -> `{link['target']}`")
    lines.extend(["", "> This inventory is mechanical evidence only; it is not an architecture verdict."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="inventory a skill package")
    parser.add_argument("--target", required=True, help="path to skill package root")
    parser.add_argument("--json-output", help="optional json output path")
    parser.add_argument("--markdown-output", help="optional markdown output path")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"target is not a directory: {target}")

    data = inventory(target)
    text = json.dumps(data, indent=2, sort_keys=True)
    print(text)

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")

    if args.markdown_output:
        out = Path(args.markdown_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(data), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
