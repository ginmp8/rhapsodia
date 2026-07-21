"""Canonical registry loading, validation, ordering, and deterministic view helpers."""

from __future__ import annotations

import sys

import heapq
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

from mago_utils import (
    CANONICAL_CYCLE_KIND,
    CANONICAL_SPEC_KIND,
    SEMVER_RE,
    SLUG_RE,
    canonical_yaml_digest,
    normalize_utc_timestamp,
    parse_cycle_id,
    parse_spec_id,
    parse_utc_timestamp,
)

ACTIVE_SPEC_STATUSES = {"planned", "in_progress", "blocked"}
VALID_SPEC_STATUSES = ACTIVE_SPEC_STATUSES | {"done", "cancelled", "superseded"}
VALID_CYCLE_STATUSES = {"proposed", "planned", "in_progress", "done", "cancelled"}
VALID_PRIORITIES = {"critical", "high", "normal", "low"}
VALID_PROFILES = {"quick", "standard", "governed"}
PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3}
VALID_HANDOFF_STATUS = {"ready_for_prepare_define", "blocked", "needs_discovery"}
VALID_DOWNSTREAM_MODE = {"define", "define-product", "define-tasks"}
VALID_PACKAGE_SHAPE = {"full", "product_only", "tasks_only"}
VALID_SEED_ARTIFACTS = {"manifest.yaml", "prd.md", "technical-design.md", "tasks.md", "notes.md", "validation.md"}


@dataclass(frozen=True)
class RegistryRecord:
    path: Path
    data: dict[str, Any]

    @property
    def spec_id(self) -> str:
        return str(self.data.get("spec_id", ""))

    @property
    def feature_key(self) -> str:
        return str(self.data.get("feature_key", ""))

    @property
    def status(self) -> str:
        return str(self.data.get("status", ""))

    @property
    def dependencies(self) -> list[str]:
        value = self.data.get("depends_on_specs") or []
        return [str(item) for item in value] if isinstance(value, list) else []


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: top-level YAML value must be a mapping")
    return loaded


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return parse_utc_timestamp(value)
    except ValueError:
        return None


def load_cycle(board_root: Path) -> dict[str, Any]:
    return load_yaml(board_root / "cycle.yaml")


def load_registry(board_root: Path) -> list[RegistryRecord]:
    registry_root = board_root / "registry"
    if not registry_root.is_dir():
        return []
    return [RegistryRecord(path, load_yaml(path)) for path in sorted(registry_root.glob("*.yaml"))]


def validate_cycle(board_root: Path, cycle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    path = board_root / "cycle.yaml"
    if cycle.get("kind") != CANONICAL_CYCLE_KIND:
        errors.append(f"{path}: kind must be `{CANONICAL_CYCLE_KIND}`")
    cycle_id = str(cycle.get("cycle_id", ""))
    try:
        parsed = parse_cycle_id(cycle_id)
    except ValueError as exc:
        errors.append(f"{path}: {exc}")
        return errors
    if board_root.name != cycle_id:
        errors.append(f"{path}: cycle_id must match cycle directory `{board_root.name}`")
    if str(cycle.get("cycle_key", "")) != parsed["key"]:
        errors.append(f"{path}: cycle_key must match cycle_id key")
    year = str(cycle.get("year", ""))
    if year != parsed["date"][:4]:
        errors.append(f"{path}: year must match cycle_id date")
    if len(board_root.parents) < 2 or board_root.parent.name != "cycles" or board_root.parent.parent.name != year:
        errors.append(f"{path}: path must be docs/boards/<board_id>/{year}/cycles/<cycle_id>/")
    if str(cycle.get("board_id", "")) != board_root.parent.parent.parent.name:
        errors.append(f"{path}: board_id must match path segment")
    if cycle.get("status") not in VALID_CYCLE_STATUSES:
        errors.append(f"{path}: invalid cycle status `{cycle.get('status')}`")
    raw_created_at = cycle.get("created_at")
    created_at = parse_timestamp(raw_created_at)
    if created_at is None:
        errors.append(f"{path}: created_at must be an ISO-8601 timestamp with timezone")
    else:
        if str(raw_created_at) != normalize_utc_timestamp(str(raw_created_at)):
            errors.append(f"{path}: created_at must use canonical UTC second precision ending in Z")
        if created_at.date().isoformat() != parsed["date"]:
            errors.append(f"{path}: created_at date must match cycle_id date")
    for field in ("proposed_version", "accepted_version"):
        value = cycle.get(field)
        if value not in (None, "") and not SEMVER_RE.fullmatch(str(value)):
            errors.append(f"{path}: {field} must be semantic version metadata")
    revision = cycle.get("planning_revision")
    if not isinstance(revision, int) or revision < 1:
        errors.append(f"{path}: planning_revision must be an integer >= 1")
    return errors


def validate_record(board_root: Path, cycle: dict[str, Any], record: RegistryRecord) -> list[str]:
    errors: list[str] = []
    path = record.path
    data = record.data
    if data.get("kind") != CANONICAL_SPEC_KIND:
        errors.append(f"{path}: kind must be `{CANONICAL_SPEC_KIND}`")
    spec_id = str(data.get("spec_id", ""))
    try:
        parsed = parse_spec_id(spec_id)
    except ValueError as exc:
        errors.append(f"{path}: {exc}")
        return errors
    if path.name != f"{spec_id}.yaml":
        errors.append(f"{path}: filename must match spec_id")
    if str(data.get("feature_key", "")) != parsed["feature"]:
        errors.append(f"{path}: feature_key must match spec_id feature segment")
    if str(data.get("cycle_id", "")) != str(cycle.get("cycle_id", "")):
        errors.append(f"{path}: cycle_id must match cycle.yaml")
    if not SLUG_RE.fullmatch(str(data.get("feature_key", ""))):
        errors.append(f"{path}: feature_key must be lowercase kebab-case")
    if not SEMVER_RE.fullmatch(str(data.get("feature_version", ""))):
        errors.append(f"{path}: feature_version must use semantic versioning")
    if data.get("status") not in VALID_SPEC_STATUSES:
        errors.append(f"{path}: invalid status `{data.get('status')}`")
    if data.get("priority") not in VALID_PRIORITIES:
        errors.append(f"{path}: invalid priority `{data.get('priority')}`")
    if data.get("profile") not in VALID_PROFILES:
        errors.append(f"{path}: profile must be one of {sorted(VALID_PROFILES)}")
    order_hint = data.get("order_hint")
    if order_hint is not None and (not isinstance(order_hint, int) or order_hint < 0):
        errors.append(f"{path}: order_hint must be null or a non-negative integer")
    raw_created_at = data.get("created_at")
    created_at = parse_timestamp(raw_created_at)
    if created_at is None:
        errors.append(f"{path}: created_at must be an ISO-8601 timestamp with timezone")
    else:
        if str(raw_created_at) != normalize_utc_timestamp(str(raw_created_at)):
            errors.append(f"{path}: created_at must use canonical UTC second precision ending in Z")
        if created_at.date().isoformat() != parsed["date"]:
            errors.append(f"{path}: created_at date must match spec_id date")
    for key in ("depends_on_features", "depends_on_specs", "supersedes"):
        if not isinstance(data.get(key), list):
            errors.append(f"{path}: {key} must be a list")
    handoff = data.get("handoff")
    if not isinstance(handoff, dict):
        errors.append(f"{path}: handoff must be a mapping")
    else:
        if handoff.get("status") not in VALID_HANDOFF_STATUS:
            errors.append(f"{path}: invalid handoff.status `{handoff.get('status')}`")
        if handoff.get("downstream_mode") not in VALID_DOWNSTREAM_MODE:
            errors.append(f"{path}: invalid handoff.downstream_mode `{handoff.get('downstream_mode')}`")
        if handoff.get("package_shape") not in VALID_PACKAGE_SHAPE:
            errors.append(f"{path}: invalid handoff.package_shape `{handoff.get('package_shape')}`")
        for list_key in ("source_candidates", "seed_artifacts", "blockers"):
            if not isinstance(handoff.get(list_key), list):
                errors.append(f"{path}: handoff.{list_key} must be a list")
        for artifact in handoff.get("seed_artifacts") or []:
            if artifact not in VALID_SEED_ARTIFACTS:
                errors.append(f"{path}: unsupported seed artifact `{artifact}`")
        profile = data.get("profile")
        expected_seed_artifacts = (
            {"manifest.yaml", "prd.md", "tasks.md", "validation.md"}
            if profile == "quick"
            else {"manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"}
        )
        actual_seed_artifacts = set(handoff.get("seed_artifacts") or [])
        if profile in VALID_PROFILES and actual_seed_artifacts != expected_seed_artifacts:
            errors.append(
                f"{path}: handoff.seed_artifacts must match `{profile}` profile minimums: "
                f"{sorted(expected_seed_artifacts)}"
            )
        for candidate in handoff.get("source_candidates") or []:
            candidate_path = Path(str(candidate))
            if candidate_path.is_absolute() or ".." in candidate_path.parts:
                errors.append(f"{path}: source candidate must be a safe cycle-relative path: `{candidate}`")
            elif not (board_root / candidate_path).exists():
                errors.append(f"{path}: source candidate does not exist: `{candidate}`")
    return errors


def dependency_errors(records: list[RegistryRecord]) -> list[str]:
    errors: list[str] = []
    by_id = {record.spec_id: record for record in records}
    by_feature: dict[str, list[str]] = {}
    for record in records:
        by_feature.setdefault(record.feature_key, []).append(record.spec_id)
        for dependency in record.dependencies:
            if dependency == record.spec_id:
                errors.append(f"{record.path}: spec cannot depend on itself")
            elif dependency not in by_id:
                errors.append(f"{record.path}: missing dependency `{dependency}`")
    for feature_key, ids in sorted(by_feature.items()):
        if len(ids) > 1:
            errors.append(f"duplicate feature_key `{feature_key}`: {', '.join(sorted(ids))}")

    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(spec_id: str) -> None:
        marker = state.get(spec_id, 0)
        if marker == 2:
            return
        if marker == 1:
            start = stack.index(spec_id)
            errors.append("dependency cycle: " + " -> ".join(stack[start:] + [spec_id]))
            return
        state[spec_id] = 1
        stack.append(spec_id)
        for dependency in by_id[spec_id].dependencies:
            if dependency in by_id:
                visit(dependency)
        stack.pop()
        state[spec_id] = 2

    for spec_id in sorted(by_id):
        visit(spec_id)
    return errors


def topological_order(records: list[RegistryRecord]) -> list[RegistryRecord]:
    by_id = {record.spec_id: record for record in records}
    indegree = {spec_id: 0 for spec_id in by_id}
    dependents: dict[str, list[str]] = {spec_id: [] for spec_id in by_id}
    for record in records:
        for dependency in record.dependencies:
            if dependency in by_id:
                indegree[record.spec_id] += 1
                dependents[dependency].append(record.spec_id)

    def key(spec_id: str) -> tuple[object, ...]:
        record = by_id[spec_id]
        data = record.data
        return (
            PRIORITY_ORDER.get(str(data.get("priority")), 99),
            data.get("order_hint") if isinstance(data.get("order_hint"), int) else 2**31,
            str(data.get("created_at", "")),
            spec_id,
        )

    ready: list[tuple[tuple[object, ...], str]] = []
    for spec_id, count in indegree.items():
        if count == 0:
            heapq.heappush(ready, (key(spec_id), spec_id))
    ordered: list[RegistryRecord] = []
    while ready:
        _, spec_id = heapq.heappop(ready)
        ordered.append(by_id[spec_id])
        for dependent in sorted(dependents[spec_id]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, (key(dependent), dependent))
    if len(ordered) != len(records):
        raise ValueError("dependency graph contains a cycle")
    return ordered


def registry_digest(records: list[RegistryRecord]) -> str:
    return canonical_yaml_digest(record.path for record in records)


def _import_only_main() -> int:
    print("concurrent_model.py is an import-only helper; use the documented Mago CLI scripts.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_import_only_main())
