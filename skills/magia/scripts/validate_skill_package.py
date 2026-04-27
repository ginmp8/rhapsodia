#!/usr/bin/env python3
"""Validate the MAGIA skill package structure and optional packaged zip."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml", ".template"}
SCAFFOLD_RE = re.compile(r"(\[" + "TO" + "DO" + r"\b|\b" + "TO" + "DO" + r"\s*:|replace with actual|this is a placeholder)", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_PATH_RE = re.compile(r"`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`")
BLOCKED_ZIP_PREFIXES = (".git/", "__pycache__/", "evals/", "benchmark-reports/", "test-results/")
BLOCKED_ZIP_NAMES = {"test-results.json"}
SECRET_NAME_RE = re.compile(r"(secret|credential|private[_-]?key|\.env$|id_rsa|token)", re.IGNORECASE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["SKILL.md must start with YAML frontmatter"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, ["SKILL.md frontmatter is not closed"]
    raw = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    for line in raw:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, errors


def normalize_ref(raw: str) -> str | None:
    ref = raw.strip().split("#", 1)[0].strip()
    if not ref or "://" in ref or ref.startswith("mailto:"):
        return None
    if any(ch.isspace() for ch in ref):
        return None
    return ref


def referenced_paths(text: str) -> list[str]:
    refs: set[str] = set()
    for match in MARKDOWN_LINK_RE.finditer(text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    for match in INLINE_PATH_RE.finditer(text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    return sorted(refs)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def validate_target(target: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    target = target.resolve()

    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        errors.append("missing SKILL.md")
        return {"status": "fail", "errors": errors, "warnings": warnings, "checks": checks}

    text = read_text(skill_md)
    frontmatter, fm_errors = parse_frontmatter(text)
    errors.extend(fm_errors)
    expected_keys = {"name", "description"}
    if set(frontmatter) != expected_keys:
        errors.append(f"frontmatter keys must be exactly {sorted(expected_keys)}, found {sorted(frontmatter)}")
    for key in expected_keys:
        value = frontmatter.get(key, "")
        if not value:
            errors.append(f"frontmatter {key} is required")
        elif value != value.lower():
            errors.append(f"frontmatter {key} must be lowercase")
    if len(frontmatter.get("description", "").split()) < 25:
        errors.append("frontmatter description must be specific enough to trigger reliably")
    checks.append("frontmatter")

    for ref in referenced_paths(text):
        candidate = (target / ref).resolve()
        try:
            candidate.relative_to(target)
        except ValueError:
            errors.append(f"reference escapes skill root: {ref}")
            continue
        if not candidate.exists():
            errors.append(f"missing referenced path: {ref}")
    checks.append("local references")

    required_paths = [
        "agents/openai.yaml",
        "references/canonical-paths.md",
        "references/common-execution.md",
        "references/resource-map.md",
        "references/modes/adhoc.md",
        "references/modes/ralph.md",
        "references/artifacts/execution-records.md",
        "references/artifacts/execution-evidence.md",
        "references/validation-and-closure.md",
        "assets/templates/spec-catalog.yaml.template",
        "assets/templates/manifest.yaml.template",
        "assets/templates/tasks.md.template",
        "assets/templates/notes.md.template",
        "assets/templates/validation.md.template",
        "examples/activation-scenarios.json",
    ]
    for required in required_paths:
        if not (target / required).exists():
            errors.append(f"missing required package resource: {required}")
    checks.append("required resources")

    agent_text = read_text(target / "agents/openai.yaml") if (target / "agents/openai.yaml").exists() else ""
    for token in ["display_name:", "short_description:", "default_prompt:", "allow_implicit_invocation:"]:
        if token not in agent_text:
            errors.append(f"agents/openai.yaml missing {token}")
    checks.append("agent metadata")

    for file_path in sorted(target.rglob("*")):
        if not file_path.is_file() or "__pycache__" in file_path.parts:
            continue
        if file_path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        resource = rel(file_path, target)
        if resource.startswith("assets/templates/"):
            continue
        content = read_text(file_path)
        for idx, line in enumerate(content.splitlines(), start=1):
            if "SCAFFOLD_RE" in line or "PLACE" + "HOLDER" in line:
                continue
            if SCAFFOLD_RE.search(line):
                errors.append(f"placeholder text in {resource}:{idx}")
    checks.append("placeholder scan")

    scripts = sorted((target / "scripts").glob("*.py"))
    if not scripts:
        errors.append("no Python scripts found under scripts/")
    with tempfile.TemporaryDirectory(prefix="magia-compile-") as tmp_dir:
        for script in scripts:
            try:
                cfile = Path(tmp_dir) / (script.name + ".pyc")
                py_compile.compile(str(script), cfile=str(cfile), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"script compile failed for {rel(script, target)}: {exc.msg}")
    checks.append("script compilation")

    try:
        scenarios = json.loads(read_text(target / "examples/activation-scenarios.json"))
        categories = {item.get("category") for item in scenarios}
        expected_categories = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
        if len(scenarios) < 20:
            errors.append("activation scenario suite must contain at least 20 scenarios")
        missing_categories = expected_categories - categories
        if missing_categories:
            errors.append(f"activation scenario suite missing categories: {sorted(missing_categories)}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"activation scenario suite is invalid JSON: {exc}")
    checks.append("activation scenarios")

    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "checks": checks}


def validate_zip(zip_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    if not zip_path.exists():
        return {"status": "fail", "errors": [f"zip does not exist: {zip_path}"], "warnings": warnings, "checks": checks}
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    if "SKILL.md" not in names:
        errors.append("zip must contain root-level SKILL.md")
    if any(name.endswith("/") for name in names):
        warnings.append("zip contains explicit directory entries")
    for name in names:
        normalized = name.lstrip("/")
        if normalized != name or ".." in Path(normalized).parts:
            errors.append(f"unsafe zip path: {name}")
        if normalized in BLOCKED_ZIP_NAMES or normalized.startswith(BLOCKED_ZIP_PREFIXES):
            errors.append(f"blocked path included in zip: {name}")
        if any(part == "__pycache__" for part in Path(normalized).parts):
            errors.append(f"cache path included in zip: {name}")
        if SECRET_NAME_RE.search(Path(normalized).name):
            errors.append(f"secret-like file name included in zip: {name}")
    for required in ["agents/openai.yaml", "references/resource-map.md", "examples/activation-scenarios.json", "scripts/validate_skill_package.py"]:
        if required not in names:
            errors.append(f"zip missing required resource: {required}")
    checks.append("zip structure")
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the MAGIA skill package and optional zip artifact.")
    parser.add_argument("--target", required=True, help="Path to the MAGIA skill root.")
    parser.add_argument("--zip", dest="zip_path", help="Optional packaged skill zip to validate.")
    parser.add_argument("--json-output", help="Optional path for machine-readable validation output.")
    args = parser.parse_args(argv)

    result: dict[str, Any] = {"target": validate_target(Path(args.target))}
    if args.zip_path:
        result["zip"] = validate_zip(Path(args.zip_path))
    statuses = [section["status"] for section in result.values() if isinstance(section, dict)]
    overall = "pass" if statuses and all(status == "pass" for status in statuses) else "fail"
    result["status"] = overall

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status: {overall}")
    for section_name, section in result.items():
        if not isinstance(section, dict) or section_name == "status":
            continue
        print(f"[{section_name}] {section['status']}")
        for check in section.get("checks", []):
            print(f"  check: {check}")
        for warning in section.get("warnings", []):
            print(f"  warning: {warning}")
        for error in section.get("errors", []):
            print(f"  error: {error}")
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
