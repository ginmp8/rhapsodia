#!/usr/bin/env python3
"""Validate the MAGIA skill folder and optional packaged zip artifact."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from validate_boundary import collect_errors as collect_boundary_errors
from validate_instruction_contract import collect_errors as collect_instruction_contract_errors
from validate_ecosystem_handoff_contract import collect_errors as collect_ecosystem_handoff_errors
from validate_priority_contract import collect_errors as collect_priority_errors
from validate_ecosystem_compatibility import collect_errors as collect_compatibility_errors
from validate_planning_handoff_contract import collect_errors as collect_planning_handoff_errors
from security_scan import scan_bytes, scan_paths
from package_policy import (
    EXCLUDED_DIR_NAMES,
    EXCLUDED_FILE_NAMES,
    SECRET_NAME_RE,
    blocked_zip_path,
    is_sensitive_name,
    iter_package_candidates,
)

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml", ".template"}
SCAFFOLD_RE = re.compile(r"(\[" + "TO" + "DO" + r"\b|\b" + "TO" + "DO" + r"\s*:|replace with " + "actual|this is a " + "placeholder)", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_PATH_RE = re.compile(r"`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`")




def scan_package_candidates(target: Path) -> list[str]:
    candidates, _ = iter_package_candidates(target)
    errors = [
        f"secret-like file name is not allowed in skill package: {path.relative_to(target).as_posix()}"
        for path in candidates
        if is_sensitive_name(path.name)
    ]
    errors.extend(scan_paths(candidates, target))
    return errors

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
    skill_resource_prefixes = ("agents/", "assets/", "evals/", "examples/", "references/", "scripts/")
    for match in MARKDOWN_LINK_RE.finditer(text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    for match in INLINE_PATH_RE.finditer(text):
        ref = normalize_ref(match.group(1))
        if ref and ref.startswith(skill_resource_prefixes):
            refs.add(ref)
    return sorted(refs)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


ALLOWED_EVAL_SCENARIO_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
REQUIRED_EVAL_SCENARIO_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
REQUIRED_EVAL_FIELDS = {"id", "type", "category", "prompt", "expected_behavior", "acceptance_criteria"}


def validate_shared_artifact_boundaries(target: Path) -> list[str]:
    errors: list[str] = []
    planning_templates = {
        "spec-catalog.yaml.template",
        "manifest.yaml.template",
        "tasks.md.template",
        "notes.md.template",
        "validation.md.template",
    }
    templates_dir = target / "assets" / "templates"
    for template in planning_templates:
        if (templates_dir / template).exists():
            errors.append(f"MAGIA must not carry MAGO-owned planning template: assets/templates/{template}")

    update_script = target / "scripts" / "update_template_lists.py"
    if update_script.exists():
        script_text = read_text(update_script)
        forbidden_support = (
            '"manifest.yaml": {',
            '"spec-catalog.yaml": {',
            '"board_status": FieldRule',
            '"specs": ListRule',
            '"traceability.supporting_discovery_files": ListRule',
        )
        for term in forbidden_support:
            if term in script_text:
                errors.append(f"update_template_lists.py still supports MAGO-owned planning update path: {term}")
    return errors


def validate_eval_scenarios(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing eval scenario suite: {path.name}"]
    try:
        payload = json.loads(read_text(path))
    except Exception as exc:  # noqa: BLE001
        return [f"eval scenario suite is invalid JSON: {exc}"]
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return ["eval scenario suite must contain a non-empty scenarios array"]
    seen: set[str] = set()
    type_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"eval scenario at index {index} is not an object")
            continue
        missing = REQUIRED_EVAL_FIELDS - set(scenario)
        sid = scenario.get("id") or f"index {index}"
        if missing:
            errors.append(f"eval scenario {sid} missing fields: {sorted(missing)}")
        if scenario.get("id") in seen:
            errors.append(f"duplicate eval scenario id: {scenario.get('id')}")
        if scenario.get("id"):
            seen.add(scenario["id"])
        stype = scenario.get("type")
        category = scenario.get("category")
        if stype not in ALLOWED_EVAL_SCENARIO_TYPES:
            errors.append(f"eval scenario {sid} has invalid type: {stype}")
        else:
            type_counts[stype] = type_counts.get(stype, 0) + 1
        if category not in ALLOWED_EVAL_SCENARIO_TYPES:
            errors.append(f"eval scenario {sid} has invalid category: {category}")
        else:
            category_counts[category] = category_counts.get(category, 0) + 1
        if stype and category and stype != category:
            errors.append(f"eval scenario {sid} type/category mismatch: {stype} != {category}")
        criteria = scenario.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
            errors.append(f"eval scenario {sid} must have non-empty string acceptance criteria")
    missing_types = REQUIRED_EVAL_SCENARIO_TYPES - set(type_counts)
    missing_categories = REQUIRED_EVAL_SCENARIO_TYPES - set(category_counts)
    if missing_types:
        errors.append(f"eval scenario suite missing required types: {sorted(missing_types)}")
    if missing_categories:
        errors.append(f"eval scenario suite missing required categories: {sorted(missing_categories)}")
    return errors


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
        "VERSION",
        "CHANGELOG.md",
        "references/canonical-paths.md",
        "references/board-contract.md",
        "references/common-execution.md",
        "references/resource-map.md",
        "references/package-delivery.md",
        "references/ecosystem-handoff-contract.md",
        "references/ecosystem-handoff-contract.json",
        "references/ecosystem-compatibility.md",
        "references/ecosystem-compatibility.json",
        "references/priority-contract.json",
        "references/priority-contract.md",
        "references/priority-contract.md",
        "references/priority-contract.json",
        "references/ecosystem-compatibility.json",
        "references/ecosystem-compatibility.md",
        "references/modes/adhoc.md",
        "references/modes/ralph.md",
        "references/artifacts/execution-records.md",
        "references/artifacts/execution-evidence.md",
        "references/validation-and-closure.md",
        "assets/templates/implementation-notes.md.template",
        "assets/templates/validation-evidence.md.template",
        "assets/templates/technical-gap-note.md.template",
        "examples/activation-scenarios.json",
        "evals/activation-scenarios.json",
        "scripts/board_contract.py",
        "scripts/validate_board_contract.py",
        "scripts/planning_traceability.py",
        "scripts/validate_execution_readiness.py",
        "scripts/validate_instruction_contract.py",
        "scripts/ecosystem_handoff.py",
        "scripts/validate_ecosystem_handoff_contract.py",
        "scripts/run_ecosystem_flow_harness.py",
        "scripts/validate_ecosystem_compatibility.py",
        "scripts/validate_priority_contract.py",
        "scripts/validate_priority_contract.py",
        "scripts/validate_ecosystem_compatibility.py",
        "scripts/run_ecosystem_flow_harness.py",
        "scripts/package_policy.py",
        "scripts/package_skill.py",
        "scripts/validate_skill_package.py",
    ]
    for required in required_paths:
        if not (target / required).exists():
            errors.append(f"missing required package resource: {required}")
    checks.append("required resources")

    version_path = target / "VERSION"
    if version_path.is_file():
        version = read_text(version_path).strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            errors.append(f"VERSION must contain semantic version X.Y.Z, got `{version}`")
    checks.append("release version")

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

    errors.extend(validate_eval_scenarios(target / "evals" / "activation-scenarios.json"))
    checks.append("eval scenarios")

    errors.extend(validate_shared_artifact_boundaries(target))
    checks.append("shared artifact boundaries")

    errors.extend(collect_instruction_contract_errors())
    checks.append("instruction contract preservation")

    errors.extend(collect_planning_handoff_errors(target))
    checks.append("planning handoff contract")

    errors.extend(collect_ecosystem_handoff_errors(target))
    checks.append("ecosystem handoff contract")

    errors.extend(collect_priority_errors(target))
    checks.append("ecosystem priority contract")

    errors.extend(collect_compatibility_errors(target))
    checks.append("ecosystem compatibility")

    errors.extend(collect_boundary_errors())
    checks.append("runtime independence and ownership boundary")

    errors.extend(scan_package_candidates(target))
    checks.append("sensitive content and symlink scan")

    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "checks": checks}


def zip_required_resources() -> list[str]:
    return [
        "SKILL.md",
        "agents/openai.yaml",
        "VERSION",
        "CHANGELOG.md",
        "references/resource-map.md",
        "references/package-delivery.md",
        "references/ecosystem-handoff-contract.md",
        "references/ecosystem-handoff-contract.json",
        "references/ecosystem-compatibility.md",
        "references/ecosystem-compatibility.json",
        "references/priority-contract.json",
        "references/priority-contract.md",
        "examples/activation-scenarios.json",
        "evals/activation-scenarios.json",
        "scripts/board_contract.py",
        "scripts/validate_board_contract.py",
        "scripts/planning_traceability.py",
        "scripts/validate_execution_readiness.py",
        "scripts/validate_instruction_contract.py",
        "scripts/ecosystem_handoff.py",
        "scripts/validate_ecosystem_handoff_contract.py",
        "scripts/run_ecosystem_flow_harness.py",
        "scripts/validate_ecosystem_compatibility.py",
        "scripts/validate_priority_contract.py",
        "scripts/package_policy.py",
        "scripts/package_skill.py",
        "scripts/validate_skill_package.py",
    ]


def validate_zip(zip_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    if not zip_path.exists():
        return {"status": "fail", "errors": [f"zip does not exist: {zip_path}"], "warnings": warnings, "checks": checks}
    try:
        with zipfile.ZipFile(zip_path) as archive:
            bad = archive.testzip()
            names = sorted(name for name in archive.namelist() if not name.endswith("/"))
            if bad:
                errors.append(f"corrupt zip member: {bad}")
            if not names:
                errors.append("zip has no files")
                return {"status": "fail", "errors": errors, "warnings": warnings, "checks": checks}
            if any("/" not in name for name in names):
                errors.append("zip must not contain loose root-level files; expected one top-level skill directory")
                root = ""
            else:
                top_levels = {name.split("/", 1)[0] for name in names}
                if len(top_levels) != 1:
                    errors.append(f"zip must contain exactly one top-level skill directory, found {sorted(top_levels)}")
                    root = sorted(top_levels)[0] if top_levels else ""
                else:
                    root = next(iter(top_levels))
            normalized_names = {name.split("/", 1)[1] for name in names if "/" in name}
            for name in names:
                normalized = name.lstrip("/")
                if normalized != name or ".." in Path(normalized).parts:
                    errors.append(f"unsafe zip path: {name}")
                rel_parts = Path(name.split("/", 1)[1] if "/" in name else name).parts
                if blocked_zip_path(rel_parts):
                    errors.append(f"blocked path included in zip: {name}")
                if Path(name).name in EXCLUDED_FILE_NAMES or Path(name).name.startswith(".coverage."):
                    errors.append(f"blocked file included in zip: {name}")
                if SECRET_NAME_RE.search(Path(name).name):
                    errors.append(f"secret-like file name included in zip: {name}")
                info = archive.getinfo(name)
                unix_mode = (info.external_attr >> 16) & 0o170000
                if unix_mode == 0o120000:
                    errors.append(f"symlink included in zip: {name}")
                else:
                    errors.extend(scan_bytes(archive.read(name), label=name))
            for required in zip_required_resources():
                if required not in normalized_names:
                    errors.append(f"zip missing required resource: {required}")
            if root and f"{root}/SKILL.md" in names:
                skill_text = archive.read(f"{root}/SKILL.md").decode("utf-8")
                frontmatter, fm_errors = parse_frontmatter(skill_text)
                errors.extend(fm_errors)
                if set(frontmatter) != {"name", "description"}:
                    errors.append(f"archived frontmatter keys must be exactly ['description', 'name'], found {sorted(frontmatter)}")
                if any(value != value.lower() for value in frontmatter.values()):
                    errors.append("archived frontmatter values must be lowercase")
                for ref in referenced_paths(skill_text):
                    ref_prefix = ref.rstrip("/") + "/"
                    if ref not in normalized_names and not any(item.startswith(ref_prefix) for item in normalized_names):
                        errors.append(f"archived SKILL.md reference is missing: {ref}")
    except zipfile.BadZipFile:
        errors.append("zip is not a readable zip file")
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
