#!/usr/bin/env python3
"""Validate nomia contracts and actor write boundaries."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from nomia_utils import (
    YEAR_RE,
    infer_year_from_cycle_id,
    load_yaml_mapping,
    parse_spec_id,
    read_normalized_lines,
    unique,
    validate_cycle_id_format,
    validate_spec_id_format,
)


nomia_ARTIFACTS = {
    "ops.yaml",
    "status.md",
    "stakeholder-brief.md",
    "replanning.md",
    "roadmap.yaml",
    "roadmap.md",
    "rfc-proposals.md",
    "governance-decisions.md",
    "feature-map.yaml",
    "feature-report.md",
    "release-notes.md",
    "internal-notes.md",
    "portfolio.md",
    "portfolio.yaml",
}
MAGO_ARTIFACTS = {
    "cycle.yaml",
    "manifest.yaml",
    "prd.md",
    "tasks.md",
    "notes.md",
    "validation.md",
    "technical-design.md",
    "architecture-decisions.md",
    "execution-handoff-plan.md",
    "contract-spec.md",
    "migration-strategy.md",
    "observability-design.md",
    "operational-requirements.md",
    "security-and-risk-considerations.md",
    "open-questions.md",
    "spec-catalog.yaml",
    "define-queue.yaml",
}
MAGIA_EVIDENCE_MARKERS = {
    "execution-evidence.yaml",
    "execution-log.yaml",
    "execution-record.yaml",
    "implementation-notes.md",
    "validation-evidence.md",
    "implementation-adr.md",
    "runbook.md",
    "migration-execution-note.md",
    "contract-change-note.md",
    "observability-note.md",
    "troubleshooting.md",
    "security-risk-note.md",
    "technical-gap-note.md",
}
SPEC_PACKAGE_RE = re.compile(
    r"(^|/|\\)specs(/|\\)[^/\\]+(/|\\)(manifest.yaml|prd.md|tasks.md|notes.md|validation.md|technical-design.md|architecture-decisions.md|execution-handoff-plan.md|contract-spec.md|migration-strategy.md|observability-design.md|operational-requirements.md|security-and-risk-considerations.md|open-questions.md)$"
)
REGISTRY_RE = re.compile(r"(^|/|\\)registry(/|\\)[^/\\]+\.yaml$")
FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROLLED_RALPH_FILES = {"manifest.yaml", "tasks.md"}
MAGIA_PLANNING_INTENT_FILES = {"prd.md", "notes.md", "validation.md", "technical-design.md"}
CONTRACT_YAML_REQUIREMENT = "PyYAML is required to validate nomia contract YAML artifacts."
SKILL_PACKAGE_DIRS = {"agents", "assets", "evals", "examples", "references", "scripts", "tests"}
SKILL_PACKAGE_FILES = {"SKILL.md", "skill.md"}
CODE_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".cs", ".c", ".cc", ".cpp", ".h", ".hpp", ".sh", ".ps1", ".sql",
}


def normalize_repo_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def path_parts(path: str) -> list[str]:
    return [part for part in normalize_repo_path(path).strip("/").split("/") if part]


def has_skill_package_anchor(path: str, skill: str) -> bool:
    parts = path_parts(path)
    for index, part in enumerate(parts):
        if part != skill:
            continue
        remainder = parts[index + 1 :]
        if not remainder:
            return True
        if remainder[0] in SKILL_PACKAGE_DIRS or remainder[0] in SKILL_PACKAGE_FILES:
            return True
    return False


def is_under_skill(path: str, skill: str) -> bool:
    return has_skill_package_anchor(path, skill)


def is_nomia_owned(path: str) -> bool:
    normalized = normalize_repo_path(path)
    name = Path(path).name
    return is_under_skill(normalized, "nomia") or name in nomia_ARTIFACTS or "/nomia/" in f"/{normalized}/"


def is_registry_file(path: str) -> bool:
    return bool(REGISTRY_RE.search(normalize_repo_path(path)))


def is_mago_owned(path: str) -> bool:
    name = Path(path).name
    return (
        is_under_skill(path, "mago")
        or name in MAGO_ARTIFACTS
        or bool(SPEC_PACKAGE_RE.search(path))
        or is_registry_file(path)
    )


def is_magia_owned(path: str) -> bool:
    normalized = normalize_repo_path(path)
    name = Path(path).name
    return (
        is_under_skill(normalized, "magia")
        or name in MAGIA_EVIDENCE_MARKERS
        or "/execution/" in f"/{normalized}/"
        or ".omni_loops/runs/" in normalized
    )


def is_spec_package_file(path: str) -> bool:
    return bool(SPEC_PACKAGE_RE.search(path))


def is_repository_code(path: str) -> bool:
    normalized = normalize_repo_path(path)
    if is_under_skill(normalized, "nomia"):
        return False
    return Path(path).suffix.lower() in CODE_SUFFIXES or normalized.startswith(
        ("tests/", "omni_loops/", "current-solution/", "client/", "server/", "redash/", "scripts/")
    )


def validate_actor(actor: str, changed_files: list[str]) -> list[str]:
    errors: list[str] = []
    for path in changed_files:
        name = Path(path).name
        if actor == "mago":
            if is_nomia_owned(path):
                errors.append(f"mago must not write nomia-owned artifact `{path}`")
            if is_magia_owned(path):
                errors.append(f"mago must not write Magia execution evidence `{path}`")
            if is_repository_code(path):
                errors.append(f"mago must not write repository code or execution outputs `{path}`")
        elif actor == "magia":
            if is_nomia_owned(path):
                errors.append(f"magia must not write nomia-owned artifact `{path}`")
            if name in MAGIA_PLANNING_INTENT_FILES:
                errors.append(f"magia must not rewrite Mago planning intent or task definitions in `{path}`")
            elif is_registry_file(path):
                continue
            elif is_mago_owned(path) and not (is_spec_package_file(path) and name in CONTROLLED_RALPH_FILES):
                errors.append(f"magia may only update controlled execution-state files in Mago packages: `{path}`")
        elif actor == "nomia":
            if is_under_skill(path, "mago") or is_under_skill(path, "magia"):
                errors.append(f"nomia must not write Mago or Magia files: `{path}`")
            elif is_mago_owned(path):
                errors.append(f"nomia must not write Mago planning or registry artifact `{path}`")
            elif is_magia_owned(path):
                errors.append(f"nomia must not write Magia execution record `{path}`")
            elif is_repository_code(path):
                errors.append(f"nomia must not write repository code or execution paths: `{path}`")
        else:
            errors.append(f"unknown actor `{actor}`")
            break
    return errors


def validate_spec_id(label: str, value: Any, errors: list[str]) -> None:
    error = validate_spec_id_format(value)
    if error:
        errors.append(f"{label} {error}")


def validate_feature_key(label: str, value: Any, errors: list[str]) -> None:
    if value not in (None, "") and not FEATURE_KEY_RE.fullmatch(str(value)):
        errors.append(f"{label} must be lowercase hyphen-case")


def validate_cycle_id(label: str, value: Any, errors: list[str]) -> None:
    error = validate_cycle_id_format(value)
    if error:
        errors.append(f"{label} {error}")


def validate_year(label: str, value: Any, errors: list[str]) -> None:
    if value not in (None, "") and not YEAR_RE.fullmatch(str(value)):
        errors.append(f"{label} must use YYYY format")


def roadmap_contract_index(path: Path) -> tuple[list[str], dict[str, dict[str, Any]], dict[str, str]]:
    errors: list[str] = []
    features: dict[str, dict[str, Any]] = {}
    candidate_to_feature: dict[str, str] = {}
    try:
        data = load_yaml_mapping(path, CONTRACT_YAML_REQUIREMENT)
    except Exception as exc:
        return [f"{path}: {exc}"], features, candidate_to_feature

    for index, feature in enumerate(data.get("features") or []):
        if not isinstance(feature, dict):
            errors.append(f"{path}: features[{index}] must be a mapping")
            continue
        feature_key = feature.get("feature_key")
        candidate = feature.get("candidate_spec_id")
        validate_feature_key(f"{path}: features[{index}].feature_key", feature_key, errors)
        validate_spec_id(f"{path}: features[{index}].candidate_spec_id", candidate, errors)
        if candidate and feature_key:
            try:
                parsed = parse_spec_id(str(candidate))
            except ValueError:
                pass
            else:
                if parsed["feature_key"] != str(feature_key):
                    errors.append(f"{path}: features[{index}].candidate_spec_id feature key must match feature_key")
        if feature_key:
            features[str(feature_key)] = feature
        if candidate:
            candidate_to_feature[str(candidate)] = str(feature_key or "")
    return errors, features, candidate_to_feature


def feature_map_contract_index(path: Path) -> tuple[list[str], dict[str, dict[str, Any]], dict[str, str]]:
    errors: list[str] = []
    features: dict[str, dict[str, Any]] = {}
    candidate_to_feature: dict[str, str] = {}
    try:
        data = load_yaml_mapping(path, CONTRACT_YAML_REQUIREMENT)
    except Exception as exc:
        return [f"{path}: {exc}"], features, candidate_to_feature

    for index, feature in enumerate(data.get("features") or []):
        if not isinstance(feature, dict):
            errors.append(f"{path}: features[{index}] must be a mapping")
            continue
        feature_key = feature.get("feature_key")
        candidate = feature.get("candidate_spec_id")
        validate_feature_key(f"{path}: features[{index}].feature_key", feature_key, errors)
        validate_spec_id(f"{path}: features[{index}].candidate_spec_id", candidate, errors)
        if candidate and feature_key:
            try:
                parsed = parse_spec_id(str(candidate))
            except ValueError:
                pass
            else:
                if parsed["feature_key"] != str(feature_key):
                    errors.append(f"{path}: features[{index}].candidate_spec_id feature key must match feature_key")
        if feature_key:
            features[str(feature_key)] = feature
        if candidate:
            candidate_to_feature[str(candidate)] = str(feature_key or "")
    return errors, features, candidate_to_feature


def execution_evidence_identity(path: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    identity: dict[str, Any] = {}
    try:
        data = load_yaml_mapping(path, CONTRACT_YAML_REQUIREMENT)
    except Exception as exc:
        return [f"{path}: {exc}"], identity

    source = data.get("identity") if isinstance(data.get("identity"), dict) else data
    for key in ("board_id", "year", "cycle_id", "spec_id", "feature_key", "candidate_spec_id"):
        if key in source:
            identity[key] = source.get(key)

    validate_spec_id(f"{path}: spec_id", identity.get("spec_id"), errors)
    validate_spec_id(f"{path}: candidate_spec_id", identity.get("candidate_spec_id"), errors)
    validate_feature_key(f"{path}: feature_key", identity.get("feature_key"), errors)
    validate_cycle_id(f"{path}: cycle_id", identity.get("cycle_id"), errors)
    validate_year(f"{path}: year", identity.get("year"), errors)
    if identity.get("cycle_id"):
        try:
            parsed_year = infer_year_from_cycle_id(str(identity["cycle_id"]))
        except ValueError:
            pass
        else:
            if identity.get("year") and str(identity["year"]) != parsed_year:
                errors.append(f"{path}: year must match cycle_id creation year `{parsed_year}`")
    if identity.get("candidate_spec_id") and identity.get("spec_id") and identity["candidate_spec_id"] != identity["spec_id"]:
        errors.append(f"{path}: candidate_spec_id must match spec_id when both are present")
    evidence_spec = identity.get("spec_id") or identity.get("candidate_spec_id")
    if evidence_spec and identity.get("feature_key"):
        try:
            parsed = parse_spec_id(str(evidence_spec))
        except ValueError:
            pass
        else:
            if parsed["feature_key"] != str(identity["feature_key"]):
                errors.append(f"{path}: spec_id feature key must match feature_key")
    return errors, identity


def validate_contract_files(roadmap: Path | None, feature_map: Path | None, execution_evidence: Path | None) -> list[str]:
    errors: list[str] = []
    for label, path in (("roadmap", roadmap), ("feature-map", feature_map), ("execution-evidence", execution_evidence)):
        if path is not None and not path.exists():
            errors.append(f"{label} file does not exist: {path}")
    if errors:
        return errors

    roadmap_features: dict[str, dict[str, Any]] = {}
    roadmap_candidates: dict[str, str] = {}
    feature_map_features: dict[str, dict[str, Any]] = {}
    feature_map_candidates: dict[str, str] = {}

    if roadmap is not None:
        roadmap_errors, roadmap_features, roadmap_candidates = roadmap_contract_index(roadmap)
        errors.extend(roadmap_errors)
    if feature_map is not None:
        map_errors, feature_map_features, feature_map_candidates = feature_map_contract_index(feature_map)
        errors.extend(map_errors)

    for feature_key, mapped in feature_map_features.items():
        roadmap_feature = roadmap_features.get(feature_key)
        if roadmap is not None and roadmap_feature is None:
            errors.append(f"{feature_map}: feature_key `{feature_key}` does not exist in roadmap")
            continue
        if roadmap_feature is not None:
            if mapped.get("ready_for_spec") != roadmap_feature.get("ready_for_spec"):
                errors.append(f"{feature_map}: `{feature_key}` ready_for_spec must match roadmap")
            if (mapped.get("candidate_spec_id") or None) != (roadmap_feature.get("candidate_spec_id") or None):
                errors.append(f"{feature_map}: `{feature_key}` candidate_spec_id must match roadmap")

    if execution_evidence is not None:
        evidence_errors, identity = execution_evidence_identity(execution_evidence)
        errors.extend(evidence_errors)
        evidence_spec = identity.get("spec_id") or identity.get("candidate_spec_id")
        evidence_feature = identity.get("feature_key")
        if evidence_spec and feature_map_candidates and evidence_spec not in feature_map_candidates:
            errors.append(f"{execution_evidence}: spec_id `{evidence_spec}` is not present in feature-map candidates")
        if evidence_feature and feature_map_features and evidence_feature not in feature_map_features:
            errors.append(f"{execution_evidence}: feature_key `{evidence_feature}` is not present in feature-map")
        if evidence_spec and evidence_feature:
            mapped_feature = feature_map_candidates.get(str(evidence_spec)) or roadmap_candidates.get(str(evidence_spec))
            if mapped_feature and mapped_feature != evidence_feature:
                errors.append(
                    f"{execution_evidence}: spec_id `{evidence_spec}` maps to feature_key `{mapped_feature}`, not `{evidence_feature}`"
                )
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate nomia contracts.")
    parser.add_argument("--actor", choices=["mago", "magia", "nomia"], help="Actor that produced the changed files.")
    parser.add_argument("--changed-files", help="Newline-delimited file containing changed paths.")
    parser.add_argument("--roadmap", help="Optional roadmap.yaml path to check for existence.")
    parser.add_argument("--feature-map", help="Optional feature-map.yaml path to check for existence.")
    parser.add_argument("--execution-evidence", help="Optional execution evidence path to check for existence.")
    args = parser.parse_args(argv)

    errors: list[str] = []
    if args.changed_files and not args.actor:
        errors.append("--actor is required with --changed-files")
    if args.actor and not args.changed_files:
        errors.append("--changed-files is required with --actor")

    if args.changed_files:
        changed_path = Path(args.changed_files).resolve()
        if not changed_path.exists():
            errors.append(f"changed-files list does not exist: {changed_path}")
        else:
            errors.extend(validate_actor(args.actor or "", read_normalized_lines(changed_path)))

    errors.extend(
        validate_contract_files(
            Path(args.roadmap).resolve() if args.roadmap else None,
            Path(args.feature_map).resolve() if args.feature_map else None,
            Path(args.execution_evidence).resolve() if args.execution_evidence else None,
        )
    )

    errors = unique(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1

    print("OK: validated nomia contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
