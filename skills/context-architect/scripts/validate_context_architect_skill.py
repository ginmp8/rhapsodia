#!/usr/bin/env python3
"""Validate the context-architect skill package with stable diagnostics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/context-map-contract.md",
    "references/evidence-and-scope-control.md",
    "references/dependency-tracing.md",
    "references/change-sequencing.md",
    "references/risk-and-validation-checklist.md",
    "references/upstream-source.md",
    "assets/templates/context-map.md.template",
    "scripts/generate_context_map_skeleton.py",
    "scripts/context_evidence_snapshot.py",
    "scripts/package_skill.py",
    "evals/activation-scenarios.json",
    "evals/reproducibility-scenarios.json",
    "examples/example-context-map.md",
]

REQUIRED_SKILL_LINKS = [
    "references/context-map-contract.md",
    "references/evidence-and-scope-control.md",
    "references/dependency-tracing.md",
    "references/change-sequencing.md",
    "references/risk-and-validation-checklist.md",
    "scripts/context_evidence_snapshot.py",
]

FORBIDDEN_MARKERS = [
    "[" + "TO" + "DO",
    "TO" + "DO:",
    "example" + "_asset.txt",
    "api" + "_reference.md",
    "scripts/" + "ex" + "ample.py",
]

ALLOWED_SCENARIO_TYPES = {
    "should_activate",
    "should_not_activate",
    "ambiguous",
    "edge_case",
    "regression",
    "adversarial",
    "core_behavior",
    "holdout",
}

REQUIRED_SCENARIO_TYPES = {
    "should_activate",
    "should_not_activate",
    "ambiguous",
    "edge_case",
    "regression",
    "adversarial",
}

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Skill directory to validate.")
    parser.add_argument("--json", dest="json_path", help="Optional JSON report output path.")
    return parser.parse_args()


def add(diags: list[dict[str, Any]], code: str, subject: str, evidence: str, severity: str = "error") -> None:
    diags.append({"code": code, "severity": severity, "subject": subject, "evidence": evidence})


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str | None]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None, "SKILL.md is missing YAML frontmatter"
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            return None, f"invalid frontmatter line: {raw_line}"
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, None


def validate_markdown_links(root: Path, diags: list[dict[str, Any]]) -> None:
    for md in sorted(root.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        for target in LINK_RE.findall(text):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel_target = target.split("#", 1)[0]
            if not rel_target:
                continue
            resolved = (md.parent / rel_target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                add(diags, "local_link_escapes_root", md.relative_to(root).as_posix(), target)
                continue
            if not resolved.exists():
                add(diags, "broken_local_link", md.relative_to(root).as_posix(), target)


def validate_scenarios(root: Path, diags: list[dict[str, Any]]) -> None:
    seen_ids: set[str] = set()
    all_types: set[str] = set()
    for path in sorted((root / "evals").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            add(diags, "invalid_scenario_json", path.relative_to(root).as_posix(), str(exc))
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get("scenarios"), list):
            add(diags, "scenario_schema_invalid", path.relative_to(root).as_posix(), "expected object with scenarios array")
            continue
        if payload.get("status") != "planned":
            add(diags, "scenario_status_not_planned", path.relative_to(root).as_posix(), repr(payload.get("status")))
        for scenario in payload["scenarios"]:
            if not isinstance(scenario, dict):
                add(diags, "scenario_not_object", path.relative_to(root).as_posix(), repr(scenario))
                continue
            missing = [key for key in ["id", "type", "prompt", "expected_behavior"] if not scenario.get(key)]
            if missing:
                add(diags, "scenario_missing_fields", path.relative_to(root).as_posix(), ",".join(missing))
                continue
            scenario_id = scenario["id"]
            scenario_type = scenario["type"]
            if scenario_id in seen_ids:
                add(diags, "duplicate_scenario_id", scenario_id, path.relative_to(root).as_posix())
            seen_ids.add(scenario_id)
            all_types.add(scenario_type)
            if scenario_type not in ALLOWED_SCENARIO_TYPES:
                add(diags, "unsupported_scenario_type", scenario_id, str(scenario_type))
            criteria = scenario.get("acceptance_criteria")
            if criteria is not None and (not isinstance(criteria, list) or not all(isinstance(x, str) and x.strip() for x in criteria)):
                add(diags, "invalid_acceptance_criteria", scenario_id, "acceptance_criteria must be a non-empty string array when present")
    missing_types = sorted(REQUIRED_SCENARIO_TYPES - all_types)
    if missing_types:
        add(diags, "scenario_coverage_missing", "evals", ",".join(missing_types))


def validate_python_sources(root: Path, diags: list[dict[str, Any]]) -> None:
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            add(diags, "python_syntax_error", path.relative_to(root).as_posix(), f"line {exc.lineno}: {exc.msg}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.target).resolve()
    diags: list[dict[str, Any]] = []

    if not root.exists() or not root.is_dir():
        add(diags, "target_missing", str(root), "target directory does not exist")
    else:
        for rel in REQUIRED_FILES:
            if not (root / rel).is_file():
                add(diags, "required_file_missing", rel, "required package file is absent")

        skill_path = root / "SKILL.md"
        if skill_path.is_file():
            skill_text = skill_path.read_text(encoding="utf-8")
            fields, error = parse_frontmatter(skill_text)
            if error:
                add(diags, "frontmatter_invalid", "SKILL.md", error)
            elif fields is not None:
                if set(fields) != {"name", "description"}:
                    add(diags, "frontmatter_fields_invalid", "SKILL.md", f"fields={sorted(fields)}")
                if fields.get("name") != "context-architect":
                    add(diags, "frontmatter_name_invalid", "SKILL.md", repr(fields.get("name")))
                description = fields.get("description", "")
                if description != description.lower():
                    add(diags, "description_not_lowercase", "SKILL.md", "frontmatter description must be lowercase")
                if len(description.split()) < 45:
                    add(diags, "description_too_short", "SKILL.md", f"words={len(description.split())}")
            if len(skill_text.splitlines()) > 500:
                add(diags, "skill_control_plane_too_long", "SKILL.md", f"lines={len(skill_text.splitlines())}", severity="warning")
            for required_link in REQUIRED_SKILL_LINKS:
                if required_link not in skill_text:
                    add(diags, "required_skill_link_missing", "SKILL.md", required_link)

        scan_suffixes = {".md", ".yaml", ".json", ".template", ".py"}
        all_text = "\n".join(
            p.read_text(encoding="utf-8", errors="ignore")
            for p in root.rglob("*")
            if p.is_file() and p.suffix in scan_suffixes
        )
        for marker in FORBIDDEN_MARKERS:
            if marker in all_text:
                add(diags, "scaffold_marker_present", marker, "forbidden scaffold marker remains")

        if len(list(root.rglob("SKILL.md"))) != 1:
            add(diags, "nested_skill_entrypoints", str(root), "package must contain exactly one SKILL.md")

        contract = root / "references/context-map-contract.md"
        if contract.is_file() and "Contract version: **2.0**" not in contract.read_text(encoding="utf-8"):
            add(diags, "context_contract_version_missing", contract.relative_to(root).as_posix(), "expected context-map contract version 2.0")

        validate_markdown_links(root, diags)
        validate_scenarios(root, diags)
        validate_python_sources(root, diags)

    errors = [d for d in diags if d["severity"] == "error"]
    warnings = [d for d in diags if d["severity"] == "warning"]
    report = {
        "status": "fail" if errors else ("warn" if warnings else "pass"),
        "target": str(root),
        "errors": errors,
        "warnings": warnings,
        "diagnostics": diags,
    }
    if args.json_path:
        write_json(Path(args.json_path), report)
    if errors:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    if warnings:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("PASS: context-architect skill package is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
