#!/usr/bin/env python3
"""Populate list fields in MAGO template-backed artifacts with schema checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
from mago_utils import SPEC_ID_RE

TASK_ID_RE = re.compile(r"^task\d{3}$")
TEMPLATE_TOKEN_RE = re.compile(r"<[^>\n]+>")


@dataclass(frozen=True)
class ListRule:
    path: str
    item_type: str
    required: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()
    enum_fields: dict[str, set[str]] = field(default_factory=dict)
    regex_fields: dict[str, re.Pattern[str]] = field(default_factory=dict)
    nullable_fields: set[str] = field(default_factory=set)
    list_fields: dict[str, str] = field(default_factory=dict)
    unique_by: str | None = None
    allow_extra: bool = False

    @property
    def allowed_keys(self) -> set[str]:
        return set(self.required) | set(self.optional)


VALID_CYCLE_STATUS = {"planned", "in_progress", "done", "cancelled"}
VALID_SPEC_STATUS = {"planned", "in_progress", "blocked", "done", "cancelled", "superseded"}
VALID_PHASE = {"define", "execute", "done"}
VALID_HANDOFF_STATUS = {"ready_for_prepare_define", "blocked", "needs_discovery"}
VALID_DOWNSTREAM_MODE = {"define", "define-product", "define-tasks"}
VALID_PACKAGE_SHAPE = {"full", "product_only", "tasks_only"}
VALID_SEED_ARTIFACT = {"manifest.yaml", "prd.md", "technical-design.md", "tasks.md", "notes.md", "validation.md"}
VALID_CANDIDATE_STATUS = {"new", "updated", "provisional", "ready_for_order", "blocked", "duplicate"}
VALID_NEXT_STEP = {"continue_discovery", "order", "drop"}
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_FRONTIER_STATUS = {"updated", "blocked", "completed"}


GENERATED_VIEW_NAMES = {"spec-catalog.yaml", "define-queue.yaml"}


RULES: dict[str, dict[str, ListRule]] = {
    "spec-registry-entry.yaml": {
        "depends_on_features": ListRule("depends_on_features", "string"),
        "depends_on_specs": ListRule("depends_on_specs", "spec_id"),
        "supersedes": ListRule("supersedes", "spec_id"),
        "handoff.source_candidates": ListRule("handoff.source_candidates", "string"),
        "handoff.seed_artifacts": ListRule("handoff.seed_artifacts", "seed_artifact"),
        "handoff.blockers": ListRule("handoff.blockers", "string"),
    },
    "define-queue.yaml": {
        "entries": ListRule(
            "entries",
            "mapping",
            required=("spec_id", "feature_key", "title", "handoff_status", "downstream_mode", "package_shape", "source_candidates", "seed_artifacts", "define_target", "blockers"),
            enum_fields={"handoff_status": VALID_HANDOFF_STATUS, "downstream_mode": VALID_DOWNSTREAM_MODE, "package_shape": VALID_PACKAGE_SHAPE},
            regex_fields={"spec_id": SPEC_ID_RE, "feature_key": FEATURE_KEY_RE},
            list_fields={"source_candidates": "string", "seed_artifacts": "seed_artifact", "blockers": "string"},
            unique_by="spec_id",
        ),
    },
    "discovery-index.yaml": {
        "candidates": ListRule(
            "candidates",
            "mapping",
            required=("candidate_id", "title", "status", "candidate_doc", "frontier", "core_files", "triage_confidence", "boundary_risk", "suggested_next_step"),
            optional=("supporting_files", "provisional_feature_key", "duplicate_of"),
            enum_fields={"status": VALID_CANDIDATE_STATUS, "triage_confidence": VALID_CONFIDENCE, "boundary_risk": VALID_CONFIDENCE, "suggested_next_step": VALID_NEXT_STEP},
            regex_fields={"provisional_feature_key": FEATURE_KEY_RE},
            nullable_fields={"provisional_feature_key", "duplicate_of"},
            list_fields={"core_files": "string", "supporting_files": "string"},
            unique_by="candidate_id",
        ),
    },
    "discovery-state.json": {
        "frontier_queue": ListRule("frontier_queue", "string"),
        "completed_frontiers": ListRule("completed_frontiers", "string"),
        "blocked_frontiers": ListRule("blocked_frontiers", "string"),
        "frontier_history": ListRule(
            "frontier_history",
            "mapping",
            required=("iteration", "frontier", "files", "next_frontier", "status"),
            enum_fields={"status": VALID_FRONTIER_STATUS},
            nullable_fields={"next_frontier"},
            list_fields={"files": "string"},
        ),
    },
    "manifest.yaml": {
        "traceability.supporting_discovery_files": ListRule("traceability.supporting_discovery_files", "string"),
    },
    "prd.md": {
        "depends_on_features": ListRule("depends_on_features", "string"),
        "depends_on_specs": ListRule("depends_on_specs", "spec_id"),
    },
    "technical-design.md": {
        "project_types": ListRule("project_types", "string"),
        "depends_on_features": ListRule("depends_on_features", "string"),
        "depends_on_specs": ListRule("depends_on_specs", "spec_id"),
    },
    "spec-catalog.yaml": {
        "specs": ListRule(
            "specs",
            "mapping",
            required=("order", "order_hint", "spec_id", "feature_key", "title", "type", "classification", "depends_on_features", "depends_on_specs", "status", "feature_version"),
            regex_fields={"spec_id": SPEC_ID_RE, "feature_key": FEATURE_KEY_RE},
            enum_fields={"status": VALID_SPEC_STATUS},
            list_fields={"depends_on_features": "string", "depends_on_specs": "spec_id"},
            unique_by="spec_id",
        ),
    },
}


def artifact_name(path: Path) -> str:
    name = path.name
    if path.parent.name == "registry" and name.endswith(".yaml"):
        return "spec-registry-entry.yaml"
    return name[:-9] if name.endswith(".template") else name


def fail(message: str) -> None:
    raise ValueError(message)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, str]:
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.strip() == "---"), None)
    if start is None:
        fail("Markdown artifact has no YAML front matter")
    end = next((index for index, line in enumerate(lines[start + 1 :], start=start + 1) if line.strip() == "---"), None)
    if end is None:
        fail("Markdown artifact front matter is not closed")
    if yaml is None:
        fail("PyYAML is required for Markdown front matter")
    data = yaml.safe_load("\n".join(lines[start + 1 : end])) or {}
    if not isinstance(data, dict):
        fail("Markdown front matter must be a mapping")
    return data, "\n".join(lines[:start]), "\n".join(lines[end + 1 :])


def load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        if yaml is None:
            fail("PyYAML is required for YAML update payloads.")
        data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        fail("payload top-level value must be a mapping")
    updates = data.get("lists", data)
    if not isinstance(updates, dict):
        fail("payload `lists` value must be a mapping")
    return updates


def load_artifact(path: Path) -> tuple[dict[str, Any], tuple[str, str] | None]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        data = json.loads(text)
        markdown_parts = None
    elif suffix == ".md":
        data, prefix, body = split_frontmatter(text)
        markdown_parts = (prefix, body)
    else:
        if yaml is None:
            fail("PyYAML is required for YAML artifacts.")
        data = yaml.safe_load(text) or {}
        markdown_parts = None
    if not isinstance(data, dict):
        fail(f"{path}: top-level artifact value must be a mapping")
    return data, markdown_parts


def write_artifact(path: Path, data: dict[str, Any], markdown_parts: tuple[str, str] | None) -> None:
    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    if yaml is None:
        fail("PyYAML is required for YAML artifacts.")
    yaml_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=False)
    if suffix == ".md":
        prefix, body = markdown_parts or ("", "")
        leading = f"{prefix}\n" if prefix else ""
        path.write_text(f"{leading}---\n{yaml_text}---\n{body}\n", encoding="utf-8")
        return
    path.write_text(yaml_text, encoding="utf-8")


def get_parent(data: dict[str, Any], dotted_path: str) -> tuple[dict[str, Any], str]:
    parts = dotted_path.split(".")
    node: Any = data
    for part in parts[:-1]:
        if not isinstance(node, dict):
            fail(f"`{'.'.join(parts[:-1])}` is not a mapping")
        if part not in node or node[part] is None:
            node[part] = {}
        node = node[part]
    if not isinstance(node, dict):
        fail(f"`{'.'.join(parts[:-1])}` is not a mapping")
    return node, parts[-1]


def has_template_token(value: Any) -> bool:
    return isinstance(value, str) and bool(TEMPLATE_TOKEN_RE.search(value))


def validate_scalar(label: str, value: Any, item_type: str) -> None:
    if item_type == "string":
        if not isinstance(value, str) or not value.strip():
            fail(f"{label} must be a non-empty string")
        if has_template_token(value):
            fail(f"{label} contains an unresolved template token")
        return
    if item_type == "spec_id":
        if not isinstance(value, str) or not SPEC_ID_RE.fullmatch(value):
            fail(f"{label} must use canonical spec-YYYY-MM-DD-feature-key--ULID format")
        return
    if item_type == "task_id":
        if not isinstance(value, str) or not TASK_ID_RE.fullmatch(value):
            fail(f"{label} must use taskNNN format")
        return
    if item_type == "seed_artifact":
        if value not in VALID_SEED_ARTIFACT:
            fail(f"{label} must be one of {sorted(VALID_SEED_ARTIFACT)}")
        return
    fail(f"{label}: unsupported scalar type `{item_type}`")


def validate_nested_list(label: str, value: Any, item_type: str) -> None:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    for index, item in enumerate(value):
        validate_scalar(f"{label}[{index}]", item, item_type)


def is_nullish(value: Any) -> bool:
    return value in (None, "", "unknown")


def validate_mapping_item(rule: ListRule, item: Any, index: int) -> None:
    label = f"{rule.path}[{index}]"
    if not isinstance(item, dict):
        fail(f"{label} must be a mapping")
    for key in rule.required:
        if key not in item:
            fail(f"{label} missing required key `{key}`")
    if not rule.allow_extra:
        extra = sorted(set(item) - rule.allowed_keys)
        if extra:
            fail(f"{label} contains noncanonical key(s): {', '.join(extra)}")
    for key, value in item.items():
        value_label = f"{label}.{key}"
        if key in rule.nullable_fields and is_nullish(value):
            continue
        if has_template_token(value):
            fail(f"{value_label} contains an unresolved template token")
        if key in rule.enum_fields and value not in rule.enum_fields[key]:
            fail(f"{value_label} must be one of {sorted(rule.enum_fields[key])}")
        if key in rule.regex_fields and not is_nullish(value) and not rule.regex_fields[key].fullmatch(str(value)):
            fail(f"{value_label} has invalid format")
        if key in rule.list_fields:
            validate_nested_list(value_label, value, rule.list_fields[key])


def validate_list(rule: ListRule, value: Any) -> None:
    if not isinstance(value, list):
        fail(f"`{rule.path}` must be a list")
    seen: set[str] = set()
    for index, item in enumerate(value):
        if rule.item_type == "mapping":
            validate_mapping_item(rule, item, index)
            if rule.unique_by and isinstance(item, dict):
                unique_value = item.get(rule.unique_by)
                if not is_nullish(unique_value):
                    unique_text = str(unique_value)
                    if unique_text in seen:
                        fail(f"`{rule.path}` has duplicate `{rule.unique_by}` value `{unique_text}`")
                    seen.add(unique_text)
        else:
            validate_scalar(f"{rule.path}[{index}]", item, rule.item_type)


def apply_updates(artifact_path: Path, updates: dict[str, Any]) -> None:
    name = artifact_name(artifact_path)
    if name in GENERATED_VIEW_NAMES:
        fail(f"`{name}` is a generated projection; use render_registry_views.py instead of mutating it")
    rules = RULES.get(name)
    if not rules:
        fail(f"unsupported MAGO template-backed artifact `{name}`")
    unknown_paths = sorted(set(updates) - set(rules))
    if unknown_paths:
        fail(f"{name}: unsupported list path(s): {', '.join(unknown_paths)}")

    data, markdown_parts = load_artifact(artifact_path)
    for path, value in updates.items():
        rule = rules[path]
        validate_list(rule, value)
        parent, key = get_parent(data, path)
        parent[key] = value
    write_artifact(artifact_path, data, markdown_parts)


def print_schema(name: str | None) -> None:
    selected = {name: RULES[name]} if name else RULES
    for artifact, rules in selected.items():
        print(f"{artifact}:")
        for path, rule in rules.items():
            print(f"  {path}: {rule.item_type}")
            if rule.required:
                print(f"    required: {', '.join(rule.required)}")
            if rule.optional:
                print(f"    optional: {', '.join(rule.optional)}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Populate MAGO artifact list fields with canonical schema checks.")
    parser.add_argument("artifact", nargs="?", help="Artifact path to update.")
    parser.add_argument("--data", help="YAML or JSON payload containing a `lists` mapping.")
    parser.add_argument("--schema", action="store_true", help="Print supported list paths and item shapes.")
    parser.add_argument("--artifact-name", help="Artifact schema name for --schema, for example spec-catalog.yaml.")
    args = parser.parse_args(argv)

    try:
        if args.schema:
            if args.artifact_name and args.artifact_name not in RULES:
                fail(f"unsupported MAGO artifact `{args.artifact_name}`")
            print_schema(args.artifact_name)
            return 0
        if not args.artifact or not args.data:
            fail("artifact and --data are required unless --schema is used")
        artifact_path = Path(args.artifact).resolve()
        if "assets" in artifact_path.parts and "templates" in artifact_path.parts:
            fail("refusing to write directly to assets/templates; update a generated artifact instead")
        apply_updates(artifact_path, load_payload(Path(args.data).resolve()))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"OK: updated list fields in {Path(args.artifact).resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
