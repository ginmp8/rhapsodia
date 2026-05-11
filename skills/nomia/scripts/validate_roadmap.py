#!/usr/bin/env python3
"""Validate nomia roadmap.yaml and feature-map.yaml artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from nomia_utils import has_unresolved_template_token, is_missing, load_yaml_mapping, scan_unresolved_template_tokens, unique


FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROADMAP_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPEC_ID_RE = re.compile(r"^spec\d{3}$")
VALID_HORIZONS = {"unknown", "now", "next", "later", "future"}
VALID_COMMITMENTS = {"unknown", "committed", "targeted", "exploratory", "parking_lot"}
VALID_CONFIDENCE = {"unknown", "low", "medium", "high"}
VALID_HANDOFF_STATUS = {"unknown", "draft", "ready", "blocked", "parked", "accepted"}
VALID_MAGO_MODES = {"unknown", "define", "refine", "split"}
FORBIDDEN_FEATURE_MAP_KEYS = {
    "acceptance_criteria",
    "tasks",
    "implementation_tasks",
    "validation_plan",
    "code_changes",
    "execution_evidence",
}

ROADMAP_REQUIRED_KEYS = ("schema_version", "roadmap_id", "title", "owner", "horizon", "features")
FEATURE_REQUIRED_KEYS = (
    "feature_key",
    "name",
    "problem",
    "outcome",
    "horizon",
    "commitment",
    "confidence",
    "dependencies",
    "ready_for_spec",
    "candidate_spec_id",
)
FEATURE_MAP_REQUIRED_KEYS = ("schema_version", "roadmap_id", "features")
HANDOFF_REQUIRED_KEYS = (
    "feature_key",
    "ready_for_spec",
    "candidate_spec_id",
)



def validate_enum(label: str, value: Any, valid_values: set[str], errors: list[str]) -> None:
    if value in (None, ""):
        return
    if has_unresolved_template_token(value):
        return
    if str(value) not in valid_values:
        errors.append(f"{label} must be one of {sorted(valid_values)}")


def validate_required_keys(label: str, data: dict[str, Any], keys: tuple[str, ...], errors: list[str]) -> None:
    for key in keys:
        if key not in data:
            errors.append(f"{label}: missing required key `{key}`")


def validate_list(label: str, value: Any, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    return value


def validate_spec_id(label: str, value: Any, errors: list[str]) -> None:
    if value not in (None, "") and not has_unresolved_template_token(value) and not SPEC_ID_RE.match(str(value)):
        errors.append(f"{label} must be null or use `specNNN` format")


def scan_for_forbidden_keys(label: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_label = f"{label}.{key_text}" if label else key_text
            if key_text in FORBIDDEN_FEATURE_MAP_KEYS:
                errors.append(f"{child_label} belongs to Mago or Magia, not nomia roadmap handoff")
            scan_for_forbidden_keys(child_label, child, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_for_forbidden_keys(f"{label}[{index}]", child, errors)


def validate_roadmap(path: Path) -> tuple[list[str], list[str], dict[str, dict[str, Any]], str | None]:
    errors: list[str] = []
    warnings: list[str] = []
    feature_by_key: dict[str, dict[str, Any]] = {}
    roadmap_id: str | None = None

    if not path.exists():
        return [f"missing required file: {path}"], warnings, feature_by_key, roadmap_id

    try:
        data = load_yaml_mapping(path)
    except Exception as exc:
        return [f"{path}: {exc}"], warnings, feature_by_key, roadmap_id

    errors.extend(scan_unresolved_template_tokens(data))

    validate_required_keys(str(path), data, ROADMAP_REQUIRED_KEYS, errors)

    if data.get("schema_version") != 1:
        errors.append(f"{path}: `schema_version` must be 1")

    roadmap_id_value = data.get("roadmap_id")
    if not is_missing(roadmap_id_value):
        roadmap_id = str(roadmap_id_value)
        if not has_unresolved_template_token(roadmap_id) and not ROADMAP_ID_RE.match(roadmap_id):
            errors.append(f"{path}: `roadmap_id` must be lowercase hyphen-case")
    else:
        warnings.append(f"{path}: `roadmap_id` is missing")

    if is_missing(data.get("title")):
        warnings.append(f"{path}: `title` is missing")
    if is_missing(data.get("owner")):
        warnings.append(f"{path}: `owner` is missing")

    validate_enum(f"{path}: `horizon`", data.get("horizon", "unknown"), VALID_HORIZONS, errors)

    features = validate_list(f"{path}: `features`", data.get("features"), errors)
    dependencies: list[tuple[str, str]] = []

    for index, feature in enumerate(features):
        feature_label = f"{path}: `features[{index}]`"
        if not isinstance(feature, dict):
            errors.append(f"{feature_label} must be a mapping")
            continue

        validate_required_keys(feature_label, feature, FEATURE_REQUIRED_KEYS, errors)

        key_value = feature.get("feature_key")
        key = str(key_value or "")
        key_label = key or f"features[{index}]"
        if has_unresolved_template_token(key):
            pass
        elif not FEATURE_KEY_RE.match(key):
            errors.append(f"{feature_label}.feature_key must be lowercase hyphen-case")
        elif key in feature_by_key:
            errors.append(f"{path}: duplicate feature_key `{key}`")
        else:
            feature_by_key[key] = feature

        for required_text_key in ("name", "problem", "outcome"):
            if required_text_key in feature and is_missing(feature.get(required_text_key)):
                warnings.append(f"{path}: `{key_label}.{required_text_key}` is missing")

        validate_enum(f"{path}: `{key_label}.horizon`", feature.get("horizon", "unknown"), VALID_HORIZONS, errors)
        validate_enum(
            f"{path}: `{key_label}.commitment`",
            feature.get("commitment", "unknown"),
            VALID_COMMITMENTS,
            errors,
        )
        validate_enum(
            f"{path}: `{key_label}.confidence`",
            feature.get("confidence", "unknown"),
            VALID_CONFIDENCE,
            errors,
        )

        if "ready_for_spec" in feature and not isinstance(feature.get("ready_for_spec"), bool):
            errors.append(f"{path}: `{key_label}.ready_for_spec` must be a boolean")

        candidate = feature.get("candidate_spec_id")
        validate_spec_id(f"{path}: `{key_label}.candidate_spec_id`", candidate, errors)

        if feature.get("ready_for_spec") is True and not candidate:
            warnings.append(f"{path}: `{key_label}` is ready_for_spec but has no candidate_spec_id")
        if feature.get("ready_for_spec") is False and candidate:
            warnings.append(f"{path}: `{key_label}` has candidate_spec_id but is not ready_for_spec")

        deps = feature.get("dependencies")
        if "dependencies" in feature:
            for dep in validate_list(f"{path}: `{key_label}.dependencies`", deps, errors):
                dependencies.append((key_label, str(dep)))

    for key, dep in dependencies:
        if dep not in feature_by_key:
            errors.append(f"{path}: `{key}` depends on unknown feature `{dep}`")

    return errors, warnings, feature_by_key, roadmap_id


def validate_feature_map(
    path: Path,
    roadmap_features: dict[str, dict[str, Any]],
    roadmap_id: str | None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"missing required file: {path}"], warnings

    try:
        data = load_yaml_mapping(path)
    except Exception as exc:
        return [f"{path}: {exc}"], warnings

    errors.extend(scan_unresolved_template_tokens(data))

    validate_required_keys(str(path), data, FEATURE_MAP_REQUIRED_KEYS, errors)

    if data.get("schema_version") != 1:
        errors.append(f"{path}: `schema_version` must be 1")

    map_roadmap_id = data.get("roadmap_id")
    if roadmap_id and map_roadmap_id not in (None, "") and str(map_roadmap_id) != roadmap_id:
        errors.append(f"{path}: `roadmap_id` must match roadmap.yaml `{roadmap_id}`")
    if is_missing(map_roadmap_id):
        warnings.append(f"{path}: `roadmap_id` is missing")

    features = validate_list(f"{path}: `features`", data.get("features"), errors)
    seen: set[str] = set()
    roadmap_ready_keys = {key for key, value in roadmap_features.items() if value.get("ready_for_spec") is True}
    map_ready_keys: set[str] = set()

    for index, feature in enumerate(features):
        feature_label = f"{path}: `features[{index}]`"
        if not isinstance(feature, dict):
            errors.append(f"{feature_label} must be a mapping")
            continue

        scan_for_forbidden_keys(feature_label, feature, errors)
        validate_required_keys(feature_label, feature, HANDOFF_REQUIRED_KEYS, errors)

        key = str(feature.get("feature_key") or "")
        key_label = key or f"features[{index}]"
        if has_unresolved_template_token(key):
            pass
        elif not FEATURE_KEY_RE.match(key):
            errors.append(f"{feature_label}.feature_key must be lowercase hyphen-case")
        elif key in seen:
            errors.append(f"{path}: duplicate feature_key `{key}`")
        else:
            seen.add(key)

        roadmap_feature = roadmap_features.get(key)
        if roadmap_feature is None:
            errors.append(f"{path}: feature_key `{key}` does not exist in roadmap.yaml")

        if "ready_for_spec" in feature and not isinstance(feature.get("ready_for_spec"), bool):
            errors.append(f"{path}: `{key_label}.ready_for_spec` must be a boolean")
        if feature.get("ready_for_spec") is True:
            map_ready_keys.add(key)

        candidate = feature.get("candidate_spec_id")
        validate_spec_id(f"{path}: `{key_label}.candidate_spec_id`", candidate, errors)

        deps = feature.get("dependencies")
        if "dependencies" in feature:
            for dep in validate_list(f"{path}: `{key_label}.dependencies`", deps, errors):
                if str(dep) not in roadmap_features:
                    errors.append(f"{path}: `{key_label}` depends on unknown feature `{dep}`")

        validate_enum(
            f"{path}: `{key_label}.handoff_status`",
            feature.get("handoff_status", "unknown"),
            VALID_HANDOFF_STATUS,
            errors,
        )
        validate_enum(
            f"{path}: `{key_label}.recommended_mago_mode`",
            feature.get("recommended_mago_mode", "unknown"),
            VALID_MAGO_MODES,
            errors,
        )

        if feature.get("ready_for_spec") is True and not candidate:
            warnings.append(f"{path}: `{key_label}` is ready_for_spec but has no candidate_spec_id")

        if roadmap_feature is not None:
            roadmap_ready = roadmap_feature.get("ready_for_spec")
            roadmap_candidate = roadmap_feature.get("candidate_spec_id")
            if feature.get("ready_for_spec") != roadmap_ready:
                errors.append(f"{path}: `{key}` ready_for_spec must match roadmap.yaml")
            if (candidate or None) != (roadmap_candidate or None):
                errors.append(f"{path}: `{key}` candidate_spec_id must match roadmap.yaml")

    missing_ready_keys = roadmap_ready_keys - map_ready_keys
    for key in sorted(missing_ready_keys):
        warnings.append(f"{path}: roadmap feature `{key}` is ready_for_spec but absent from feature-map.yaml")

    return errors, warnings



def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate nomia roadmap artifacts.")
    parser.add_argument("--roadmap", default="roadmap.yaml", help="Path to roadmap.yaml.")
    parser.add_argument("--feature-map", default="feature-map.yaml", help="Path to feature-map.yaml.")
    args = parser.parse_args(argv)

    roadmap_path = Path(args.roadmap).resolve()
    feature_map_path = Path(args.feature_map).resolve()

    errors, warnings, roadmap_features, roadmap_id = validate_roadmap(roadmap_path)
    map_errors, map_warnings = validate_feature_map(feature_map_path, roadmap_features, roadmap_id)
    errors.extend(map_errors)
    warnings.extend(map_warnings)
    errors = unique(errors)
    warnings = unique(warnings)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        print(f"FAILED: {len(errors)} errors, {len(warnings)} warnings")
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}")
    if warnings:
        print(f"OK: completed with {len(warnings)} warnings")
    else:
        print("OK: validated nomia roadmap artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
