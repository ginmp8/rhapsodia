#!/usr/bin/env python3
"""Validate JSON prompts, JSON Schemas, and multi-skill workflow manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SECRET_KEY_RE = re.compile(
    r"(^|_)(api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|private[_-]?key|client[_-]?secret|connection[_-]?string)($|_)",
    re.IGNORECASE,
)
API_CONTROL_KEYS = {
    "model",
    "temperature",
    "top_p",
    "max_tokens",
    "max_output_tokens",
    "timeout",
    "reasoning_effort",
}


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


def walk(value: Any, path: str = "$"):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")


def detect_kind(value: Any) -> str:
    if isinstance(value, dict):
        if "steps" in value and ("workflow_id" in value or "workflow_version" in value):
            return "workflow"
        if value.get("$schema") or (value.get("type") and "properties" in value):
            return "schema"
    return "prompt"


def validate_common(value: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(value, (dict, list)):
        errors.append("root must be a JSON object or array")
        return
    depth = max_depth(value)
    if depth > 10:
        warnings.append(f"deep nesting detected: depth {depth}")
    for path, item in walk(value):
        if isinstance(item, dict):
            for key, child in item.items():
                if SECRET_KEY_RE.search(key):
                    if child not in (None, "", "REDACTED", "<redacted>"):
                        errors.append(f"possible secret value at {path}.{key}")
        if isinstance(item, str) and len(item) > 200_000:
            warnings.append(f"very large string at {path}: {len(item)} characters")
        if isinstance(item, list) and len(item) > 10_000:
            warnings.append(f"very large array at {path}: {len(item)} items")


def validate_prompt(value: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(value, dict):
        warnings.append("prompt artifacts are usually clearer as a root object")
        return
    if not any(key in value for key in ("task", "objective", "instruction", "instructions")):
        warnings.append("no explicit task, objective, instruction, or instructions field")
    controls = sorted(API_CONTROL_KEYS.intersection(value.keys()))
    if controls:
        warnings.append(
            "API controls appear inside the prompt root and may not affect runtime configuration: "
            + ", ".join(controls)
        )
    if len(value) == 1 and "prompt" in value and isinstance(value["prompt"], str):
        warnings.append("JSON wrapper adds little structure around a single prompt string")
    if "output_schema" in value and isinstance(value["output_schema"], dict):
        validate_schema(value["output_schema"], errors, warnings, prefix="output_schema")


def validate_schema(
    value: Any,
    errors: list[str],
    warnings: list[str],
    prefix: str = "$",
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    schema_type = value.get("type")
    if schema_type is None:
        warnings.append(f"{prefix} has no explicit type")
    if schema_type == "object":
        properties = value.get("properties")
        if not isinstance(properties, dict):
            errors.append(f"{prefix}.properties must be an object for object schemas")
            return
        required = value.get("required", [])
        if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
            errors.append(f"{prefix}.required must be an array of strings")
        else:
            unknown = sorted(set(required) - set(properties))
            if unknown:
                errors.append(f"{prefix}.required references unknown properties: {', '.join(unknown)}")
        if "additionalProperties" not in value:
            warnings.append(f"{prefix} does not declare additionalProperties")
        for key, child in properties.items():
            validate_schema(child, errors, warnings, prefix=f"{prefix}.properties.{key}")
    elif schema_type == "array":
        if "items" not in value:
            errors.append(f"{prefix}.items is required for array schemas")
        else:
            validate_schema(value["items"], errors, warnings, prefix=f"{prefix}.items")
    enum = value.get("enum")
    if enum is not None and (not isinstance(enum, list) or not enum):
        errors.append(f"{prefix}.enum must be a non-empty array")


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


def validate_workflow(value: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("workflow root must be an object")
        return
    steps = value.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("workflow steps must be a non-empty array")
        return
    ids: list[str] = []
    graph: dict[str, list[str]] = {}
    output_keys: list[str] = []
    for index, step in enumerate(steps):
        location = f"steps[{index}]"
        if not isinstance(step, dict):
            errors.append(f"{location} must be an object")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or not step_id.strip():
            errors.append(f"{location}.id must be a non-empty string")
            continue
        ids.append(step_id)
        for field in ("skill", "action", "instruction"):
            if not isinstance(step.get(field), str) or not step[field].strip():
                errors.append(f"{location}.{field} must be a non-empty string")
        dependencies = step.get("depends_on", [])
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            errors.append(f"{location}.depends_on must be an array of strings")
            dependencies = []
        graph[step_id] = dependencies
        output = step.get("output")
        if isinstance(output, dict) and isinstance(output.get("key"), str):
            output_keys.append(output["key"])
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    if duplicate_ids:
        errors.append("duplicate step ids: " + ", ".join(duplicate_ids))
    known = set(ids)
    for step_id, dependencies in graph.items():
        unknown = sorted(set(dependencies) - known)
        if unknown:
            errors.append(f"step {step_id} has unknown dependencies: {', '.join(unknown)}")
        if step_id in dependencies:
            errors.append(f"step {step_id} depends on itself")
    if not duplicate_ids:
        cycle = find_cycle(graph)
        if cycle:
            errors.append("dependency cycle: " + " -> ".join(cycle))
    duplicate_outputs = sorted({item for item in output_keys if output_keys.count(item) > 1})
    if duplicate_outputs:
        warnings.append("duplicate output keys: " + ", ".join(duplicate_outputs))
    execution = value.get("execution", {})
    if isinstance(execution, dict):
        parallelism = execution.get("maximum_parallelism")
        if isinstance(parallelism, int) and parallelism < 1:
            errors.append("execution.maximum_parallelism must be at least 1")


def run(path: Path, kind: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        value = load_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError, DuplicateKeyError, OSError) as exc:
        return {"file": str(path), "kind": kind, "status": "fail", "errors": [str(exc)], "warnings": []}
    resolved_kind = detect_kind(value) if kind == "auto" else kind
    validate_common(value, errors, warnings)
    if resolved_kind == "prompt":
        validate_prompt(value, errors, warnings)
    elif resolved_kind == "schema":
        validate_schema(value, errors, warnings)
    elif resolved_kind == "workflow":
        validate_workflow(value, errors, warnings)
    status = "fail" if errors else ("pass-with-warnings" if warnings else "pass")
    return {
        "file": str(path),
        "kind": resolved_kind,
        "status": status,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def self_test() -> int:
    fixtures = {
        "prompt": {"task": "classify", "input": {"text": "hello"}},
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"result": {"type": "string"}},
            "required": ["result"],
        },
        "workflow": {
            "workflow_version": "1.0.0",
            "workflow_id": "test",
            "steps": [
                {
                    "id": "one",
                    "skill": "example-skill",
                    "action": "run",
                    "instruction": "Run the example.",
                    "depends_on": [],
                }
            ],
        },
    }
    failures: list[str] = []
    for kind, value in fixtures.items():
        errors: list[str] = []
        warnings: list[str] = []
        validate_common(value, errors, warnings)
        if kind == "prompt":
            validate_prompt(value, errors, warnings)
        elif kind == "schema":
            validate_schema(value, errors, warnings)
        else:
            validate_workflow(value, errors, warnings)
        if errors:
            failures.append(f"{kind}: {errors}")
    print(json.dumps({"status": "fail" if failures else "pass", "failures": failures}, indent=2))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="JSON files to validate")
    parser.add_argument("--kind", choices=["auto", "prompt", "schema", "workflow"], default="auto")
    parser.add_argument("--report", help="Write the combined JSON report to this path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.files:
        parser.error("provide at least one JSON file or use --self-test")
    reports = [run(Path(name).resolve(), args.kind) for name in args.files]
    combined = {
        "status": "fail" if any(item["status"] == "fail" for item in reports) else "pass",
        "results": reports,
    }
    rendered = json.dumps(combined, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 1 if combined["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
