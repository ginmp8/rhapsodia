#!/usr/bin/env python3
"""Specialized lint for structured LLM JSON artifacts.

This tool validates JSON syntax, duplicate-key determinism, prompt/workflow hygiene,
security-sensitive values, and optional provider capability profiles. It is NOT a
normative JSON Schema validator. Use a conforming implementation of the declared
JSON Schema dialect for conformance claims.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SECRET_KEY_RE = re.compile(
    r"(^|_)(api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|private[_-]?key|client[_-]?secret|connection[_-]?string)($|_)",
    re.IGNORECASE,
)
API_CONTROL_KEYS = {
    "model", "temperature", "top_p", "max_tokens", "max_output_tokens",
    "timeout", "reasoning_effort",
}
SCHEMA_MARKERS = {
    "$schema", "$id", "$ref", "$defs", "definitions", "type", "properties",
    "allOf", "anyOf", "oneOf", "not", "if", "then", "else", "enum", "const",
}
SCHEMA_MAP_KEYS = {"$defs", "definitions", "properties", "patternProperties", "dependentSchemas"}
SCHEMA_SINGLE_KEYS = {
    "items", "contains", "additionalProperties", "unevaluatedProperties",
    "unevaluatedItems", "propertyNames", "not", "if", "then", "else",
    "additionalItems", "contentSchema",
}
SCHEMA_LIST_KEYS = {"prefixItems", "allOf", "anyOf", "oneOf"}


class DuplicateKeyError(ValueError):
    pass


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=unique_object)


def max_depth(value: Any, current: int = 0) -> int:
    if isinstance(value, dict):
        return max([current] + [max_depth(item, current + 1) for item in value.values()])
    if isinstance(value, list):
        return max([current] + [max_depth(item, current + 1) for item in value])
    return current


def walk_json(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk_json(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_json(item, f"{path}[{index}]")


def detect_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "schema"
    if isinstance(value, dict):
        if "steps" in value and ("workflow_id" in value or "workflow_version" in value):
            return "workflow"
        if SCHEMA_MARKERS.intersection(value.keys()):
            return "schema"
    return "prompt"


def schema_nodes(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    """Yield schema nodes without confusing property names with schema keywords."""
    if isinstance(value, bool):
        yield path, value
        return
    if not isinstance(value, dict):
        return
    yield path, value
    for key in SCHEMA_MAP_KEYS:
        child = value.get(key)
        if isinstance(child, dict):
            for name, sub in child.items():
                yield from schema_nodes(sub, f"{path}.{key}.{name}")
    for key in SCHEMA_SINGLE_KEYS:
        if key in value:
            yield from schema_nodes(value[key], f"{path}.{key}")
    for key in SCHEMA_LIST_KEYS:
        child = value.get(key)
        if isinstance(child, list):
            for index, sub in enumerate(child):
                yield from schema_nodes(sub, f"{path}.{key}[{index}]")


def schema_keyword_locations(value: Any, keywords: set[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path, node in schema_nodes(value):
        if isinstance(node, dict):
            for key in node.keys():
                if key in keywords:
                    findings.append({"path": f"{path}.{key}", "keyword": key})
    return findings


def validate_common(value: Any, errors: list[str], warnings: list[str]) -> list[str]:
    security_errors: list[str] = []
    depth = max_depth(value)
    if depth > 12:
        warnings.append(f"deep nesting detected: depth {depth}")
    for path, item in walk_json(value):
        if isinstance(item, dict):
            for key, child in item.items():
                if SECRET_KEY_RE.search(key) and child not in (None, "", "REDACTED", "<redacted>"):
                    message = f"possible secret value at {path}.{key}"
                    errors.append(message)
                    security_errors.append(message)
        if isinstance(item, str) and len(item) > 200_000:
            warnings.append(f"very large string at {path}: {len(item)} characters")
        if isinstance(item, list) and len(item) > 10_000:
            warnings.append(f"very large array at {path}: {len(item)} items")
    return security_errors


def validate_prompt(value: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(value, dict):
        warnings.append("structured prompt artifacts are usually clearer as a root object")
        return
    if not any(key in value for key in ("task", "objective", "instruction", "instructions")):
        warnings.append("no explicit task, objective, instruction, or instructions field")
    controls = sorted(API_CONTROL_KEYS.intersection(value.keys()))
    if controls:
        warnings.append(
            "API controls appear inside prompt data and may not configure runtime behavior: "
            + ", ".join(controls)
        )
    if len(value) == 1 and "prompt" in value and isinstance(value["prompt"], str):
        warnings.append("JSON wrapper adds little structure around a single prompt string")
    if "output_schema" in value:
        validate_schema_lint(value["output_schema"], errors, warnings, prefix="$.output_schema", standalone=False)


def validate_schema_lint(
    value: Any,
    errors: list[str],
    warnings: list[str],
    *,
    prefix: str = "$",
    standalone: bool = True,
) -> None:
    if isinstance(value, bool):
        return
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be a JSON Schema object or boolean")
        return
    if standalone and prefix == "$" and "$schema" not in value:
        warnings.append("standalone schema does not declare $schema; dialect interpretation may be implementation-defined")

    for path, node in schema_nodes(value, prefix):
        if isinstance(node, bool):
            continue
        if not isinstance(node, dict):
            errors.append(f"{path} must be a schema object or boolean")
            continue
        schema_type = node.get("type")
        properties = node.get("properties")
        if properties is not None and not isinstance(properties, dict):
            errors.append(f"{path}.properties must be an object")
        required = node.get("required")
        if required is not None:
            if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
                errors.append(f"{path}.required must be an array of strings")
            else:
                if len(required) != len(set(required)):
                    errors.append(f"{path}.required contains duplicate property names")
                if isinstance(properties, dict):
                    unknown = sorted(set(required) - set(properties))
                    if unknown:
                        errors.append(f"{path}.required references unknown properties: {', '.join(unknown)}")
        enum = node.get("enum")
        if enum is not None and (not isinstance(enum, list) or not enum):
            errors.append(f"{path}.enum must be a non-empty array")
        if schema_type == "array" and "items" not in node and "prefixItems" not in node:
            warnings.append(f"{path} array schema declares neither items nor prefixItems")
        if schema_type == "object" and isinstance(properties, dict) and "additionalProperties" not in node:
            warnings.append(f"{path} object schema does not state an additionalProperties policy")


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dependency in graph.get(node, []):
            cycle = visit(dependency)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def validate_workflow(value: Any, errors: list[str], warnings: list[str]) -> list[str]:
    workflow_errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)
        workflow_errors.append(message)

    if not isinstance(value, dict):
        fail("workflow root must be an object")
        return workflow_errors
    steps = value.get("steps")
    if not isinstance(steps, list) or not steps:
        fail("workflow steps must be a non-empty array")
        return workflow_errors
    ids: list[str] = []
    graph: dict[str, list[str]] = {}
    output_keys: list[str] = []
    for index, step in enumerate(steps):
        location = f"steps[{index}]"
        if not isinstance(step, dict):
            fail(f"{location} must be an object")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or not step_id.strip():
            fail(f"{location}.id must be a non-empty string")
            continue
        ids.append(step_id)
        capability = step.get("skill", step.get("capability"))
        if not isinstance(capability, str) or not capability.strip():
            fail(f"{location} must declare a non-empty skill or capability")
        for field in ("action", "instruction"):
            if not isinstance(step.get(field), str) or not step[field].strip():
                fail(f"{location}.{field} must be a non-empty string")
        dependencies = step.get("depends_on", [])
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            fail(f"{location}.depends_on must be an array of strings")
            dependencies = []
        graph[step_id] = dependencies
        output = step.get("output")
        if isinstance(output, dict) and isinstance(output.get("key"), str):
            output_keys.append(output["key"])
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    if duplicate_ids:
        fail("duplicate step ids: " + ", ".join(duplicate_ids))
    known = set(ids)
    for step_id, dependencies in graph.items():
        unknown = sorted(set(dependencies) - known)
        if unknown:
            fail(f"step {step_id} has unknown dependencies: {', '.join(unknown)}")
        if step_id in dependencies:
            fail(f"step {step_id} depends on itself")
    if not duplicate_ids:
        cycle = find_cycle(graph)
        if cycle:
            fail("dependency cycle: " + " -> ".join(cycle))
    duplicate_outputs = sorted({item for item in output_keys if output_keys.count(item) > 1})
    if duplicate_outputs:
        warnings.append("duplicate output keys: " + ", ".join(duplicate_outputs))
    execution = value.get("execution", {})
    if isinstance(execution, dict):
        for field in ("maximum_parallelism", "maximum_attempts_per_step"):
            number = execution.get(field)
            if number is not None and (not isinstance(number, int) or isinstance(number, bool) or number < 1):
                fail(f"execution.{field} must be an integer of at least 1")
    return workflow_errors


def validate_provider_profile(schema: Any, profile: Any) -> tuple[str, list[dict[str, Any]], list[str]]:
    findings: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not isinstance(profile, dict):
        return "fail", [{"code": "profile/not-object", "path": "$", "detail": "provider profile must be an object"}], warnings
    if profile.get("profile_version") != 1:
        findings.append({"code": "profile/version", "path": "$.profile_version", "detail": "expected profile_version 1"})
    if not str(profile.get("verified_at", "")).strip():
        warnings.append("provider profile has no verified_at date")
    unsupported = profile.get("unsupported_keywords", [])
    if not isinstance(unsupported, list) or not all(isinstance(item, str) for item in unsupported):
        findings.append({"code": "profile/unsupported-keywords", "path": "$.unsupported_keywords", "detail": "must be an array of strings"})
        unsupported = []
    for item in schema_keyword_locations(schema, set(unsupported)):
        findings.append({"code": "provider/unsupported-keyword", **item, "detail": "canonical constraint is not supported by this capability profile"})

    requirements = profile.get("requirements", {})
    if isinstance(requirements, dict):
        root_type = requirements.get("root_type")
        if root_type is not None and isinstance(schema, dict) and schema.get("type") != root_type:
            findings.append({"code": "provider/root-type", "path": "$.type", "detail": f"profile requires root type {root_type!r}"})
        require_closed = requirements.get("require_additional_properties_false") is True
        require_all = requirements.get("require_all_properties_required") is True
        for path, node in schema_nodes(schema):
            if not isinstance(node, dict):
                continue
            props = node.get("properties")
            if isinstance(props, dict):
                if require_closed and node.get("additionalProperties") is not False:
                    findings.append({"code": "provider/object-closure", "path": path, "detail": "profile requires additionalProperties: false"})
                if require_all:
                    required = node.get("required")
                    if not isinstance(required, list) or set(required) != set(props):
                        findings.append({"code": "provider/all-properties-required", "path": path, "detail": "profile requires every declared property to be listed in required"})
    return ("fail" if findings else "pass"), findings, warnings


def run(path: Path, kind: str = "auto", provider_profile: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        value = load_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError, DuplicateKeyError, OSError) as exc:
        return {
            "file": str(path), "kind": kind, "status": "fail", "syntax_status": "fail",
            "specialized_lint_status": "not-run", "normative_schema_validation": "not-run",
            "provider_compatibility_status": "not-run", "semantic_validation_status": "not-run",
            "security_authority_status": "not-run", "workflow_status": "not-run",
            "errors": [str(exc)], "warnings": [], "provider_findings": [],
        }

    resolved_kind = detect_kind(value) if kind == "auto" else kind
    security_errors = validate_common(value, errors, warnings)
    workflow_errors: list[str] = []
    if resolved_kind == "prompt":
        validate_prompt(value, errors, warnings)
    elif resolved_kind == "schema":
        validate_schema_lint(value, errors, warnings)
    elif resolved_kind == "workflow":
        workflow_errors = validate_workflow(value, errors, warnings)
    else:
        errors.append(f"unknown kind: {resolved_kind}")

    provider_status = "not-run"
    provider_findings: list[dict[str, Any]] = []
    if provider_profile is not None:
        if resolved_kind != "schema":
            warnings.append("provider profile supplied for a non-schema artifact; compatibility check not run")
        else:
            try:
                profile = load_json(provider_profile)
                provider_status, provider_findings, profile_warnings = validate_provider_profile(value, profile)
                warnings.extend(profile_warnings)
            except Exception as exc:
                provider_status = "fail"
                provider_findings = [{"code": "profile/read-error", "path": "$", "detail": str(exc)}]

    lint_status = "fail" if errors else ("pass-with-warnings" if warnings else "pass")
    overall_fail = bool(errors) or provider_status == "fail"
    overall_status = "fail" if overall_fail else ("pass-with-warnings" if warnings else "pass")
    return {
        "file": str(path),
        "kind": resolved_kind,
        "status": overall_status,
        "syntax_status": "pass",
        "specialized_lint_status": lint_status,
        "normative_schema_validation": "not-run" if resolved_kind == "schema" else "not-applicable",
        "provider_compatibility_status": provider_status,
        "semantic_validation_status": "not-run",
        "security_authority_status": "fail" if security_errors else "pass",
        "workflow_status": ("fail" if workflow_errors else "pass") if resolved_kind == "workflow" else "not-applicable",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "provider_findings": provider_findings,
    }


def self_test() -> int:
    failures: list[str] = []
    schema_errors: list[str] = []
    schema_warnings: list[str] = []
    validate_schema_lint(True, schema_errors, schema_warnings)
    if schema_errors:
        failures.append(f"boolean schema rejected: {schema_errors}")
    ref_errors: list[str] = []
    ref_warnings: list[str] = []
    validate_schema_lint({"$schema": "https://json-schema.org/draft/2020-12/schema", "$ref": "#/$defs/x", "$defs": {"x": {"type": "string"}}}, ref_errors, ref_warnings)
    if any("explicit type" in item for item in ref_warnings):
        failures.append("$ref-only schema received explicit-type warning")
    wf_errors: list[str] = []
    wf_warnings: list[str] = []
    validate_workflow({"workflow_version": "1.0.0", "workflow_id": "t", "steps": [{"id": "a", "skill": "x", "action": "run", "instruction": "Run.", "depends_on": []}]}, wf_errors, wf_warnings)
    if wf_errors:
        failures.append(f"valid workflow rejected: {wf_errors}")
    print(json.dumps({"status": "fail" if failures else "pass", "failures": failures}, indent=2))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="JSON artifacts")
    parser.add_argument("--kind", choices=["auto", "prompt", "schema", "workflow"], default="auto")
    parser.add_argument("--provider-profile", help="Capability profile JSON for schema compatibility checks")
    parser.add_argument("--report", help="Write combined JSON report")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.files:
        parser.error("provide at least one JSON file or use --self-test")
    profile = Path(args.provider_profile).resolve() if args.provider_profile else None
    reports = [run(Path(name).resolve(), args.kind, profile) for name in args.files]
    combined = {"status": "fail" if any(item["status"] == "fail" for item in reports) else "pass", "results": reports}
    rendered = json.dumps(combined, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 1 if combined["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
