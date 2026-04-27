#!/usr/bin/env python3
"""Inventory a ChatGPT or Agent skill package for skill-harness runs."""
import argparse
import json
import re
from pathlib import Path

TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".js", ".ts", ".sh", ".template"}
IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}
IGNORE_SUFFIXES = {".pyc", ".pyo", ".zip"}
def scaffold_marker_patterns():
    """Return regex patterns for unresolved scaffold markers without embedding marker tokens in source."""
    return [
        r"\[" + "TO" + "DO",
        "TO" + "DO:",
        "T" + "BD:",
        "FI" + "XME",
        "REPLACE" + "_ME",
        r"example" + r"\.py",
        r"api" + r"_reference\.md",
        r"example" + r"_asset\.txt",
    ]


PLACEHOLDER_PATTERNS = scaffold_marker_patterns()
REFERENCE_RE = re.compile(r"`([^`]+\.(?:md|py|json|yaml|yml|template|sh|js|ts))`|\(([^)]+\.(?:md|py|json|yaml|yml|template|sh|js|ts))\)")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}
    match = re.match(r"^---\n(.*?)\n---", content, re.S)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def is_ignored(path, target):
    rel = path.relative_to(target)
    parts = set(rel.parts)
    if parts & IGNORE_DIRS:
        return True
    if path.suffix.lower() in IGNORE_SUFFIXES:
        return True
    return False


def iter_files(target):
    for path in sorted(target.rglob("*")) if target.exists() else []:
        if not path.is_file():
            continue
        if is_ignored(path, target):
            continue
        yield path


def should_skip_placeholder_scan(line):
    marker_names = ("PLACE" + "HOLDER_PATTERNS", "UNRESOLVED" + "_MARKERS")
    return any(marker in line for marker in marker_names)


def collect_references(text):
    references = set()
    for match in REFERENCE_RE.finditer(text):
        ref = match.group(1) or match.group(2)
        if ref and not ref.startswith(("http://", "https://", "/")):
            references.add(ref)
    return references


def inventory(target):
    target = Path(target).resolve()
    skill_files = [p for p in target.rglob("SKILL.md") if not is_ignored(p, target)] if target.exists() else []
    files = []
    placeholders = []
    referenced_paths = set()

    for path in iter_files(target):
        rel = path.relative_to(target).as_posix()
        stat = path.stat()
        item = {"path": rel, "size_bytes": stat.st_size, "suffix": path.suffix.lower()}
        if path.suffix.lower() in TEXT_EXTS:
            text = read_text(path)
            item["lines"] = text.count("\n") + 1 if text else 0
            for lineno, line in enumerate(text.splitlines(), start=1):
                if should_skip_placeholder_scan(line):
                    continue
                for pattern in PLACEHOLDER_PATTERNS:
                    if re.search(pattern, line, re.I):
                        placeholders.append({"path": rel, "line": lineno, "pattern": pattern})
            referenced_paths.update(collect_references(text))
        files.append(item)

    skill_md = target / "SKILL.md"
    skill_content = read_text(skill_md) if skill_md.exists() else ""
    frontmatter = parse_frontmatter(skill_content)

    top_dirs = {
        p.name: p.exists() and p.is_dir()
        for p in [target / "agents", target / "references", target / "scripts", target / "assets", target / "examples", target / "evals"]
    }
    missing_references = []
    for ref in sorted(referenced_paths):
        clean = ref.lstrip("./")
        if not (target / clean).exists():
            missing_references.append(clean)

    return {
        "target": str(target),
        "exists": target.exists(),
        "skill_md_count": len(skill_files),
        "frontmatter": frontmatter,
        "top_dirs": top_dirs,
        "file_count": len(files),
        "files": files,
        "placeholders": placeholders,
        "referenced_paths": sorted(referenced_paths),
        "missing_references": missing_references,
    }


def main():
    parser = argparse.ArgumentParser(description="Inventory a ChatGPT or Agent skill package.")
    parser.add_argument("--target", required=True, help="Path to target skill folder")
    parser.add_argument("--output", help="Path to write JSON inventory")
    args = parser.parse_args()
    data = inventory(args.target)
    payload = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
