#!/usr/bin/env python3
"""Deterministic cross-artifact linkage for MAGIA planning and execution evidence."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict

TASK_LINE_RE = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s+(?P<task_id>task\d{3}):\s*(?P<title>.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(?P<value>.+?)\s*$")
ANCHOR_RE = re.compile(r"\b(?:OBJ|GOAL|REQ|AC|VAL)-\d{3}\b", re.IGNORECASE)
PARALLEL_MARKER_RE = re.compile(r"\[(?:parallel|independent)\]", re.IGNORECASE)

OBJECTIVE_HEADINGS = {"objective", "objectives", "goal", "goals", "desired outcome", "problem statement"}
ACCEPTANCE_HEADINGS = {
    "acceptance criterion",
    "acceptance criteria",
    "success criterion",
    "success criteria",
    "expected behavior",
}
VALIDATION_HEADINGS = {
    "validation plan",
    "planned check",
    "planned checks",
    "validation check",
    "validation checks",
    "test plan",
    "verification",
    "checks",
}

# These words describe workflow mechanics rather than the product behavior that
# must connect a task to its selected spec.
STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "into", "is", "it", "of", "on",
    "only", "or", "that", "the", "then", "this", "to", "with", "while", "without",
    "build", "change", "check", "confirm", "execute", "expect", "expected", "fix", "implement", "implementation",
    "lint", "manual", "manually", "method", "pytest", "python", "run", "should", "test", "tests", "validate",
    "validation", "verify", "work", "behavior", "task", "objective", "criterion", "criteria", "requirement",
    "code", "exit", "result", "results", "success", "successful", "passes", "pass",
}


class PlanningItem(TypedDict):
    kind: str
    text: str
    anchors: set[str]


class TaskItem(TypedDict):
    task_id: str
    title: str
    done: bool
    anchors: set[str]


def normalize_text(value: str) -> str:
    value = value.strip().strip("`").lower()
    value = re.sub(r"[_/\\.-]+", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def meaningful_tokens(value: str) -> set[str]:
    return {
        token
        for token in normalize_text(value).split()
        if len(token) >= 3 and token not in STOPWORDS and not token.isdigit()
    }


def extract_anchors(value: str) -> set[str]:
    return {match.group(0).upper() for match in ANCHOR_RE.finditer(value)}


def heading_name(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    return stripped.lstrip("#").strip().rstrip("#").strip().lower()


def _section_items(path: Path, headings: set[str], kind: str) -> list[PlanningItem]:
    items: list[PlanningItem] = []
    active = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        heading = heading_name(line)
        if heading is not None:
            active = heading in headings
            continue
        if not active or not line.strip():
            continue
        match = BULLET_RE.match(line)
        value = match.group("value") if match else line.strip()
        if value:
            items.append({"kind": kind, "text": value, "anchors": extract_anchors(value)})
    return items


def parse_intent(prd_path: Path) -> list[PlanningItem]:
    return [
        *_section_items(prd_path, OBJECTIVE_HEADINGS, "objective"),
        *_section_items(prd_path, ACCEPTANCE_HEADINGS, "acceptance"),
    ]


def parse_validation_checks(validation_path: Path) -> list[PlanningItem]:
    return _section_items(validation_path, VALIDATION_HEADINGS, "validation")


def parse_tasks(tasks_path: Path) -> list[TaskItem]:
    tasks: list[TaskItem] = []
    for line in tasks_path.read_text(encoding="utf-8-sig").splitlines():
        match = TASK_LINE_RE.match(line)
        if not match:
            continue
        title = match.group("title")
        tasks.append({
            "task_id": match.group("task_id"),
            "title": title,
            "done": match.group("mark").lower() == "x",
            "anchors": extract_anchors(title),
        })
    return tasks


def _overlap(left: str, right: str) -> int:
    return len(meaningful_tokens(left) & meaningful_tokens(right))


def task_linkage_errors(spec_package: Path, task_id: str) -> list[str]:
    tasks_path = spec_package / "tasks.md"
    prd_path = spec_package / "prd.md"
    validation_path = spec_package / "validation.md"
    if not tasks_path.is_file() or not prd_path.is_file() or not validation_path.is_file():
        return []

    tasks = parse_tasks(tasks_path)
    selected_index = next((index for index, task in enumerate(tasks) if task["task_id"] == task_id), None)
    if selected_index is None:
        return []
    selected = tasks[selected_index]
    errors: list[str] = []

    if not PARALLEL_MARKER_RE.search(selected["title"]):
        earlier_open = [task["task_id"] for task in tasks[:selected_index] if not task["done"]]
        if earlier_open:
            errors.append(
                f"selected task `{task_id}` is not dependency-safe because earlier required tasks remain open: "
                + ", ".join(earlier_open)
                + "; mark an independently executable task with `[parallel]` in planning"
            )

    intent = parse_intent(prd_path)
    intent_anchors = set().union(*(item["anchors"] for item in intent)) if intent else set()
    explicit_intent_link = bool(selected["anchors"] & intent_anchors)
    linked_intent = [item for item in intent if _overlap(selected["title"], item["text"]) >= 2]
    if not explicit_intent_link and not linked_intent:
        errors.append(
            f"selected task `{task_id}` is not linked to any concrete PRD objective or acceptance criterion; "
            "use a shared canonical anchor such as `AC-001` or at least two shared domain terms"
        )

    checks = parse_validation_checks(validation_path)
    check_anchors = set().union(*(item["anchors"] for item in checks)) if checks else set()
    explicit_check_link = bool(selected["anchors"] & check_anchors)
    semantic_context = " ".join([selected["title"], *(item["text"] for item in linked_intent)])
    linked_checks = [item for item in checks if _overlap(semantic_context, item["text"]) >= 1]
    if not explicit_check_link and not linked_checks:
        errors.append(
            f"selected task `{task_id}` is not linked to any planned validation check; "
            "use a shared canonical anchor such as `VAL-001` or a shared domain term"
        )

    return errors


def canonical_source_matches(spec_package: Path, task_id: str, source: str) -> bool:
    """Return whether a traceability source resolves to current planning truth.

    Accepted forms are a real task id (optionally followed by descriptive text),
    a canonical anchor present in PRD/tasks, or the exact normalized text of a
    concrete objective, acceptance criterion, or task title.
    """
    source_normalized = normalize_text(source)
    if not source_normalized:
        return False

    tasks_path = spec_package / "tasks.md"
    prd_path = spec_package / "prd.md"
    if not tasks_path.is_file() or not prd_path.is_file():
        return False

    tasks = parse_tasks(tasks_path)
    selected = next((task for task in tasks if task["task_id"] == task_id), None)
    if selected is None:
        return False

    # Compatibility form used by existing execution records: "task001 objective".
    if re.match(rf"^{re.escape(task_id.lower())}(?:\b|\s)", source.strip().lower()):
        return True

    intent = parse_intent(prd_path)
    known_anchors = set(selected["anchors"])
    for item in intent:
        known_anchors.update(item["anchors"])
    source_anchors = extract_anchors(source)
    if source_anchors and source_anchors <= known_anchors:
        return True

    canonical_texts = {normalize_text(selected["title"])}
    canonical_texts.update(normalize_text(item["text"]) for item in intent)
    return source_normalized in canonical_texts
