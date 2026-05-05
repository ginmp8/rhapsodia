#!/usr/bin/env python3
"""Validate skill-booster package structure or preflight a target skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

FORBIDDEN_PACKAGE_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "reports",
    "generated_evidence",
    "generated-evidence",
    "benchmark-results",
    "validation-reports",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
SCAFFOLD_MARKERS = ["TO" + "DO", "[" + "TO" + "DO", "replace with" + " actual", "example" + " asset", "api_" + "reference.md"]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_frontmatter(skill_md: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    text = read_text(skill_md)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}, ["missing or invalid yaml frontmatter"]
    if yaml is None:
        return {}, ["pyyaml is unavailable"]
    try:
        data = yaml.safe_load(match.group(1))
    except Exception as exc:
        return {}, [f"invalid yaml frontmatter: {exc}"]
    if not isinstance(data, dict):
        return {}, ["frontmatter is not a mapping"]
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    if not name:
        errors.append("frontmatter.name is required")
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("frontmatter.name must be lowercase hyphen-case")
    if not description:
        errors.append("frontmatter.description is required")
    elif len(description) > 1024:
        errors.append("frontmatter.description exceeds 1024 characters")
    return data, errors


def find_skill_roots(root: Path) -> list[Path]:
    return [p for p in root.rglob("SKILL.md") if not any(part in FORBIDDEN_PACKAGE_PARTS for part in p.parts)]


def check_links(root: Path) -> list[str]:
    errors: list[str] = []
    for md in root.rglob("*.md"):
        if any(part in FORBIDDEN_PACKAGE_PARTS for part in md.parts):
            continue
        for target in LINK_RE.findall(read_text(md)):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            link_path = target.split("#", 1)[0]
            if not link_path:
                continue
            resolved = (md.parent / link_path).resolve()
            if not str(resolved).startswith(str(root.resolve())):
                errors.append(f"local link leaves package: {md.relative_to(root)} -> {target}")
            elif not resolved.exists():
                errors.append(f"broken local link: {md.relative_to(root)} -> {target}")
    return errors


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    files = []

    if not root.exists() or not root.is_dir():
        return {"status": "fail", "errors": [f"not a directory: {root}"], "warnings": [], "files": []}

    skill_roots = find_skill_roots(root)
    if len(skill_roots) != 1:
        errors.append(f"expected exactly one SKILL.md, found {len(skill_roots)}")
    else:
        fm, fm_errors = parse_frontmatter(skill_roots[0])
        errors.extend(fm_errors)
        description = str(fm.get("description", "")).strip()
        if description and len(description) < 80:
            warnings.append("description may be too short for accurate activation")
        body = read_text(skill_roots[0]).lower()
        for term in ["workflow", "output contract", "stop condition"]:
            if term not in body:
                warnings.append(f"SKILL.md should visibly include {term}")

    if not (root / "agents" / "openai.yaml").exists():
        warnings.append("agents/openai.yaml missing")

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in FORBIDDEN_PACKAGE_PARTS for part in path.parts):
            errors.append(f"forbidden generated or control path found: {rel}")
            continue
        if path.is_file():
            files.append(str(rel))
            if path.suffix in FORBIDDEN_SUFFIXES:
                errors.append(f"bytecode must not be packaged: {rel}")
            if path.suffix.lower() in {".md", ".txt", ".py", ".yaml", ".yml", ".json"}:
                content = read_text(path)
                for marker in SCAFFOLD_MARKERS:
                    if marker.lower() in content.lower() or marker.lower() in str(rel).lower():
                        errors.append(f"scaffold marker found in {rel}: {marker}")
                        break

    errors.extend(check_links(root))
    return {
        "status": "pass" if not errors else "fail",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "files": sorted(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill-booster or preflight a target skill.")
    parser.add_argument("--target", required=True, help="Skill folder to validate")
    parser.add_argument("--json", dest="json_output", help="Optional JSON output path")
    args = parser.parse_args()

    report = validate(Path(args.target))
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    json_output = getattr(args, "json_output")
    if json_output:
        Path(json_output).write_text(text + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
