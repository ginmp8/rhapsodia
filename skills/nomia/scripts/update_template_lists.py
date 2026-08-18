#!/usr/bin/env python3
"""Populate list fields in nomia template-backed artifacts with schema checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nomia_utils import SPEC_ID_RE

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_./:][a-z0-9]+)*$")
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
    bool_fields: set[str] = field(default_factory=set)
    unique_by: str | None = None
    allow_extra: bool = False

    @property
    def allowed_keys(self) -> set[str]:
        return set(self.required) | set(self.optional)


VALID_PRIORITY = {"unknown", "low", "medium", "high", "urgent"}
VALID_URGENCY = {"unknown", "low", "medium", "high", "immediate"}
VALID_IMPACT = {"unknown", "low", "medium", "high", "critical"}
VALID_RISK = {"unknown", "low", "medium", "high", "critical"}
VALID_STATE = {"unknown", "intake", "triage", "planned", "in_progress", "blocked", "at_risk", "done", "canceled"}
VALID_CONFIDENCE = {"unknown", "low", "medium", "high"}
VALID_HORIZONS = {"unknown", "now", "next", "later", "future"}
VALID_COMMITMENTS = {"unknown", "committed", "targeted", "exploratory", "parking_lot"}
VALID_HANDOFF_STATUS = {"unknown", "draft", "ready", "blocked", "parked", "accepted"}
VALID_MAGO_MODES = {"unknown", "define", "refine", "split"}


RULES: dict[str, dict[str, ListRule]] = {
    "ops.yaml": {
        "ownership.stakeholders": ListRule("ownership.stakeholders", "string"),
        "ownership.watchers": ListRule("ownership.watchers", "string"),
        "status.inferred.evidence": ListRule("status.inferred.evidence", "string"),
        "blockers": ListRule(
            "blockers",
            "mapping",
            required=("id", "summary"),
            optional=("owner", "needed_by"),
            regex_fields={"id": SLUG_RE},
            nullable_fields={"owner", "needed_by"},
            unique_by="id",
        ),
        "risks": ListRule(
            "risks",
            "mapping",
            required=("id", "summary", "severity"),
            optional=("owner",),
            enum_fields={"severity": VALID_RISK},
            regex_fields={"id": SLUG_RE},
            nullable_fields={"owner"},
            unique_by="id",
        ),
        "replanning": ListRule(
            "replanning",
            "mapping",
            required=("date", "changed_fields", "reason", "impact"),
            optional=("from", "to", "decision_maker"),
            list_fields={"changed_fields": "string"},
            nullable_fields={"from", "to", "decision_maker"},
        ),
        "tags": ListRule("tags", "string"),
        "repos.candidate_impacted": ListRule("repos.candidate_impacted", "string"),
        "links.mago": ListRule("links.mago", "string"),
        "links.magia": ListRule("links.magia", "string"),
        "links.external": ListRule("links.external", "string"),
    },
    "portfolio.yaml": {
        "items": ListRule(
            "items",
            "mapping",
            required=("spec_id", "feature_key", "title", "owner", "state", "target_date", "priority", "urgency", "impact", "risk", "confidence", "candidate_impacted_repos", "source"),
            optional=(),
            enum_fields={
                "state": VALID_STATE,
                "priority": VALID_PRIORITY,
                "urgency": VALID_URGENCY,
                "impact": VALID_IMPACT,
                "risk": VALID_RISK,
                "confidence": VALID_CONFIDENCE,
            },
            regex_fields={"spec_id": SPEC_ID_RE, "feature_key": FEATURE_KEY_RE},
            nullable_fields={"spec_id", "target_date"},
            list_fields={"candidate_impacted_repos": "string"},
            unique_by="spec_id",
        ),
        "blocked": ListRule(
            "blocked",
            "mapping",
            required=("id", "spec_id", "feature_key", "summary", "owner", "needed_by"),
            regex_fields={"id": SLUG_RE, "spec_id": SPEC_ID_RE, "feature_key": FEATURE_KEY_RE},
            nullable_fields={"spec_id", "needed_by"},
            unique_by="id",
        ),
        "risks": ListRule(
            "risks",
            "mapping",
            required=("id", "summary", "severity", "owner", "mitigation"),
            enum_fields={"severity": VALID_RISK},
            regex_fields={"id": SLUG_RE},
            nullable_fields={"owner", "mitigation"},
            unique_by="id",
        ),
        "replans": ListRule(
            "replans",
            "mapping",
            required=("spec_id", "feature_key", "date", "summary", "impact"),
            regex_fields={"spec_id": SPEC_ID_RE, "feature_key": FEATURE_KEY_RE},
            nullable_fields={"spec_id"},
        ),
        "flags.blocked": ListRule("flags.blocked", "string"),
        "flags.overdue": ListRule("flags.overdue", "string"),
        "flags.replanned": ListRule("flags.replanned", "string"),
        "flags.missing_owner": ListRule("flags.missing_owner", "string"),
        "flags.at_risk": ListRule("flags.at_risk", "string"),
        "flags.multi_repo": ListRule("flags.multi_repo", "string"),
    },
    "roadmap.yaml": {
        "goals": ListRule("goals", "string"),
        "outcomes": ListRule("outcomes", "string"),
        "themes": ListRule("themes", "string"),
        "stakeholders": ListRule("stakeholders", "string"),
        "constraints": ListRule("constraints", "string"),
        "assumptions": ListRule("assumptions", "string"),
        "success_measures": ListRule("success_measures", "string"),
        "risks": ListRule("risks", "string"),
        "features": ListRule(
            "features",
            "mapping",
            required=("feature_key", "name", "problem", "outcome", "horizon", "commitment", "confidence", "dependencies", "ready_for_spec", "candidate_spec_id"),
            optional=("scope_summary", "mvp_boundary", "later_phases", "non_goals", "stakeholders", "risks", "notes", "source_links"),
            enum_fields={"horizon": VALID_HORIZONS, "commitment": VALID_COMMITMENTS, "confidence": VALID_CONFIDENCE},
            regex_fields={"feature_key": FEATURE_KEY_RE, "candidate_spec_id": SPEC_ID_RE},
            nullable_fields={"candidate_spec_id", "scope_summary", "notes"},
            bool_fields={"ready_for_spec"},
            list_fields={
                "dependencies": "string",
                "mvp_boundary": "string",
                "later_phases": "string",
                "non_goals": "string",
                "stakeholders": "string",
                "risks": "string",
                "source_links": "string",
            },
            unique_by="feature_key",
        ),
    },
    "feature-map.yaml": {
        "features": ListRule(
            "features",
            "mapping",
            required=("feature_key", "ready_for_spec", "candidate_spec_id", "title", "scope_summary", "dependencies", "recommended_mago_mode"),
            optional=("handoff_status", "source_summary", "mago_inputs", "notes"),
            enum_fields={"recommended_mago_mode": VALID_MAGO_MODES, "handoff_status": VALID_HANDOFF_STATUS},
            regex_fields={"feature_key": FEATURE_KEY_RE, "candidate_spec_id": SPEC_ID_RE},
            nullable_fields={"candidate_spec_id", "title", "scope_summary", "source_summary", "notes"},
            bool_fields={"ready_for_spec"},
            list_fields={"dependencies": "string", "mago_inputs": "string"},
            unique_by="feature_key",
        ),
    },
}


def artifact_name(path: Path) -> str:
    name = path.name
    return name[:-9] if name.endswith(".template") else name


def fail(message: str) -> None:
    raise ValueError(message)


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


def load_artifact(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        if yaml is None:
            fail("PyYAML is required for YAML artifacts.")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        fail(f"{path}: top-level artifact value must be a mapping")
    return data


def write_artifact(path: Path, data: dict[str, Any]) -> None:
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    if yaml is None:
        fail("PyYAML is required for YAML artifacts.")
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


def validate_string(label: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    if has_template_token(value):
        fail(f"{label} contains an unresolved template token")


def validate_nested_list(label: str, value: Any, item_type: str) -> None:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    for index, item in enumerate(value):
        if item_type == "string":
            validate_string(f"{label}[{index}]", item)
        else:
            fail(f"{label}: unsupported nested list item type `{item_type}`")


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
        if key in rule.regex_fields and not rule.regex_fields[key].fullmatch(str(value)):
            fail(f"{value_label} has invalid format")
        if key in rule.bool_fields and not isinstance(value, bool):
            fail(f"{value_label} must be a boolean")
        if key in rule.list_fields:
            validate_nested_list(value_label, value, rule.list_fields[key])


def validate_list(rule: ListRule, value: Any) -> None:
    if not isinstance(value, list):
        fail(f"`{rule.path}` must be a list")
    seen: set[str] = set()
    for index, item in enumerate(value):
        if rule.item_type == "string":
            validate_string(f"{rule.path}[{index}]", item)
        elif rule.item_type == "mapping":
            validate_mapping_item(rule, item, index)
            if rule.unique_by and isinstance(item, dict):
                unique_value = item.get(rule.unique_by)
                if not is_nullish(unique_value):
                    unique_text = str(unique_value)
                    if unique_text in seen:
                        fail(f"`{rule.path}` has duplicate `{rule.unique_by}` value `{unique_text}`")
                    seen.add(unique_text)
        else:
            fail(f"`{rule.path}` has unsupported item type `{rule.item_type}`")


def apply_updates(artifact_path: Path, updates: dict[str, Any]) -> None:
    name = artifact_name(artifact_path)
    rules = RULES.get(name)
    if not rules:
        fail(f"unsupported nomia template-backed artifact `{name}`")
    unknown_paths = sorted(set(updates) - set(rules))
    if unknown_paths:
        fail(f"{name}: unsupported list path(s): {', '.join(unknown_paths)}")

    data = load_artifact(artifact_path)
    for path, value in updates.items():
        rule = rules[path]
        validate_list(rule, value)
        parent, key = get_parent(data, path)
        parent[key] = value
    write_artifact(artifact_path, data)


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
    parser = argparse.ArgumentParser(description="Populate nomia artifact list fields with canonical schema checks.")
    parser.add_argument("artifact", nargs="?", help="Artifact path to update.")
    parser.add_argument("--data", help="YAML or JSON payload containing a `lists` mapping.")
    parser.add_argument("--schema", action="store_true", help="Print supported list paths and item shapes.")
    parser.add_argument("--artifact-name", help="Artifact schema name for --schema, for example roadmap.yaml.")
    args = parser.parse_args(argv)

    try:
        if args.schema:
            if args.artifact_name and args.artifact_name not in RULES:
                fail(f"unsupported nomia artifact `{args.artifact_name}`")
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
