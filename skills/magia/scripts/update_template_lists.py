#!/usr/bin/env python3
"""Reject generic updates to shared planning artifacts and reserve MAGIA-owned schema updates."""

from __future__ import annotations

import argparse
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
SPEC_ID_RE = re.compile(r"^spec\d{3}$")
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


@dataclass(frozen=True)
class FieldRule:
    path: str
    enum_values: set[str] | None = None
    regex: re.Pattern[str] | None = None
    nullable: bool = False


VALID_BOARD_STATUS = {"planned", "in_progress", "done", "cancelled"}
VALID_SPEC_STATUS = {"planned", "in_progress", "blocked", "done", "cancelled"}
VALID_PHASE = {"define", "execute", "done"}


PLANNING_ARTIFACTS = {"manifest.yaml", "spec-catalog.yaml", "tasks.md", "notes.md", "validation.md", "prd.md", "technical-design.md"}

# MAGIA intentionally has no generic list/field updater for MAGO-owned planning
# artifacts. Execution-state updates for manifest.yaml/spec-catalog.yaml must go
# through sync_execution_state.py, heal_execution_state.py, close_execution_state.py,
# and validate_execution_state.py, which are narrow, evidence-backed workflows.
RULES: dict[str, dict[str, ListRule]] = {}
FIELD_RULES: dict[str, dict[str, FieldRule]] = {}


def artifact_name(path: Path) -> str:
    name = path.name
    return name[:-9] if name.endswith(".template") else name


def fail(message: str) -> None:
    raise ValueError(message)


def load_payload(path: Path) -> dict[str, Any]:
    if yaml is None:
        fail("PyYAML is required for MAGIA update payloads.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        fail("payload top-level value must be a mapping")

    if "lists" in data or "fields" in data:
        updates: dict[str, Any] = {}
        for section_name in ("fields", "lists"):
            section = data.get(section_name, {})
            if section is None:
                section = {}
            if not isinstance(section, dict):
                fail(f"payload `{section_name}` value must be a mapping")
            duplicates = sorted(set(updates) & set(section))
            if duplicates:
                fail(f"payload repeats update path(s): {', '.join(duplicates)}")
            updates.update(section)
    else:
        updates = data

    if not isinstance(updates, dict):
        fail("payload updates value must be a mapping")
    return updates


def load_artifact(path: Path) -> dict[str, Any]:
    if yaml is None:
        fail("PyYAML is required for MAGIA YAML artifacts.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        fail(f"{path}: top-level artifact value must be a mapping")
    return data


def write_artifact(path: Path, data: dict[str, Any]) -> None:
    if yaml is None:
        fail("PyYAML is required for MAGIA YAML artifacts.")
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


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
            fail(f"{label} must use specNNN format")
        return
    if item_type == "task_id":
        if not isinstance(value, str) or not TASK_ID_RE.fullmatch(value):
            fail(f"{label} must use taskNNN format")
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


def validate_field(rule: FieldRule, value: Any) -> None:
    label = f"`{rule.path}`"
    if rule.nullable and is_nullish(value):
        return
    if has_template_token(value):
        fail(f"{label} contains an unresolved template token")
    if rule.enum_values is not None and (not isinstance(value, str) or value not in rule.enum_values):
        fail(f"{label} must be one of {sorted(rule.enum_values)}")
    if rule.regex is not None and not rule.regex.fullmatch(str(value)):
        fail(f"{label} has invalid format")


def apply_updates(artifact_path: Path, updates: dict[str, Any]) -> None:
    name = artifact_name(artifact_path)
    list_rules = RULES.get(name, {})
    field_rules = FIELD_RULES.get(name, {})
    if name in PLANNING_ARTIFACTS:
        fail(
            f"`{name}` is MAGO-owned planning structure. MAGIA may update only narrow execution-state fields through "
            "sync_execution_state.py, heal_execution_state.py, or close_execution_state.py."
        )
    if not list_rules and not field_rules:
        fail(f"unsupported MAGIA template-backed artifact `{name}`")
    supported_paths = set(list_rules) | set(field_rules)
    unknown_paths = sorted(set(updates) - supported_paths)
    if unknown_paths:
        fail(f"{name}: unsupported update path(s): {', '.join(unknown_paths)}")

    data = load_artifact(artifact_path)
    for path, value in updates.items():
        if path in list_rules:
            rule = list_rules[path]
            validate_list(rule, value)
        else:
            rule = field_rules[path]
            validate_field(rule, value)
        parent, key = get_parent(data, path)
        parent[key] = value
    write_artifact(artifact_path, data)


def print_schema(name: str | None) -> None:
    artifacts = [name] if name else sorted(set(RULES) | set(FIELD_RULES))
    for artifact in artifacts:
        print(f"{artifact}:")
        for path, rule in FIELD_RULES.get(artifact, {}).items():
            print(f"  {path}: field")
            if rule.enum_values:
                print(f"    enum: {', '.join(sorted(rule.enum_values))}")
        for path, rule in RULES.get(artifact, {}).items():
            print(f"  {path}: {rule.item_type}")
            if rule.required:
                print(f"    required: {', '.join(rule.required)}")
            if rule.optional:
                print(f"    optional: {', '.join(rule.optional)}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Reject generic planning-artifact updates and show supported MAGIA-owned schema updates.")
    parser.add_argument("artifact", nargs="?", help="Artifact path to update.")
    parser.add_argument("--data", help="YAML payload containing `fields` and/or `lists` mappings.")
    parser.add_argument("--schema", action="store_true", help="Print supported update paths and item shapes.")
    parser.add_argument("--artifact-name", help="Artifact schema name for --schema.")
    args = parser.parse_args(argv)

    try:
        if args.schema:
            if args.artifact_name in PLANNING_ARTIFACTS:
                fail(
                    f"`{args.artifact_name}` is MAGO-owned planning structure; use MAGIA execution-state scripts for evidence-backed state sync"
                )
            if args.artifact_name and args.artifact_name not in RULES and args.artifact_name not in FIELD_RULES:
                fail(f"unsupported MAGIA artifact `{args.artifact_name}`")
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

    print(f"OK: updated fields in {Path(args.artifact).resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
