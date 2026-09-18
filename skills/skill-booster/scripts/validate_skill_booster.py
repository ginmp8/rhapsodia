#!/usr/bin/env python3
"""Dependency-free structural validator for Agent Skills-compatible packages."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

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
TOP_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def frontmatter_text(skill_md: Path) -> tuple[str | None, list[str]]:
    text = read_text(skill_md).replace("\r\n", "\n")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not match:
        return None, ["missing or invalid yaml frontmatter"]
    return match.group(1), []


def decode_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in {"'", '"'} and value[-1] == value[0]:
        try:
            decoded = ast.literal_eval(value)
            return str(decoded)
        except Exception:
            return value[1:-1]
    return value


def parse_top_level_scalars(raw: str) -> dict[str, str]:
    """Parse the top-level scalar subset needed by the open Agent Skills spec.

    This intentionally avoids a PyYAML dependency. Nested mappings such as metadata are
    ignored because structural validation only needs top-level scalar fields.
    """
    lines = raw.replace("\r\n", "\n").splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or line.lstrip().startswith("#") or line[:1].isspace():
            i += 1
            continue
        match = TOP_KEY_RE.match(line)
        if not match:
            i += 1
            continue
        key = match.group(1)
        value = (match.group(2) or "").strip()
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            folded = value.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt and not nxt[:1].isspace() and TOP_KEY_RE.match(nxt):
                    break
                block.append(nxt.lstrip())
                i += 1
            data[key] = (" " if folded else "\n").join(block).strip()
            continue
        data[key] = decode_scalar(value)
        i += 1
    return data


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, str], list[str]]:
    raw, errors = frontmatter_text(skill_md)
    if raw is None:
        return {}, errors
    data = parse_top_level_scalars(raw)
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    compatibility = str(data.get("compatibility", "")).strip()
    if not name:
        errors.append("frontmatter.name is required")
    else:
        if len(name) > 64:
            errors.append("frontmatter.name exceeds 64 characters")
        if not NAME_RE.fullmatch(name):
            errors.append("frontmatter.name must be lowercase hyphen-case")
        if name != skill_md.parent.name:
            errors.append(f"frontmatter.name must match parent directory name: {skill_md.parent.name}")
    if not description:
        errors.append("frontmatter.description is required")
    elif len(description) > 1024:
        errors.append("frontmatter.description exceeds 1024 characters")
    if compatibility and len(compatibility) > 500:
        errors.append("frontmatter.compatibility exceeds 500 characters")
    return data, errors


def find_skill_roots(root: Path) -> list[Path]:
    return [p for p in root.rglob("SKILL.md") if not any(part in FORBIDDEN_PACKAGE_PARTS for part in p.relative_to(root).parts)]


def check_links(root: Path) -> list[str]:
    errors: list[str] = []
    resolved_root = root.resolve()
    for md in root.rglob("*.md"):
        if any(part in FORBIDDEN_PACKAGE_PARTS for part in md.relative_to(root).parts):
            continue
        for target in LINK_RE.findall(read_text(md)):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            link_path = target.split("#", 1)[0]
            if not link_path:
                continue
            resolved = (md.parent / link_path).resolve()
            try:
                resolved.relative_to(resolved_root)
            except ValueError:
                errors.append(f"local link leaves package: {md.relative_to(root)} -> {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken local link: {md.relative_to(root)} -> {target}")
    return errors


def diagnostic_from_message(message: str, severity: str) -> dict:
    lower = message.lower()
    code = "VALIDATION_WARNING" if severity == "warning" else "VALIDATION_ERROR"
    subject = "package"
    fixes = ["inspect the reported evidence and repair the target package"]

    mapping = [
        ("not a directory", "TARGET_NOT_DIRECTORY", "target", "provide an existing skill directory"),
        ("expected exactly one skill.md", "SKILL_ROOT_COUNT", "SKILL.md", "ensure the target contains exactly one root SKILL.md"),
        ("frontmatter.name must match", "SKILL_NAME_DIRECTORY_MISMATCH", "frontmatter.name", "make SKILL.md name match its parent skill directory"),
        ("frontmatter", "FRONTMATTER_INVALID", "SKILL.md frontmatter", "repair Agent Skills-compatible YAML frontmatter"),
        ("description may be too short", "ACTIVATION_DESCRIPTION_SHORT", "frontmatter.description", "add specific activation and non-activation context"),
        ("should visibly include", "CONTROL_PLANE_SECTION_MISSING", "SKILL.md", "add the missing control-plane section"),
        ("forbidden generated or control path", "FORBIDDEN_PATH", "package tree", "remove generated/control artifacts from the target package"),
        ("bytecode must not be packaged", "BYTECODE_PRESENT", "package tree", "remove bytecode/cache artifacts"),
        ("scaffold marker found", "SCAFFOLD_MARKER", "package content", "replace or remove scaffold/example content"),
        ("local link leaves package", "LOCAL_LINK_ESCAPE", "markdown link", "use a package-local link or external URL"),
        ("broken local link", "LOCAL_LINK_BROKEN", "markdown link", "repair or remove the broken package-local link"),
    ]
    for needle, mapped_code, mapped_subject, fix in mapping:
        if needle in lower:
            code, subject, fixes = mapped_code, mapped_subject, [fix]
            break

    return {
        "code": code,
        "severity": severity,
        "subject": subject,
        "evidence": message,
        "supported_fixes": fixes,
    }


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    files: list[str] = []
    fm: dict[str, str] = {}

    if not root.exists() or not root.is_dir():
        message = f"not a directory: {root}"
        return {
            "status": "fail",
            "errors": [message],
            "warnings": [],
            "diagnostics": [diagnostic_from_message(message, "error")],
            "files": [],
            "frontmatter_parser": "portable-minimal",
        }

    skill_roots = find_skill_roots(root)
    if len(skill_roots) != 1:
        errors.append(f"expected exactly one SKILL.md, found {len(skill_roots)}")
    else:
        skill_md = skill_roots[0]
        fm, fm_errors = parse_frontmatter(skill_md)
        errors.extend(fm_errors)
        description = str(fm.get("description", "")).strip()
        if description and len(description) < 80:
            warnings.append("description may be too short for accurate activation")
        body = read_text(skill_md).lower()
        for term in ["workflow", "output contract", "stop condition"]:
            if term not in body:
                warnings.append(f"SKILL.md should visibly include {term}")

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in FORBIDDEN_PACKAGE_PARTS for part in rel.parts):
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
    unique_errors = sorted(set(errors))
    unique_warnings = sorted(set(warnings))
    diagnostics = [diagnostic_from_message(message, "error") for message in unique_errors]
    diagnostics.extend(diagnostic_from_message(message, "warning") for message in unique_warnings)
    return {
        "status": "pass" if not unique_errors else "fail",
        "errors": unique_errors,
        "warnings": unique_warnings,
        "diagnostics": diagnostics,
        "files": sorted(files),
        "frontmatter_parser": "portable-minimal",
        "frontmatter": {k: fm[k] for k in ("name", "description", "compatibility") if k in fm},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Agent Skills-compatible package without third-party dependencies.")
    parser.add_argument("--target", required=True, help="Skill folder to validate")
    parser.add_argument("--json", dest="json_output", help="Optional JSON output path")
    args = parser.parse_args()

    report = validate(Path(args.target))
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json_output:
        Path(args.json_output).write_text(text + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
