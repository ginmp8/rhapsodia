#!/usr/bin/env python3
"""Validate Magnomo contracts and actor write boundaries."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from magnomo_utils import load_yaml_mapping, read_normalized_lines, unique


MAGNOMO_ARTIFACTS = {
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
MAGO_ARTIFACTS = {"spec-catalog.yaml", "define-queue.yaml", "manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"}
MAGIA_EVIDENCE_MARKERS = {"execution-evidence.yaml", "execution-log.yaml", "execution-record.yaml"}
SPEC_PACKAGE_RE = re.compile(r"(^|/|\\)specs(/|\\)[^/\\]+(/|\\)(manifest.yaml|prd.md|tasks.md|notes.md|validation.md)$")
SPEC_ID_RE = re.compile(r"^spec\d{3}$")
CYCLE_VERSION_RE = re.compile(r"^\d{2}\.\d{2}\.\d{2}$")
FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROLLED_RALPH_FILES = {"manifest.yaml", "tasks.md", "notes.md", "validation.md"}
MAGIA_PLANNING_INTENT_FILES = {"prd.md"}
MAGNOMO_ALLOWED_CODE_DIR = ".github/skills/magnomo/scripts/"
CONTRACT_YAML_REQUIREMENT = "PyYAML is required to validate Magnomo contract YAML artifacts."
CODE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".rb",
    ".php",
    ".cs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".sh",
    ".ps1",
    ".sql",
}



def is_under_skill(path: str, skill: str) -> bool:
    return f".github/skills/{skill}/" in path


def is_magnomo_owned(path: str) -> bool:
    name = Path(path).name
    return is_under_skill(path, "magnomo") or name in MAGNOMO_ARTIFACTS or "/magnomo/" in path


def is_mago_owned(path: str) -> bool:
    name = Path(path).name
    return is_under_skill(path, "mago") or name in MAGO_ARTIFACTS or bool(SPEC_PACKAGE_RE.search(path))


def is_magia_owned(path: str) -> bool:
    name = Path(path).name
    return (
        is_under_skill(path, "magia")
        or name in MAGIA_EVIDENCE_MARKERS
        or "/execution/" in path
        or ".omni_loops/runs/" in path
    )


def is_spec_package_file(path: str) -> bool:
    return bool(SPEC_PACKAGE_RE.search(path))


def is_repository_code(path: str) -> bool:
    if path.startswith(MAGNOMO_ALLOWED_CODE_DIR) or is_under_skill(path, "magnomo"):
        return False
    return Path(path).suffix.lower() in CODE_SUFFIXES or path.startswith(
        ("tests/", "omni_loops/", "current-solution/", "client/", "server/", "redash/", "scripts/")
    )


def validate_actor(actor: str, changed_files: list[str]) -> list[str]:
    errors: list[str] = []
    for path in changed_files:
        name = Path(path).name
        if actor == "mago":
            if is_magnomo_owned(path):
                errors.append(f"mago must not write Magnomo-owned artifact `{path}`")
            if is_magia_owned(path):
                errors.append(f"mago must not write Magia execution evidence `{path}`")
            if is_repository_code(path):
                errors.append(f"mago must not write repository code or execution outputs `{path}`")
        elif actor == "magia":
            if is_magnomo_owned(path):
                errors.append(f"magia must not write Magnomo-owned artifact `{path}`")
            if name in MAGIA_PLANNING_INTENT_FILES:
                errors.append(f"magia must not rewrite Mago planning intent or task definitions in `{path}`")
            elif is_mago_owned(path) and not (is_spec_package_file(path) and name in CONTROLLED_RALPH_FILES):
                errors.append(f"magia may only update controlled RALPH execution-state files in Mago packages: `{path}`")
        elif actor == "magnomo":
            if is_under_skill(path, "mago") or is_under_skill(path, "magia"):
                errors.append(f"magnomo must not write Mago or Magia files: `{path}`")
            elif is_mago_owned(path):
                errors.append(f"magnomo must not write Mago planning package artifact `{path}`")
            elif is_magia_owned(path):
                errors.append(f"magnomo must not write Magia execution record `{path}`")
            elif is_repository_code(path):
                errors.append(f"magnomo must not write repository code or execution paths: `{path}`")
        else:
            errors.append(f"unknown actor `{actor}`")
            break
    return errors


def validate_spec_id(label: str, value: Any, errors: list[str]) -> None:
    if value not in (None, "") and not SPEC_ID_RE.match(str(value)):
        errors.append(f"{label} must use `specNNN` format")


def validate_feature_key(label: str, value: Any, errors: list[str]) -> None:
    if value not in (None, "") and not FEATURE_KEY_RE.match(str(value)):
        errors.append(f"{label} must be lowercase hyphen-case")


def validate_cycle_version(label: str, value: Any, errors: list[str]) -> None:
    if value not in (None, "") and not CYCLE_VERSION_RE.match(str(value)):
        errors.append(f"{label} must use `NN.NN.NN` format")


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
    for key in ("spec_id", "feature_key", "cycle_version", "candidate_spec_id"):
        if key in source:
            identity[key] = source.get(key)

    validate_spec_id(f"{path}: spec_id", identity.get("spec_id"), errors)
    validate_spec_id(f"{path}: candidate_spec_id", identity.get("candidate_spec_id"), errors)
    validate_feature_key(f"{path}: feature_key", identity.get("feature_key"), errors)
    validate_cycle_version(f"{path}: cycle_version", identity.get("cycle_version"), errors)
    if identity.get("candidate_spec_id") and identity.get("spec_id") and identity["candidate_spec_id"] != identity["spec_id"]:
        errors.append(f"{path}: candidate_spec_id must match spec_id when both are present")
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
    parser = argparse.ArgumentParser(description="Validate Magnomo contracts.")
    parser.add_argument("--actor", choices=["mago", "magia", "magnomo"], help="Actor that produced the changed files.")
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
            errors.extend(
                validate_actor(
                    args.actor or "",
                    read_normalized_lines(changed_path),
                )
            )

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

    print("OK: validated Magnomo contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
