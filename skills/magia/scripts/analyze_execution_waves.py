#!/usr/bin/env python3
"""Conservatively classify explicit task graphs into safe execution waves."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import PurePosixPath, Path
from typing import Any


def normalize_path(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or value.strip() in {"", "."}:
        raise ValueError(f"invalid write path: {value}")
    return path.as_posix()


def paths_overlap(left: str, right: str) -> bool:
    a = PurePosixPath(left).parts
    b = PurePosixPath(right).parts
    limit = min(len(a), len(b))
    return a[:limit] == b[:limit]


def load_tasks(data: Any) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        return [], ["root must contain a tasks list"]
    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(data["tasks"]):
        label = f"tasks[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{label} must be an object")
            continue
        task_id = raw.get("id")
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"{label} requires a non-empty id")
            continue
        if task_id in seen:
            errors.append(f"duplicate task id: {task_id}")
            continue
        seen.add(task_id)
        depends = raw.get("depends_on", [])
        write_paths = raw.get("write_paths", [])
        surfaces = raw.get("contract_surfaces", [])
        if not isinstance(depends, list) or not all(isinstance(x, str) and x for x in depends):
            errors.append(f"{task_id}: depends_on must be a string list")
            depends = []
        if not isinstance(write_paths, list) or not all(isinstance(x, str) for x in write_paths):
            errors.append(f"{task_id}: write_paths must be a string list")
            write_paths = []
        normalized: list[str] = []
        for value in write_paths:
            try:
                normalized.append(normalize_path(value))
            except ValueError as exc:
                errors.append(f"{task_id}: {exc}")
        if not isinstance(surfaces, list) or not all(isinstance(x, str) and x.strip() for x in surfaces):
            errors.append(f"{task_id}: contract_surfaces must be a non-empty-string list")
            surfaces = []
        tasks.append({
            "id": task_id,
            "depends_on": list(dict.fromkeys(depends)),
            "parallel": raw.get("parallel") is True,
            "write_paths": sorted(set(normalized)),
            "contract_surfaces": sorted(set(surfaces)),
            "input_order": index,
        })
    ids = {task["id"] for task in tasks}
    for task in tasks:
        for dep in task["depends_on"]:
            if dep not in ids:
                errors.append(f"{task['id']}: unknown dependency {dep}")
            if dep == task["id"]:
                errors.append(f"{task['id']}: self dependency")
    return tasks, errors


def topological_layers(tasks: list[dict[str, Any]]) -> tuple[list[list[dict[str, Any]]], list[str]]:
    by_id = {task["id"]: task for task in tasks}
    indegree = {task["id"]: 0 for task in tasks}
    children: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        for dep in task["depends_on"]:
            if dep in by_id:
                indegree[task["id"]] += 1
                children[dep].append(task["id"])
    ready = deque(sorted((task for task in tasks if indegree[task["id"]] == 0), key=lambda x: x["input_order"]))
    layers: list[list[dict[str, Any]]] = []
    processed = 0
    while ready:
        current = list(ready)
        ready.clear()
        layers.append(current)
        processed += len(current)
        next_ids: list[str] = []
        for task in current:
            for child in children[task["id"]]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    next_ids.append(child)
        for task_id in sorted(next_ids, key=lambda x: by_id[x]["input_order"]):
            ready.append(by_id[task_id])
    if processed != len(tasks):
        remaining = sorted(task_id for task_id, degree in indegree.items() if degree > 0)
        return [], [f"dependency cycle detected: {', '.join(remaining)}"]
    return layers, []


def layer_conflicts(layer: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    for task in layer:
        if not task["parallel"]:
            reasons.append(f"{task['id']}: explicit parallel permission missing")
        if not task["write_paths"]:
            reasons.append(f"{task['id']}: write scope missing")
    for index, left in enumerate(layer):
        for right in layer[index + 1:]:
            for a in left["write_paths"]:
                for b in right["write_paths"]:
                    if paths_overlap(a, b):
                        reasons.append(f"{left['id']} and {right['id']}: overlapping write paths {a} / {b}")
            shared = sorted(set(left["contract_surfaces"]) & set(right["contract_surfaces"]))
            if shared:
                reasons.append(f"{left['id']} and {right['id']}: shared contract surfaces {', '.join(shared)}")
    return sorted(set(reasons))


def analyze(data: Any) -> dict[str, Any]:
    tasks, errors = load_tasks(data)
    if errors:
        return {"kind": "magia-execution-waves", "version": 1, "status": "blocked", "errors": errors, "waves": []}
    layers, graph_errors = topological_layers(tasks)
    if graph_errors:
        return {"kind": "magia-execution-waves", "version": 1, "status": "blocked", "errors": graph_errors, "waves": []}

    waves: list[dict[str, Any]] = []
    any_parallel = False
    fallbacks: list[str] = []
    number = 1
    for layer in layers:
        reasons = layer_conflicts(layer) if len(layer) > 1 else []
        if len(layer) > 1 and not reasons:
            any_parallel = True
            waves.append({"wave": number, "mode": "parallel", "tasks": [task["id"] for task in layer], "reconciliation_required": True})
            number += 1
        else:
            if reasons:
                fallbacks.extend(reasons)
            for task in layer:
                waves.append({"wave": number, "mode": "sequential", "tasks": [task["id"]], "reconciliation_required": False})
                number += 1
    status = "parallel-safe" if any_parallel and not fallbacks else "sequential-required"
    return {
        "kind": "magia-execution-waves",
        "version": 1,
        "status": status,
        "read_only": True,
        "tasks_executed": [],
        "waves": waves,
        "fallback_reasons": sorted(set(fallbacks)),
        "limitations": [
            "analysis depends on explicitly supplied dependencies, write paths, and contract surfaces",
            "runtime locks, external resources, migrations, and environment conflicts require separate inspection",
            "parallel waves require isolated checks and final reconciliation",
        ],
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines = ["# MAGIA Execution Waves", "", f"- Status: `{result['status']}`", "- Read-only: `true`", ""]
    if result.get("errors"):
        lines += ["## Errors", *[f"- {item}" for item in result["errors"]], ""]
    if result.get("waves"):
        lines += ["## Waves", "", "| Wave | Mode | Tasks | Reconciliation |", "|---:|---|---|---|"]
        for wave in result["waves"]:
            lines.append(f"| {wave['wave']} | {wave['mode']} | {', '.join(wave['tasks'])} | {str(wave['reconciliation_required']).lower()} |")
        lines.append("")
    if result.get("fallback_reasons"):
        lines += ["## Sequential fallback reasons", *[f"- {item}" for item in result["fallback_reasons"]], ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Conservatively analyze explicit task dependencies and scopes into execution waves.")
    parser.add_argument("--input", required=True, help="JSON file containing the explicit task graph.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", help="Optional output path. Defaults to stdout.")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read input: {exc}")
    result = analyze(data)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n" if args.format == "json" else to_markdown(result)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
