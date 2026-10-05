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
    "references/context-selection-evaluation.md",
    "references/change-sequencing.md",
    "references/risk-and-validation-checklist.md",
    "references/upstream-source.md",
    "references/host-portability.md",
    "references/parallelization-map.md",
    "assets/templates/context-map.md.template",
    "scripts/generate_context_map_skeleton.py",
    "scripts/context_evidence_snapshot.py",
    "scripts/evaluate_context_selection.py",
    "scripts/package_skill.py",
    "evals/activation-scenarios.json",
    "evals/reproducibility-scenarios.json",
    "evals/context-selection-fixtures.json",
    "evals/context-architect-2.1-scenarios.json",
    "examples/example-context-map.md",
]

REQUIRED_SKILL_LINKS = [
    "references/context-map-contract.md",
    "references/evidence-and-scope-control.md",
    "references/dependency-tracing.md",
    "references/context-selection-evaluation.md",
    "references/change-sequencing.md",
    "references/risk-and-validation-checklist.md",
    "references/host-portability.md",
    "references/parallelization-map.md",
    "references/upstream-source.md",
    "scripts/context_evidence_snapshot.py",
    "scripts/evaluate_context_selection.py",
]

TOP100_REQUIRED_MARKERS = [
    "## Mission and activation boundary",
    "## Critical invariants",
    "## Modes",
    "## Evidence tiers",
    "## Direct branch map",
    "## Quick-start workflow",
    "## Hard stops before editing",
    "10. Render using the context-map contract",
]

TOP100_REQUIRED_LINKS = [
    "references/evidence-and-scope-control.md",
    "references/dependency-tracing.md",
    "references/context-map-contract.md",
    "references/change-sequencing.md",
    "references/risk-and-validation-checklist.md",
    "references/context-selection-evaluation.md",
    "references/parallelization-map.md",
    "references/host-portability.md",
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


def material_h2_headings(text: str) -> list[str]:
    headings: list[str] = []
    fence: str | None = None
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r"^##\s+(.+?)\s*$", raw_line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def contents_entries(text: str) -> list[str]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == "## Contents"), None)
    if start is None:
        return []
    entries: list[str] = []
    for raw_line in lines[start + 1 :]:
        if raw_line.startswith("## "):
            break
        stripped = raw_line.strip()
        if stripped.startswith("- "):
            entry = stripped[2:].strip().strip("`").strip()
            if entry:
                entries.append(entry)
    return entries


def validate_top100_and_reference_loading(root: Path, skill_text: str, diags: list[dict[str, Any]]) -> None:
    lines = skill_text.splitlines()
    if len(lines) <= 100:
        return
    top100 = "\n".join(lines[:100])
    for marker in TOP100_REQUIRED_MARKERS:
        if marker not in top100:
            add(diags, "top100_required_marker_missing", "SKILL.md", marker)
    for link in TOP100_REQUIRED_LINKS:
        if link not in top100:
            add(diags, "top100_required_link_missing", "SKILL.md", link)

    for mode in ["context-map-only", "implementation-plan", "review-impact", "apply-after-approved-map"]:
        if mode not in top100:
            add(diags, "top100_mode_missing", "SKILL.md", mode)
    for tier in ["focused", "standard", "extended"]:
        if f"`{tier}`" not in top100:
            add(diags, "top100_evidence_tier_missing", "SKILL.md", tier)

    references_dir = root / "references"
    if references_dir.is_dir():
        for ref in sorted(references_dir.glob("*.md")):
            rel = ref.relative_to(root).as_posix()
            if rel not in skill_text:
                add(diags, "reference_not_directly_reachable", "SKILL.md", rel)


def validate_long_markdown_previews(root: Path, diags: list[dict[str, Any]]) -> None:
    required_preview_markers = ["## At a Glance", "**Purpose:**", "**Load when:**", "**Decision impact:**", "## Contents"]
    generic_preview_fragments = ["Read this file when the active workflow needs", "Primary topics:"]

    for path in sorted(root.rglob("*.md")):
        if path.name == "SKILL.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        if len(lines) <= 100:
            continue
        rel = path.relative_to(root).as_posix()
        first40 = "\n".join(lines[:40])
        exception = re.search(r"<!--\s*context-preview-exception:\s*(generated|vendor|unsafe-to-rewrite)\s*-->", first40)
        if exception:
            add(diags, "long_markdown_preview_exception", rel, exception.group(1), severity="warning")
            continue
        for marker in required_preview_markers:
            if marker not in first40:
                add(diags, "long_markdown_preview_missing", rel, marker)
        for fragment in generic_preview_fragments:
            if fragment in first40:
                add(diags, "long_markdown_preview_too_generic", rel, fragment)

        actual = [h for h in material_h2_headings(text) if h not in {"At a Glance", "Contents"}]
        listed = contents_entries(text)
        if listed != actual:
            add(
                diags,
                "long_markdown_contents_mismatch",
                rel,
                f"contents={listed!r}; headings={actual!r}",
            )


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
        if path.name == "context-selection-fixtures.json":
            if not isinstance(payload, dict) or payload.get("schema_version") != "1.0" or not isinstance(payload.get("cases"), list) or not payload.get("cases"):
                add(diags, "context_fixture_schema_invalid", path.relative_to(root).as_posix(), "expected schema_version 1.0 with non-empty cases array")
                continue
            ids = [case.get("id") for case in payload["cases"] if isinstance(case, dict)]
            if len(ids) != len(payload["cases"]) or any(not x for x in ids) or len(ids) != len(set(ids)):
                add(diags, "context_fixture_ids_invalid", path.relative_to(root).as_posix(), "case ids must be present and unique")
            if not any(isinstance(case, dict) and not case.get("expected_relevant") for case in payload["cases"]):
                add(diags, "context_fixture_no_gold_missing", path.relative_to(root).as_posix(), "at least one no-gold case is required")
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
                if "use for" not in description or "do not use" not in description:
                    add(diags, "description_boundary_missing", "SKILL.md", "description must include explicit use and non-use boundaries")
            validate_top100_and_reference_loading(root, skill_text, diags)
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
        if contract.is_file() and "Contract version: **2.1**" not in contract.read_text(encoding="utf-8"):
            add(diags, "context_contract_version_missing", contract.relative_to(root).as_posix(), "expected context-map contract version 2.1")

        validate_markdown_links(root, diags)
        validate_long_markdown_previews(root, diags)
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
