#!/usr/bin/env python3
"""Validate nomia skill package structure before packaging."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from nomia_utils import atomic_write_text, sensitive_package_reason

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml", ".template"}
EXPECTED_FRONTMATTER_KEYS = ["name", "description"]
REQUIRED_DIRS = ["agents", "references", "references/modes", "references/artifacts", "assets/templates", "scripts", "examples/golden", "evals", "tests"]
REQUIRED_FILES = [
    "SKILL.md",
    "VERSION",
    "CHANGELOG.md",
    "requirements.txt",
    "agents/openai.yaml",
    "references/canonical-paths.md",
    "references/common-governance.md",
    "references/contracts.md",
    "references/roadmap-to-mago-contract.md",
    "references/activation-and-evaluation.md",
    "references/package-validation.md",
    "references/priority-contract.md",
    "references/ecosystem-handoff-contract.md",
    "references/ecosystem-handoff-contract.json",
    "references/ecosystem-compatibility.json",
    "references/ecosystem-compatibility.md",
    "references/priority-contract.json",
    "references/assurance-contract.json",
    "references/assurance-and-release.md",
    "references/modes/delivery.md",
    "references/modes/roadmap.md",
    "references/modes/rfc.md",
    "references/modes/governance-decision.md",
    "references/modes/reporting.md",
    "references/modes/validation.md",
    "references/modes/governance-adapt.md",
    "references/governance-profiles-and-lifecycle.md",
    "references/state-risk-and-handoffs.md",
    "references/canonical-governance-and-projections.md",
    "references/guided-intake-and-discovery.md",
    "references/artifacts/delivery.md",
    "references/artifacts/roadmap.md",
    "references/artifacts/rfc.md",
    "references/artifacts/governance-decision.md",
    "references/artifacts/reporting.md",
    "scripts/validate_artifact.py",
    "scripts/validate_board_paths.py",
    "scripts/write_artifact_scaffold.py",
    "scripts/update_template_lists.py",
    "scripts/validate_skill_package.py",
    "scripts/validate_priority_contract.py",
    "scripts/validate_activation_scenarios.py",
    "scripts/validate_golden_examples.py",
    "scripts/validate_governance_scenarios.py",
    "scripts/governance_contract.py",
    "scripts/ecosystem_handoff.py",
    "scripts/validate_ecosystem_handoff_contract.py",
    "scripts/validate_ecosystem_compatibility.py",
    "scripts/run_ecosystem_flow_harness.py",
    "scripts/validate_governance_closure.py",
    "scripts/guide_intake.py",
    "scripts/adapt_governance.py",
    "scripts/project_governance_views.py",
    "scripts/validate_projection_metadata.py",
    "scripts/evaluate_governance.py",
    "scripts/validate_all.py",
    "scripts/validate_identity_contract.py",
    "scripts/validate_contract_preservation.py",
    "scripts/validate_release_contract.py",
    "scripts/validate_documentation.py",
    "scripts/validate_assurance_contract.py",
    "scripts/package_skill.py",
    "tests/original-contract.json",
    "tests/current-release-contract.json",
    "tests/protected-file-migrations.json",
    "tests/test_release_contract.py",
    "tests/test_documentation_validation.py",
    "tests/test_assurance_contract.py",
    "tests/test_package_attestation.py",
    "tests/test_identity_model.py",
    "tests/test_ecosystem_handoff.py",
    "tests/test_ecosystem_compatibility.py",
    "tests/test_governance_closure.py",
    "tests/test_guided_intake.py",
    "tests/test_governance_views_v23.py",
    "tests/test_priority_contract.py",
    "tests/test_handoff_diagnostics.py",
    "assets/icon.svg",
    "examples/activation-scenarios.json",
    "evals/activation-boundary-scenarios.json",
    "evals/booster-activation-scenarios.json",
]
REQUIRED_TEMPLATE_NAMES = {
    "ops.yaml.template",
    "status.md.template",
    "stakeholder-brief.md.template",
    "replanning.md.template",
    "feature-report.md.template",
    "portfolio.yaml.template",
    "portfolio.md.template",
    "roadmap.yaml.template",
    "roadmap.md.template",
    "feature-map.yaml.template",
    "rfc-proposals.md.template",
    "governance-decisions.md.template",
    "release-notes.md.template",
    "internal-notes.md.template",
}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_PATH_RE = re.compile(r"`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`")
MARKER_PARTS = [r"\[" + "TO" + "DO", r"\b" + "TO" + "DO" + r"\s*:", "replace with " + "actual", "this is a " + "placeholder"]
MARKER_RE = re.compile("|".join(MARKER_PARTS), re.IGNORECASE)
SCENARIO_CATEGORIES = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
SCENARIO_CATEGORY_PREFIXES = {
    "should_activate": "A",
    "should_not_activate": "N",
    "ambiguous": "B",
    "edge_case": "E",
    "regression": "R",
    "adversarial": "X",
}
EPHEMERAL_CACHE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EPHEMERAL_CACHE_SUFFIXES = {".pyc", ".pyo"}
GENERATED_OR_BLOCKED_DIR_NAMES = {
    ".git",
    "docs/skill-benchmark",
    "reports",
    "generated-evidence",
    "evidence",
}
BLOCKED_FILE_SUFFIXES = {".tmp", ".zip"}
BLOCKED_FILE_NAMES = {".DS_Store"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")
    raw_lines = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    keys: list[str] = []
    for line in raw_lines:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        keys.append(key)
        data[key] = value
    body = text[end + len("\n---"):]
    return data, keys, body


def normalize_ref(raw: str) -> str | None:
    ref = raw.strip().split("#", 1)[0].strip()
    if not ref or "://" in ref or ref.startswith("mailto:"):
        return None
    if any(ch.isspace() for ch in ref):
        return None
    return ref


def referenced_paths(skill_text: str) -> list[str]:
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


def validate_skill_md(root: Path, errors: list[str]) -> None:
    path = root / "SKILL.md"
    text = read_text(path)
    try:
        frontmatter, keys, body = parse_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        return
    if keys != EXPECTED_FRONTMATTER_KEYS:
        errors.append(f"SKILL.md frontmatter keys must be exactly {EXPECTED_FRONTMATTER_KEYS}; found {keys}")
    if frontmatter.get("name") != "nomia":
        errors.append("SKILL.md name must be nomia")
    description = frontmatter.get("description", "")
    if not description or description != description.lower():
        errors.append("SKILL.md description must be present and lowercase")
    if len(description.split()) < 25:
        errors.append("SKILL.md description must be specific enough for activation")
    required_phrases = [
        "mode selection matrix",
        "output contract",
        "acceptance gates",
        "stop conditions",
        "progressive loading",
        "scripts/validate_skill_package.py",
        "scripts/validate_activation_scenarios.py",
        "scripts/validate_golden_examples.py",
    "scripts/validate_governance_scenarios.py",
    "scripts/governance_contract.py",
    "scripts/guide_intake.py",
    "scripts/adapt_governance.py",
    "scripts/project_governance_views.py",
    "scripts/validate_projection_metadata.py",
    "scripts/evaluate_governance.py",
    "scripts/validate_all.py",
        "scripts/validate_identity_contract.py",
        "scripts/validate_contract_preservation.py",
        "scripts/package_skill.py",
        "references/package-validation.md",
    ]
    lower_body = body.lower()
    for phrase in required_phrases:
        if phrase not in lower_body:
            errors.append(f"SKILL.md is missing required control-plane phrase: {phrase}")
    for ref in referenced_paths(text):
        candidate = (root / ref).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            errors.append(f"SKILL.md references a path outside the skill: {ref}")
            continue
        if not candidate.exists():
            errors.append(f"SKILL.md references a missing path: {ref}")


def validate_required_files(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing required directory: {rel}")
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    template_dir = root / "assets" / "templates"
    found = {p.name for p in template_dir.glob("*.template")} if template_dir.exists() else set()
    missing = sorted(REQUIRED_TEMPLATE_NAMES - found)
    if missing:
        errors.append(f"missing template files: {', '.join(missing)}")


def validate_no_markers(root: Path, errors: list[str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("assets/templates/"):
            continue
        text = read_text(path)
        for index, line in enumerate(text.splitlines(), start=1):
            if MARKER_RE.search(line):
                errors.append(f"scaffold marker remains in {rel}:{index}")


def validate_scenarios(root: Path, errors: list[str]) -> None:
    scenario_path = root / "examples" / "activation-scenarios.json"
    try:
        data = json.loads(read_text(scenario_path))
    except Exception as exc:
        errors.append(f"activation scenarios are not valid JSON: {exc}")
        return
    if not isinstance(data, list):
        errors.append("activation scenarios must be a list")
        return
    counts = {category: 0 for category in SCENARIO_CATEGORIES}
    seen_ids: set[str] = set()
    seen_prompts: set[str] = set()
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"scenario {index} must be an object")
            continue
        scenario_id = item.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append(f"scenario {index} has no id")
        elif scenario_id in seen_ids:
            errors.append(f"duplicate scenario id: {scenario_id}")
        else:
            seen_ids.add(scenario_id)
        category = item.get("category")
        if category not in SCENARIO_CATEGORIES:
            errors.append(f"scenario {scenario_id or index} has invalid category: {category}")
        else:
            counts[category] += 1
            expected_prefix = SCENARIO_CATEGORY_PREFIXES[category]
            if isinstance(scenario_id, str) and not scenario_id.startswith(expected_prefix):
                errors.append(f"scenario {scenario_id or index} id must start with {expected_prefix} for category {category}")
        prompt = item.get("prompt")
        behavior = item.get("expected_behavior")
        notes = item.get("notes")
        if not isinstance(prompt, str) or len(prompt.strip()) < 20:
            errors.append(f"scenario {scenario_id or index} prompt is too short")
        else:
            normalized_prompt = " ".join(prompt.lower().split())
            if normalized_prompt in seen_prompts:
                errors.append(f"scenario {scenario_id or index} duplicates an earlier prompt")
            seen_prompts.add(normalized_prompt)
        if not isinstance(behavior, str) or len(behavior.strip()) < 30:
            errors.append(f"scenario {scenario_id or index} expected behavior is too short")
        if not isinstance(notes, str) or len(notes.strip()) < 3:
            errors.append(f"scenario {scenario_id or index} notes must describe the scenario purpose")
        expected = item.get("expected_activation")
        if category == "should_activate" and expected is not True:
            errors.append(f"scenario {scenario_id or index} should activate but expected_activation is not true")
        if category == "should_not_activate" and expected is not False:
            errors.append(f"scenario {scenario_id or index} should not activate but expected_activation is not false")
        if category == "ambiguous" and expected is not None:
            errors.append(f"scenario {scenario_id or index} ambiguous must have expected_activation null")
        if category == "edge_case" and expected is not True:
            errors.append(f"scenario {scenario_id or index} edge case must still activate")
        if category == "adversarial" and expected is False:
            errors.append(f"scenario {scenario_id or index} adversarial cases should activate to refuse, block, or validate rather than silently route away")
    for category, count in sorted(counts.items()):
        if count < 5:
            errors.append(f"activation scenario category {category} has {count}; expected at least 5")



def validate_harness_scenarios(root: Path, errors: list[str]) -> None:
    """Validate harness-compatible prompt scenarios used by external skill evaluators."""
    scenario_path = root / "evals" / "activation-boundary-scenarios.json"
    try:
        data = json.loads(read_text(scenario_path))
    except Exception as exc:
        errors.append(f"harness scenarios are not valid JSON: {exc}")
        return
    if not isinstance(data, dict):
        errors.append("harness scenarios must be a JSON object")
        return
    if data.get("target_skill") != "nomia":
        errors.append("harness scenarios target_skill must be nomia")
    if data.get("status") not in {"planned", "measured"}:
        errors.append("harness scenarios status must be planned or measured")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("harness scenarios must include a non-empty scenarios list")
        return

    required_fields = {"id", "type", "prompt", "expected_behavior", "acceptance_criteria"}
    counts = {category: 0 for category in SCENARIO_CATEGORIES}
    seen_ids: set[str] = set()
    seen_prompts: set[str] = set()
    for index, item in enumerate(scenarios):
        label = item.get("id", index) if isinstance(item, dict) else index
        if not isinstance(item, dict):
            errors.append(f"harness scenario {index} must be an object")
            continue
        missing = sorted(required_fields - set(item))
        if missing:
            errors.append(f"harness scenario {label} missing required fields: {', '.join(missing)}")
        scenario_id = item.get("id")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            errors.append(f"harness scenario {index} has no id")
        elif scenario_id in seen_ids:
            errors.append(f"duplicate harness scenario id: {scenario_id}")
        else:
            seen_ids.add(scenario_id)
        category = item.get("type")
        if category not in SCENARIO_CATEGORIES:
            errors.append(f"harness scenario {label} has invalid type: {category}")
        else:
            counts[category] += 1
        prompt = item.get("prompt")
        if not isinstance(prompt, str) or len(prompt.strip()) < 20:
            errors.append(f"harness scenario {label} prompt is too short")
        else:
            normalized_prompt = " ".join(prompt.lower().split())
            if normalized_prompt in seen_prompts:
                errors.append(f"harness scenario {label} duplicates an earlier prompt")
            seen_prompts.add(normalized_prompt)
        behavior = item.get("expected_behavior")
        if not isinstance(behavior, str) or len(behavior.strip()) < 40:
            errors.append(f"harness scenario {label} expected_behavior is too short")
        criteria = item.get("acceptance_criteria")
        if not isinstance(criteria, list) or len(criteria) < 2 or not all(isinstance(value, str) and value.strip() for value in criteria):
            errors.append(f"harness scenario {label} must include at least two acceptance criteria")
    for category, count in sorted(counts.items()):
        if count < 5:
            errors.append(f"harness scenario category {category} has {count}; expected at least 5")

def validate_package_hygiene(root: Path, errors: list[str]) -> None:
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if any(part in EPHEMERAL_CACHE_DIR_NAMES for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix.lower() in EPHEMERAL_CACHE_SUFFIXES:
            continue
        reason = sensitive_package_reason(path)
        if reason:
            errors.append(f"unsafe package path {rel}: {reason}")
            continue
        if any(rel == name or rel.startswith(name + "/") for name in GENERATED_OR_BLOCKED_DIR_NAMES):
            errors.append(f"blocked generated path present: {rel}")
            continue
        if path.is_file() and path.name in BLOCKED_FILE_NAMES:
            errors.append(f"blocked generated/system file present: {rel}")
        if path.is_file() and path.suffix.lower() in BLOCKED_FILE_SUFFIXES:
            errors.append(f"blocked generated/package file present: {rel}")


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"target is not a directory: {root}"]
    validate_required_files(root, errors)
    if (root / "SKILL.md").exists():
        validate_skill_md(root, errors)
    validate_no_markers(root, errors)
    validate_scenarios(root, errors)
    validate_harness_scenarios(root, errors)
    validate_package_hygiene(root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate nomia skill package structure before packaging.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="nomia skill root. Defaults to this script's parent skill.")
    parser.add_argument("--json-output", help="Optional path for machine-readable validation output.")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    errors = validate_package(root)
    status = "pass" if not errors else "fail"
    result: dict[str, Any] = {"target": str(root), "status": status, "errors": errors}
    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(output_path, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"status: {status}")
    if errors:
        for error in errors:
            print(f"fail: {error}")
    else:
        print("all nomia skill package checks passed")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
