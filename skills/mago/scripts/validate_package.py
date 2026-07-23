#!/usr/bin/env python3
"""Validate profile-aware cross-artifact consistency for MAGO spec packages."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from mago_utils import dedupe_preserve_order, strip_quotes

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


VALID_PROFILES = {"quick", "standard", "governed"}
PROFILE_REQUIRED_ARTIFACTS: dict[str, tuple[str, ...]] = {
    "quick": ("manifest.yaml", "prd.md", "tasks.md", "validation.md"),
    "standard": ("manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"),
    "governed": ("manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"),
}
CONDITIONAL_ARTIFACTS = (
    "technical-design.md",
    "complexity-reduction-plan.md",
    "adr.md",
    "execution-handoff-plan.md",
    "contract-spec.md",
    "migration-strategy.md",
    "observability-design.md",
    "operational-requirements.md",
    "security-and-risk-considerations.md",
    "open-questions.md",
)
QUICK_ALLOWED_CONDITIONAL = {"technical-design.md", "complexity-reduction-plan.md", "open-questions.md"}
VALID_ARTIFACT_DECISIONS = {"required", "not_applicable"}

CANONICAL_PHASES = (
    (1, "Foundation"),
    (2, "Core Implementation"),
    (3, "Integration"),
    (4, "Validation and Hardening"),
    (5, "Migration and Rollout"),
)
PHASE_TYPES: dict[int, set[str]] = {
    1: {"analysis", "setup", "confirmation", "refinement"},
    2: {"implementation", "refinement"},
    3: {"integration", "confirmation", "refinement"},
    4: {"validation", "hardening", "confirmation", "refinement"},
    5: {"migration", "rollout", "confirmation"},
}
BASE_REQUIRED_TASK_FIELDS = (
    "objective",
    "affected boundary",
    "task type",
    "reasoning",
    "why this reasoning is sufficient",
    "specialist support",
    "required load",
    "optional load",
    "selection hint",
    "dependencies",
    "validation",
    "expected result",
)
TRACEABILITY_TASK_FIELDS = ("requirements", "acceptance", "decisions", "validations")
VALID_REASONING = {"low", "medium", "high", "xhigh"}
VALID_SPECIALIST_SUPPORT = {"not_required", "required", "optional"}
VALID_EXECUTION_STATUSES = {"not_started", "in_progress", "blocked", "done"}
VALID_LAST_EXECUTION_KEYS = {"task_id", "date", "summary", "files_changed"}
VALID_MUTATION_STATUSES = {"clean", "in_progress", "cancelled", "rollback_required"}

TASK_HEADER_RE = re.compile(
    r"^\s*-\s*\[(?P<mark>[ xX])\]\s+(?P<task_id>task\d{3}):\s+(?P<title>.+?)\s*$"
)
TASK_METADATA_RE = re.compile(r"^\s{2,}-\s+(?P<key>[^:]+):\s*(?P<value>.*?)\s*$")
PHASE_RE = re.compile(r"^##\s+Phase\s+(?P<number>[1-5])\s+-\s+(?P<name>.+?)\s*$")
PHASE_NA_RE = re.compile(r"^\s*(?:-\s*)?Not applicable:\s*(?P<value>.+?)\s*$", re.IGNORECASE)
PHASE_EVIDENCE_RE = re.compile(r"^\s*(?:-\s*)?Evidence:\s*(?P<value>.+?)\s*$", re.IGNORECASE)
NOTES_TASK_RE = re.compile(r"^###\s+(?P<task_id>task\d{3})\b")
NOTES_STATUS_RE = re.compile(r"^\s*-\s+Status:\s*(?P<value>.+?)\s*$")
PLACEHOLDER_RE = re.compile(r"<[A-Za-z0-9_|.-]+>")
UNRESOLVED_VALUE_RE = re.compile(r"(?i)^(?:unknown|tbd|to[d]o|replace me|placeholder)$")


@dataclass(frozen=True)
class TaskRef:
    task_id: str
    line_number: int
    checked: bool = False


@dataclass
class TaskBlock:
    task_id: str
    title: str
    line_number: int
    checked: bool
    phase_number: int | None
    phase_name: str | None
    fields: dict[str, tuple[str, int]] = field(default_factory=dict)


@dataclass
class PhaseBlock:
    number: int
    name: str
    line_number: int
    task_ids: list[str] = field(default_factory=list)
    not_applicable_rationale: str | None = None
    not_applicable_evidence: str | None = None


class ManifestParseError(ValueError):
    pass


def normalize_field_name(value: str) -> str:
    return " ".join(value.strip().lower().split())


def is_resolved_value(value: object) -> bool:
    if value is None:
        return False
    text = strip_quotes(str(value)) or ""
    text = text.strip()
    if not text or PLACEHOLDER_RE.search(text) or UNRESOLVED_VALUE_RE.fullmatch(text):
        return False
    return True


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if yaml is None:
        raise ManifestParseError("PyYAML is required for profile-aware package validation")
    try:
        loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8-sig")) or {}
    except yaml.YAMLError as exc:  # type: ignore[attr-defined]
        mark = getattr(exc, "problem_mark", None)
        location = f":{mark.line + 1}:{mark.column + 1}" if mark is not None else ""
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        raise ManifestParseError(f"{manifest_path}{location}: invalid YAML: {problem}") from None
    if not isinstance(loaded, dict):
        raise ManifestParseError(f"{manifest_path}: top-level value must be a mapping")
    return loaded


def parse_tasks(tasks_path: Path) -> tuple[dict[str, TaskBlock], list[PhaseBlock], list[str]]:
    tasks: dict[str, TaskBlock] = {}
    phases: list[PhaseBlock] = []
    errors: list[str] = []
    current_phase: PhaseBlock | None = None
    current_task: TaskBlock | None = None

    for line_number, line in enumerate(tasks_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        phase_match = PHASE_RE.match(line)
        if phase_match:
            phase = PhaseBlock(
                number=int(phase_match.group("number")),
                name=phase_match.group("name").strip(),
                line_number=line_number,
            )
            phases.append(phase)
            current_phase = phase
            current_task = None
            continue

        task_match = TASK_HEADER_RE.match(line)
        if task_match:
            task_id = task_match.group("task_id")
            if task_id in tasks:
                errors.append(
                    f"{tasks_path}:{line_number}: duplicate task id `{task_id}` "
                    f"(first seen on line {tasks[task_id].line_number})"
                )
                current_task = None
                continue
            task = TaskBlock(
                task_id=task_id,
                title=task_match.group("title").strip(),
                line_number=line_number,
                checked=task_match.group("mark").lower() == "x",
                phase_number=current_phase.number if current_phase else None,
                phase_name=current_phase.name if current_phase else None,
            )
            tasks[task_id] = task
            current_task = task
            if current_phase is None:
                errors.append(f"{tasks_path}:{line_number}: task `{task_id}` is outside a canonical phase")
            else:
                current_phase.task_ids.append(task_id)
            continue

        na_match = PHASE_NA_RE.match(line)
        if na_match and current_phase is not None and current_task is None:
            rationale = na_match.group("value").strip()
            if not is_resolved_value(rationale):
                errors.append(f"{tasks_path}:{line_number}: phase non-applicability needs explicit rationale")
            elif current_phase.not_applicable_rationale is not None:
                errors.append(f"{tasks_path}:{line_number}: duplicate phase non-applicability rationale")
            else:
                current_phase.not_applicable_rationale = rationale
            continue

        evidence_match = PHASE_EVIDENCE_RE.match(line)
        if evidence_match and current_phase is not None and current_task is None:
            evidence = evidence_match.group("value").strip()
            if not is_resolved_value(evidence):
                errors.append(f"{tasks_path}:{line_number}: phase non-applicability evidence needs an explicit source")
            elif current_phase.not_applicable_evidence is not None:
                errors.append(f"{tasks_path}:{line_number}: duplicate phase non-applicability evidence")
            else:
                current_phase.not_applicable_evidence = evidence
            continue

        metadata_match = TASK_METADATA_RE.match(line)
        if metadata_match and current_task is not None:
            key = normalize_field_name(metadata_match.group("key"))
            value = metadata_match.group("value").strip()
            if key in current_task.fields:
                errors.append(
                    f"{tasks_path}:{line_number}: duplicate `{metadata_match.group('key').strip()}` field "
                    f"for `{current_task.task_id}`"
                )
            else:
                current_task.fields[key] = (value, line_number)

    return tasks, phases, errors


def extract_dependency_ids(value: str) -> tuple[list[str], bool]:
    if value.lower() == "none":
        return [], True
    dependency_ids = re.findall(r"task\d{3}", value)
    normalized = re.sub(r"task\d{3}", "", value)
    normalized = normalized.replace(",", " ").strip()
    return dependency_ids, not normalized


def detect_task_cycles(tasks_path: Path, tasks: dict[str, TaskBlock], dependencies: dict[str, list[str]]) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            try:
                start = stack.index(task_id)
            except ValueError:
                start = 0
            cycle = stack[start:] + [task_id]
            errors.append(f"{tasks_path}: task dependency cycle detected: {' -> '.join(cycle)}")
            return
        visiting.add(task_id)
        stack.append(task_id)
        for dependency_id in dependencies.get(task_id, []):
            if dependency_id in tasks:
                visit(dependency_id)
        stack.pop()
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id)
    return dedupe_preserve_order(errors)


def validate_task_contract(tasks_path: Path, profile: str) -> tuple[dict[str, TaskRef], list[str], list[str]]:
    tasks, phases, errors = parse_tasks(tasks_path)
    warnings: list[str] = []
    if not tasks:
        errors.append(f"{tasks_path}: no task ids in `taskNNN` format were found")

    expected_phases = list(CANONICAL_PHASES)
    actual_phases = [(phase.number, phase.name) for phase in phases]
    if actual_phases != expected_phases:
        errors.append(
            f"{tasks_path}: canonical phases must appear exactly once and in order: "
            + "; ".join(f"Phase {number} - {name}" for number, name in expected_phases)
        )

    phase_by_number = {phase.number: phase for phase in phases}
    for number, name in CANONICAL_PHASES:
        phase = phase_by_number.get(number)
        if phase is None:
            continue
        if phase.name != name:
            errors.append(f"{tasks_path}:{phase.line_number}: Phase {number} must be named `{name}`")
        if phase.task_ids and (phase.not_applicable_rationale or phase.not_applicable_evidence):
            errors.append(
                f"{tasks_path}:{phase.line_number}: phase cannot contain tasks and non-applicability metadata"
            )
        if phase.not_applicable_evidence and not phase.not_applicable_rationale:
            errors.append(f"{tasks_path}:{phase.line_number}: phase evidence requires a `Not applicable` rationale")
        if not phase.task_ids:
            if profile == "quick":
                if not phase.not_applicable_rationale:
                    errors.append(
                        f"{tasks_path}:{phase.line_number}: empty quick phase needs `Not applicable: <rationale>`"
                    )
            elif number in {2, 4}:
                errors.append(
                    f"{tasks_path}:{phase.line_number}: {profile} profile requires at least one task in Phase {number}"
                )
            else:
                if not phase.not_applicable_rationale:
                    errors.append(
                        f"{tasks_path}:{phase.line_number}: empty {profile} phase needs `Not applicable: <rationale>`"
                    )
                if not phase.not_applicable_evidence:
                    errors.append(
                        f"{tasks_path}:{phase.line_number}: empty {profile} phase needs `Evidence: <source or linked planning id>`"
                    )

    dependencies: dict[str, list[str]] = {}
    required_fields = BASE_REQUIRED_TASK_FIELDS + (TRACEABILITY_TASK_FIELDS if profile in {"standard", "governed"} else ())
    for task in tasks.values():
        for field_name in required_fields:
            if field_name not in task.fields:
                errors.append(
                    f"{tasks_path}:{task.line_number}: `{task.task_id}` missing required field `{field_name.title()}`"
                )
                continue
            value, field_line = task.fields[field_name]
            if not is_resolved_value(value):
                errors.append(
                    f"{tasks_path}:{field_line}: `{task.task_id}` field `{field_name.title()}` needs an explicit value"
                )

        task_type = task.fields.get("task type", ("", task.line_number))[0].lower()
        if task.phase_number in PHASE_TYPES and task_type and task_type not in PHASE_TYPES[task.phase_number]:
            errors.append(
                f"{tasks_path}:{task.line_number}: `{task.task_id}` task type `{task_type}` is invalid for "
                f"Phase {task.phase_number}; use one of {sorted(PHASE_TYPES[task.phase_number])}"
            )
        reasoning = task.fields.get("reasoning", ("", task.line_number))[0].lower()
        if reasoning and reasoning not in VALID_REASONING:
            errors.append(
                f"{tasks_path}:{task.line_number}: `{task.task_id}` reasoning must be one of {sorted(VALID_REASONING)}"
            )
        specialist_support = task.fields.get("specialist support", ("", task.line_number))[0].lower()
        if specialist_support and specialist_support not in VALID_SPECIALIST_SUPPORT:
            errors.append(
                f"{tasks_path}:{task.line_number}: `{task.task_id}` Specialist Support must be one of "
                f"{sorted(VALID_SPECIALIST_SUPPORT)}"
            )

        dependency_value, dependency_line = task.fields.get("dependencies", ("", task.line_number))
        dependency_ids, clean_format = extract_dependency_ids(dependency_value)
        dependencies[task.task_id] = dependency_ids
        if dependency_value and dependency_value.lower() != "none" and not clean_format:
            errors.append(
                f"{tasks_path}:{dependency_line}: `{task.task_id}` Dependencies contains non-task text: "
                f"`{dependency_value}`"
            )
        for dependency_id in dependency_ids:
            if dependency_id == task.task_id:
                errors.append(f"{tasks_path}:{dependency_line}: `{task.task_id}` cannot depend on itself")
            elif dependency_id not in tasks:
                errors.append(
                    f"{tasks_path}:{dependency_line}: dependency `{dependency_id}` does not exist in tasks.md"
                )
            elif tasks[dependency_id].line_number >= task.line_number:
                errors.append(
                    f"{tasks_path}:{dependency_line}: `{task.task_id}` must depend only on an earlier task; "
                    f"`{dependency_id}` appears later"
                )

    errors.extend(detect_task_cycles(tasks_path, tasks, dependencies))
    refs = {
        task_id: TaskRef(task_id=task_id, line_number=task.line_number, checked=task.checked)
        for task_id, task in tasks.items()
    }
    return refs, dedupe_preserve_order(errors), dedupe_preserve_order(warnings)


def parse_notes_task_ids(notes_path: Path) -> tuple[list[TaskRef], list[str], list[str]]:
    refs: list[TaskRef] = []
    duplicates: list[str] = []
    warnings: list[str] = []
    seen: dict[str, int] = {}
    current_task_id: str | None = None
    current_task_line: int | None = None
    current_has_status = False

    for line_number, line in enumerate(notes_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        match = NOTES_TASK_RE.match(line)
        if match:
            if current_task_id is not None and not current_has_status and current_task_line is not None:
                warnings.append(
                    f"{notes_path}:{current_task_line}: execution-log subsection `{current_task_id}` "
                    "is missing canonical `- Status: ...`"
                )
            task_id = match.group("task_id")
            current_task_id = task_id
            current_task_line = line_number
            current_has_status = False
            refs.append(TaskRef(task_id=task_id, line_number=line_number))
            if task_id in seen:
                duplicates.append(
                    f"{notes_path}:{line_number}: duplicate execution-log subsection for `{task_id}` "
                    f"(first seen on line {seen[task_id]})"
                )
            else:
                seen[task_id] = line_number
            continue
        status_match = NOTES_STATUS_RE.match(line)
        if status_match and current_task_id is not None:
            current_has_status = True
            status_value = (strip_quotes(status_match.group("value")) or "").lower()
            if status_value not in VALID_EXECUTION_STATUSES:
                warnings.append(
                    f"{notes_path}:{line_number}: execution-log status `{status_value}` for `{current_task_id}` "
                    f"is noncanonical; use one of {sorted(VALID_EXECUTION_STATUSES)}"
                )

    if current_task_id is not None and not current_has_status and current_task_line is not None:
        warnings.append(
            f"{notes_path}:{current_task_line}: execution-log subsection `{current_task_id}` "
            "is missing canonical `- Status: ...`"
        )
    return refs, duplicates, warnings


def validate_manifest_contract(manifest_path: Path, package_path: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = load_manifest(manifest_path)
    except ManifestParseError as exc:
        return {}, [str(exc)], warnings

    required_keys = (
        "kind",
        "spec_id",
        "cycle_id",
        "feature_key",
        "title",
        "type",
        "classification",
        "profile",
        "status",
        "phase",
        "feature_version",
        "source_of_truth",
        "mutation_state",
    )
    for key in required_keys:
        if key not in data:
            errors.append(f"{manifest_path}: missing required key `{key}`")
        elif key not in {"source_of_truth", "mutation_state"} and not is_resolved_value(data.get(key)):
            errors.append(f"{manifest_path}: `{key}` needs an explicit value")

    profile = str(data.get("profile", "")).strip().lower()
    if profile not in VALID_PROFILES:
        errors.append(f"{manifest_path}: `profile` must be one of {sorted(VALID_PROFILES)}")

    source_of_truth = data.get("source_of_truth")
    if not isinstance(source_of_truth, dict):
        errors.append(f"{manifest_path}: `source_of_truth` must be a mapping")
    else:
        for key, artifact in (("prd", "prd.md"), ("tasks", "tasks.md"), ("validation", "validation.md")):
            if source_of_truth.get(key) != artifact:
                errors.append(f"{manifest_path}: `source_of_truth.{key}` must be `{artifact}`")
        if profile in {"standard", "governed"} and source_of_truth.get("notes") != "notes.md":
            errors.append(f"{manifest_path}: `{profile}` profile requires `source_of_truth.notes: notes.md`")

    mutation_state = data.get("mutation_state")
    if not isinstance(mutation_state, dict):
        errors.append(f"{manifest_path}: `mutation_state` must be a mapping")
    else:
        mutation_status = str(mutation_state.get("status", "")).strip().lower()
        if mutation_status not in VALID_MUTATION_STATUSES:
            errors.append(
                f"{manifest_path}: `mutation_state.status` must be one of {sorted(VALID_MUTATION_STATUSES)}"
            )
        planned_writes = mutation_state.get("planned_writes")
        completed_writes = mutation_state.get("completed_writes")
        if not isinstance(planned_writes, list) or not isinstance(completed_writes, list):
            errors.append(f"{manifest_path}: mutation write sets must be lists")
        elif not set(map(str, completed_writes)).issubset(set(map(str, planned_writes))):
            errors.append(f"{manifest_path}: completed mutation writes must be a subset of planned writes")
        if mutation_status == "clean":
            if mutation_state.get("rollback_required") is True:
                errors.append(f"{manifest_path}: clean mutation state cannot require rollback")
            if planned_writes or completed_writes:
                errors.append(f"{manifest_path}: clean mutation state must clear planned/completed write sets")
        elif mutation_status in {"in_progress", "cancelled", "rollback_required"}:
            for key in ("transaction_id", "inspected_digest", "checkpoint"):
                if not is_resolved_value(mutation_state.get(key)):
                    errors.append(f"{manifest_path}: `{key}` is required while mutation state is `{mutation_status}`")
            if not planned_writes:
                errors.append(f"{manifest_path}: non-clean mutation state requires `planned_writes`")
            errors.append(
                f"{manifest_path}: package is not handoff-ready while `mutation_state.status` is `{mutation_status}`"
            )
            if mutation_status == "cancelled" and mutation_state.get("cancellation_requested") is not True:
                errors.append(f"{manifest_path}: cancelled mutation state requires `cancellation_requested: true`")
            if mutation_status == "rollback_required" and mutation_state.get("rollback_required") is not True:
                errors.append(f"{manifest_path}: rollback-required state requires `rollback_required: true`")

    last_execution = data.get("last_execution")
    if last_execution is not None:
        if not isinstance(last_execution, dict):
            errors.append(f"{manifest_path}: `last_execution` must be a mapping")
        else:
            keys = {str(key) for key in last_execution}
            unexpected = sorted(keys - VALID_LAST_EXECUTION_KEYS)
            if unexpected:
                errors.append(
                    f"{manifest_path}: `last_execution` uses noncanonical key(s) {unexpected}; "
                    f"allowed keys are {sorted(VALID_LAST_EXECUTION_KEYS)}"
                )
            if not is_resolved_value(last_execution.get("task_id")):
                errors.append(f"{manifest_path}: `last_execution.task_id` is required when last_execution exists")

    decisions = data.get("artifact_decisions")
    if profile in {"standard", "governed"} and not isinstance(decisions, dict):
        errors.append(f"{manifest_path}: `{profile}` profile requires `artifact_decisions` mapping")
        decisions = {}
    elif decisions is None:
        decisions = {}
    elif not isinstance(decisions, dict):
        errors.append(f"{manifest_path}: `artifact_decisions` must be a mapping")
        decisions = {}

    if profile in {"standard", "governed"}:
        missing_decisions = sorted(set(CONDITIONAL_ARTIFACTS) - set(map(str, decisions.keys())))
        if missing_decisions:
            errors.append(
                f"{manifest_path}: `{profile}` profile must decide every conditional artifact: {missing_decisions}"
            )

    for artifact_name, raw_decision in decisions.items():
        artifact = str(artifact_name)
        if artifact not in CONDITIONAL_ARTIFACTS:
            errors.append(f"{manifest_path}: unknown conditional artifact decision `{artifact}`")
            continue
        if not isinstance(raw_decision, dict):
            errors.append(f"{manifest_path}: decision for `{artifact}` must be a mapping")
            continue
        decision_status = str(raw_decision.get("status", "")).strip().lower()
        rationale = raw_decision.get("rationale")
        if decision_status not in VALID_ARTIFACT_DECISIONS:
            errors.append(
                f"{manifest_path}: `{artifact}` decision status must be one of {sorted(VALID_ARTIFACT_DECISIONS)}"
            )
            continue
        if not is_resolved_value(rationale):
            errors.append(f"{manifest_path}: `{artifact}` decision needs evidence-backed rationale")
        artifact_path = package_path / artifact
        if decision_status == "required" and not artifact_path.is_file():
            errors.append(f"{manifest_path}: `{artifact}` is required by artifact_decisions but is missing")
        if decision_status == "not_applicable" and artifact_path.exists():
            errors.append(f"{manifest_path}: `{artifact}` exists but artifact_decisions marks it not_applicable")
        if profile == "quick" and decision_status == "required" and artifact not in QUICK_ALLOWED_CONDITIONAL:
            errors.append(
                f"{manifest_path}: quick profile cannot require `{artifact}`; escalate to standard or governed"
            )

    for artifact in CONDITIONAL_ARTIFACTS:
        artifact_path = package_path / artifact
        if artifact_path.exists() and artifact not in decisions:
            errors.append(f"{manifest_path}: `{artifact}` exists without an artifact_decisions entry")

    return data, dedupe_preserve_order(errors), dedupe_preserve_order(warnings)


def validate_conditional_artifacts(package_path: Path) -> list[str]:
    errors: list[str] = []
    technical_design = package_path / "technical-design.md"
    if technical_design.exists():
        from validate_technical_design import validate as validate_technical_design

        errors.extend(validate_technical_design(technical_design))

    security = package_path / "security-and-risk-considerations.md"
    if security.exists():
        from validate_security_risk import validate as validate_security_risk

        errors.extend(validate_security_risk(security, require_v2=True))

    from validate_triggered_artifact import ARTIFACT_HEADINGS, validate as validate_triggered_artifact

    for artifact_name in ARTIFACT_HEADINGS:
        path = package_path / artifact_name
        if path.exists():
            errors.extend(validate_triggered_artifact(path))
    return errors


def validate_package(package_path: Path) -> tuple[list[str], list[str]]:
    package_path = package_path.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = package_path / "manifest.yaml"
    if not manifest_path.exists():
        return [f"{package_path}: missing required manifest.yaml"], warnings

    manifest, manifest_errors, manifest_warnings = validate_manifest_contract(manifest_path, package_path)
    errors.extend(manifest_errors)
    warnings.extend(manifest_warnings)
    profile = str(manifest.get("profile", "")).strip().lower()
    if profile not in VALID_PROFILES:
        profile = "standard"

    for artifact in PROFILE_REQUIRED_ARTIFACTS[profile]:
        if not (package_path / artifact).is_file():
            errors.append(f"{package_path}: `{profile}` profile missing required `{artifact}`")

    tasks_path = package_path / "tasks.md"
    task_map: dict[str, TaskRef] = {}
    if tasks_path.exists():
        task_map, task_errors, task_warnings = validate_task_contract(tasks_path, profile)
        errors.extend(task_errors)
        warnings.extend(task_warnings)

    notes_path = package_path / "notes.md"
    if notes_path.exists():
        notes_text = notes_path.read_text(encoding="utf-8-sig")
        clarification_v2 = bool(re.search(r"(?m)^clarification_contract:\s*2\s*$", notes_text))
        handoff_phase = str(manifest.get("phase", "")).strip().lower() in {"execute", "review", "done"}
        if clarification_v2 or (profile == "governed" and handoff_phase):
            from validate_clarification_readiness import validate_notes
            errors.extend(validate_notes(
                notes_path,
                require_v2=(profile == "governed" and handoff_phase),
                handoff=handoff_phase,
            ))
    if notes_path.exists() and task_map:
        note_refs, duplicate_note_errors, note_warnings = parse_notes_task_ids(notes_path)
        errors.extend(duplicate_note_errors)
        warnings.extend(note_warnings)
        for ref in note_refs:
            if ref.task_id not in task_map:
                errors.append(
                    f"{notes_path}:{ref.line_number}: execution-log task `{ref.task_id}` does not exist in tasks.md"
                )

    last_execution = manifest.get("last_execution")
    if isinstance(last_execution, dict) and task_map:
        last_execution_task_id = str(last_execution.get("task_id", "")).strip()
        if last_execution_task_id and last_execution_task_id not in task_map:
            errors.append(
                f"{manifest_path}: `last_execution.task_id` references `{last_execution_task_id}`, "
                "which does not exist in tasks.md"
            )

    if manifest.get("status") == "done" or manifest.get("phase") == "done":
        open_tasks = sorted(task_id for task_id, ref in task_map.items() if not ref.checked)
        if open_tasks:
            preview = ", ".join(open_tasks[:5])
            suffix = "" if len(open_tasks) <= 5 else ", ..."
            errors.append(
                f"{manifest_path}: package is marked done but still has open tasks in tasks.md: {preview}{suffix}"
            )

    errors.extend(validate_conditional_artifacts(package_path))
    return dedupe_preserve_order(errors), dedupe_preserve_order(warnings)


def resolve_package_targets(board_root_raw: str, spec_ids: Iterable[str]) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    board_root = Path(board_root_raw).resolve()

    for spec_id in spec_ids:
        candidate = board_root / "specs" / spec_id
        if candidate not in seen:
            resolved.append(candidate)
            seen.add(candidate)
    if resolved:
        return resolved

    specs_dir = board_root / "specs"
    if specs_dir.is_dir():
        for child in sorted(specs_dir.iterdir()):
            if child.is_dir() and child not in seen:
                resolved.append(child)
                seen.add(child)
    elif board_root not in seen:
        resolved.append(board_root)
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate profile-aware MAGO spec packages.")
    parser.add_argument("board_root", help="Path to the canonical BOARD_ROOT or one package directory.")
    parser.add_argument(
        "--spec-id",
        action="append",
        default=[],
        help="Repeat to validate selected packages under BOARD_ROOT/specs/. Omit to validate every package.",
    )
    args = parser.parse_args(argv)

    package_paths = resolve_package_targets(args.board_root, args.spec_id)
    if not package_paths:
        print("ERROR: no package targets found")
        print("FAILED: 1 errors, 0 warnings")
        return 1

    total_errors = 0
    total_warnings = 0
    for package_path in package_paths:
        if not package_path.exists():
            print(f"ERROR: {package_path}: target does not exist")
            total_errors += 1
            continue
        errors, warnings = validate_package(package_path)
        total_errors += len(errors)
        total_warnings += len(warnings)
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")

    if total_errors:
        print(f"FAILED: {total_errors} errors, {total_warnings} warnings")
        return 1
    if total_warnings:
        print(f"OK: validated {len(package_paths)} package(s) with {total_warnings} warning(s)")
    else:
        print(f"OK: validated {len(package_paths)} package(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
