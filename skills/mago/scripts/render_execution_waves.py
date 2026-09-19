#!/usr/bin/env python3
"""Render dependency-safe task waves from canonical Mago tasks Markdown."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

TASK_RE = re.compile(r"^\s*-\s*\[(?P<done>[ xX])\]\s+(?P<id>task\d{3}):\s*(?P<title>.+?)\s*$")
FIELD_RE = re.compile(r"^\s+-\s+(?P<name>Dependencies|Task type|Affected boundary):\s*(?P<value>.*?)\s*$", re.IGNORECASE)
TASK_ID_RE = re.compile(r"task\d{3}")
COORDINATION_TYPES = {"integration", "validation", "hardening", "migration", "rollout", "confirmation"}


def parse_tasks(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    tasks: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    current: dict[str, Any] | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        match = TASK_RE.match(line)
        if match:
            task_id = match.group("id")
            if task_id in by_id:
                errors.append(f"line {line_number}: duplicate task id {task_id}")
                current = by_id[task_id]
                continue
            current = {
                "id": task_id,
                "title": match.group("title"),
                "completed": bool(match.group("done").strip()),
                "dependencies": [],
                "task_type": "unknown",
                "affected_boundary": "unknown",
                "source_order": len(tasks),
            }
            tasks.append(current)
            by_id[task_id] = current
            continue
        field = FIELD_RE.match(line)
        if current and field:
            name = field.group("name").lower()
            value = field.group("value").strip()
            if "<" in value or ">" in value:
                errors.append(f"{current['id']}: unresolved placeholder in {name}")
            if name == "dependencies":
                lowered = value.lower()
                current["dependencies"] = [] if lowered in {"", "none", "not_required", "n/a"} else TASK_ID_RE.findall(value)
                if not current["dependencies"] and lowered not in {"", "none", "not_required", "n/a"}:
                    errors.append(f"{current['id']}: dependencies field has no parseable task id")
            elif name == "task type":
                current["task_type"] = value.lower()
            elif name == "affected boundary":
                current["affected_boundary"] = value
    if not tasks:
        errors.append("no canonical taskNNN records found")
    return tasks, errors


def build_waves(tasks: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    by_id = {task["id"]: task for task in tasks}
    indegree = {task["id"]: 0 for task in tasks}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        for dep in task["dependencies"]:
            if dep == task["id"]:
                errors.append(f"{task['id']}: self dependency")
                continue
            if dep not in by_id:
                errors.append(f"{task['id']}: unknown dependency {dep}")
                continue
            indegree[task["id"]] += 1
            outgoing[dep].append(task["id"])

    waves: list[list[str]] = []
    ready = [task["id"] for task in tasks if indegree[task["id"]] == 0]
    processed: list[str] = []
    while ready:
        wave = sorted(ready, key=lambda item: by_id[item]["source_order"])
        waves.append(wave)
        next_ready: list[str] = []
        for task_id in wave:
            processed.append(task_id)
            for child in outgoing.get(task_id, []):
                indegree[child] -= 1
                if indegree[child] == 0:
                    next_ready.append(child)
        ready = next_ready
    if len(processed) != len(tasks):
        cycle_nodes = sorted(set(by_id) - set(processed), key=lambda item: by_id[item]["source_order"])
        errors.append(f"dependency cycle or blocked subgraph: {', '.join(cycle_nodes)}")

    depth: dict[str, int] = {}
    predecessor: dict[str, str | None] = {}
    for wave in waves:
        for task_id in wave:
            deps = [dep for dep in by_id[task_id]["dependencies"] if dep in depth]
            if deps:
                best = max(deps, key=lambda dep: depth[dep])
                depth[task_id] = depth[best] + 1
                predecessor[task_id] = best
            else:
                depth[task_id] = 1
                predecessor[task_id] = None
    critical_path: list[str] = []
    if depth:
        current = max(depth, key=lambda item: (depth[item], -by_id[item]["source_order"]))
        while current:
            critical_path.append(current)
            current = predecessor[current]
        critical_path.reverse()

    coordination_gates = [
        task["id"] for task in tasks
        if any(token.strip() in COORDINATION_TYPES for token in re.split(r"[|,/ ]+", task["task_type"]))
    ]
    return {
        "waves": [
            {
                "wave": index + 1,
                "tasks": [
                    {key: by_id[task_id][key] for key in ("id", "title", "completed", "task_type", "affected_boundary", "dependencies")}
                    for task_id in wave
                ],
            }
            for index, wave in enumerate(waves)
        ],
        "critical_path": critical_path,
        "coordination_gates": coordination_gates,
        "errors": errors,
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Mago Execution Wave Projection",
        "",
        "- Authoritative: false",
        "- Scope: dependency projection only",
        "- Magia overlap check required: true",
        "",
    ]
    for wave in data["waves"]:
        lines.extend([f"## Wave {wave['wave']}", ""])
        for task in wave["tasks"]:
            deps = ", ".join(task["dependencies"]) or "none"
            lines.append(f"- `{task['id']}` — {task['title']} (dependencies: {deps})")
        lines.append("")
    lines.extend([
        "## Critical Path",
        "",
        " -> ".join(f"`{item}`" for item in data["critical_path"]) or "none",
        "",
        "## Coordination Gates",
        "",
        ", ".join(f"`{item}`" for item in data["coordination_gates"]) or "none",
        "",
        "## Errors",
        "",
    ])
    lines.extend(f"- {error}" for error in data["errors"])
    if not data["errors"]:
        lines.append("- none")
    lines.extend([
        "",
        "This projection does not prove file, contract, schema, migration, environment, or runtime independence.",
        "",
    ])
    return "\n".join(lines)


def write_output(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"output exists; pass --force to replace: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks", help="Canonical tasks.md path")
    parser.add_argument("--output", required=True, help="External output path")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    source = Path(args.tasks).resolve()
    if not source.is_file():
        raise SystemExit(f"tasks file not found: {source}")
    output = Path(args.output).resolve()
    package = source.parent
    if output == package or package in output.parents:
        raise SystemExit("output must be outside the canonical package directory")
    tasks, errors = parse_tasks(source)
    result = build_waves(tasks, errors)
    data = {
        "kind": "mago-execution-wave-projection",
        "authoritative": False,
        "source": str(source),
        "parallelism_scope": "dependency_projection_only",
        "requires_magia_overlap_check": True,
        **result,
    }
    text = json.dumps(data, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_markdown(data)
    try:
        write_output(output, text, args.force)
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"status: {'pass' if not errors else 'fail'}")
    print(f"waves: {len(result['waves'])}")
    print(f"output: {output}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
