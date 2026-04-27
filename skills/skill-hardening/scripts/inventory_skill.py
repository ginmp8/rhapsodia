#!/usr/bin/env python3
"""Create a deterministic inventory for a ChatGPT skill folder."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml", ".template"}
PLACEHOLDER_PATTERNS = [
    re.compile(r"\[" + "TO" + "DO", re.IGNORECASE),
    re.compile(r"\b" + "TO" + "DO" + r"\s*:", re.IGNORECASE),
    re.compile("replace with " + "actual", re.IGNORECASE),
    re.compile("this is a " + "placeholder", re.IGNORECASE),
]
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_PATH_RE = re.compile(r"`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`")


@dataclass
class SkillInventory:
    target_path: str
    skill_name: str | None
    description: str | None
    skill_md_exists: bool
    skill_md_lines: int
    top_level_dirs: list[str]
    files: list[dict[str, Any]]
    references: list[str]
    scripts: list[str]
    templates: list[str]
    assets: list[str]
    agents: list[str]
    examples: list[str]
    referenced_paths: list[str]
    missing_referenced_paths: list[str]
    unreferenced_resources: list[str]
    placeholder_hits: list[dict[str, Any]]
    has_output_contract: bool
    has_validation: bool
    has_mode_matrix: bool
    has_stop_conditions: bool


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""
    except Exception:
        return ""


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    current_key: str | None = None
    for line in raw:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip().strip('"').strip("'")
        elif current_key:
            data[current_key] += " " + line.strip().strip('"').strip("'")
    return data


def normalize_ref(raw: str) -> str | None:
    ref = raw.strip().split("#", 1)[0].strip()
    if not ref or "://" in ref or ref.startswith("mailto:"):
        return None
    if any(ch.isspace() for ch in ref):
        return None
    return ref


def extract_referenced_paths(skill_text: str) -> list[str]:
    refs: set[str] = set()
    for match in MARKDOWN_LINK_RE.finditer(skill_text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    for match in INLINE_PATH_RE.finditer(skill_text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    return sorted(refs)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def classify_resources(root: Path) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    refs: list[str] = []
    scripts: list[str] = []
    templates: list[str] = []
    assets: list[str] = []
    agents: list[str] = []
    examples: list[str] = []
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        if "__pycache__" in file_path.parts:
            continue
        r = rel(file_path, root)
        if r.startswith("references/"):
            refs.append(r)
        elif r.startswith("scripts/"):
            scripts.append(r)
        elif r.startswith("assets/templates/"):
            templates.append(r)
            assets.append(r)
        elif r.startswith("assets/"):
            assets.append(r)
        elif r.startswith("agents/"):
            agents.append(r)
        elif r.startswith("examples/"):
            examples.append(r)
    return refs, scripts, templates, assets, agents, examples


def scan_files(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    files: list[dict[str, Any]] = []
    placeholder_hits: list[dict[str, Any]] = []
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        if "__pycache__" in file_path.parts:
            continue
        r = rel(file_path, root)
        try:
            size = file_path.stat().st_size
        except OSError:
            size = 0
        text = read_text(file_path) if file_path.suffix.lower() in TEXT_SUFFIXES else ""
        lines = text.count("\n") + (1 if text else 0)
        files.append({"path": r, "size_bytes": size, "lines": lines, "suffix": file_path.suffix.lower()})
        if text and not r.startswith("assets/templates/"):
            for idx, line in enumerate(text.splitlines(), start=1):
                if "re.compile" in line and "PLACEHOLDER" not in line:
                    continue
                if any(pattern.search(line) for pattern in PLACEHOLDER_PATTERNS):
                    placeholder_hits.append({"path": r, "line": idx, "text": line.strip()[:160]})
    return files, placeholder_hits


def inventory(root: Path) -> SkillInventory:
    root = root.resolve()
    skill_md = root / "SKILL.md"
    skill_text = read_text(skill_md) if skill_md.exists() else ""
    frontmatter = parse_frontmatter(skill_text)
    referenced_paths = extract_referenced_paths(skill_text)
    references, scripts, templates, assets, agents, examples = classify_resources(root)
    files, placeholder_hits = scan_files(root)

    missing: list[str] = []
    for ref in referenced_paths:
        candidate = (root / ref).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            missing.append(ref)
            continue
        if not candidate.exists():
            missing.append(ref)

    resource_files = set(references + scripts + assets + agents + examples)
    referenced_exact = set(referenced_paths)
    referenced_prefixes = {p.rstrip("/") for p in referenced_paths}
    unreferenced: list[str] = []
    for resource in sorted(resource_files):
        if resource.startswith("agents/"):
            continue
        if resource in referenced_exact:
            continue
        if any(resource.startswith(prefix + "/") for prefix in referenced_prefixes):
            continue
        unreferenced.append(resource)

    top_level_dirs = sorted([p.name for p in root.iterdir() if p.is_dir()]) if root.exists() else []
    lower_text = skill_text.lower()
    return SkillInventory(
        target_path=str(root),
        skill_name=frontmatter.get("name"),
        description=frontmatter.get("description"),
        skill_md_exists=skill_md.exists(),
        skill_md_lines=skill_text.count("\n") + (1 if skill_text else 0),
        top_level_dirs=top_level_dirs,
        files=files,
        references=references,
        scripts=scripts,
        templates=templates,
        assets=assets,
        agents=agents,
        examples=examples,
        referenced_paths=referenced_paths,
        missing_referenced_paths=sorted(set(missing)),
        unreferenced_resources=unreferenced,
        placeholder_hits=placeholder_hits,
        has_output_contract="output contract" in lower_text or "required output" in lower_text,
        has_validation="validation" in lower_text or "validate" in lower_text or "acceptance" in lower_text,
        has_mode_matrix="mode" in lower_text and "|" in skill_text and "required" in lower_text,
        has_stop_conditions="stop condition" in lower_text or "blocker" in lower_text,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory a ChatGPT skill folder.")
    parser.add_argument("--target", required=True, help="Path to the target skill folder.")
    parser.add_argument("--output", help="Optional path for inventory JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        print(f"ERROR: target is not a directory: {target}", file=sys.stderr)
        return 2

    data = asdict(inventory(target))
    payload = json.dumps(data, indent=2 if args.pretty else None, sort_keys=True)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
