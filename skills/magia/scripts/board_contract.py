"""Self-contained canonical planning-board contract used by MAGIA."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from magia_utils import (
    SPEC_ID_RE,
    board_root_path_error,
    load_yaml,
    parse_cycle_id,
    parse_spec_id,
    spec_registry_path,
)

CYCLE_KIND = "mago-cycle"
SPEC_KIND = "mago-spec"
MANIFEST_KIND = "mago-spec-manifest"
VALID_CYCLE_STATUSES = {"proposed", "planned", "in_progress", "done", "cancelled"}
VALID_SPEC_STATUSES = {"planned", "in_progress", "blocked", "done", "cancelled", "superseded"}
VALID_MANIFEST_PHASES = {"define", "execute", "review", "done"}
FORBIDDEN_AGGREGATES = {"spec-catalog.yaml", "define-queue.yaml"}
VALID_BUSINESS_PRIORITIES = {"unknown", "low", "medium", "high", "urgent"}
VALID_TECHNICAL_CRITICALITIES = {"low", "normal", "high", "critical"}
VALID_EXECUTION_LANES = {"expedite", "fixed_date", "standard", "deferred"}


def _as_list(value: Any, label: str, errors: list[str]) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    return value


def _cycle_errors(board_root: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    path_error = board_root_path_error(board_root)
    if path_error:
        errors.append(path_error)
    cycle_path = board_root / "cycle.yaml"
    if not cycle_path.is_file():
        return {}, errors + [f"missing cycle.yaml: {cycle_path}"]
    try:
        cycle = load_yaml(cycle_path)
    except Exception as exc:  # noqa: BLE001
        return {}, errors + [str(exc)]
    if cycle.get("kind") != CYCLE_KIND:
        errors.append(f"cycle.yaml kind must be `{CYCLE_KIND}`")
    cycle_id = str(cycle.get("cycle_id", ""))
    try:
        parsed = parse_cycle_id(cycle_id)
    except ValueError as exc:
        errors.append(str(exc))
        parsed = {}
    if cycle_id != board_root.name:
        errors.append("cycle.yaml cycle_id must match the cycle directory name")
    if str(cycle.get("board_id", "")) != board_root.parents[2].name:
        errors.append("cycle.yaml board_id must match the board directory")
    if str(cycle.get("year", "")) != board_root.parents[1].name:
        errors.append("cycle.yaml year must match the year directory")
    if parsed and parsed["date"][:4] != str(cycle.get("year", "")):
        errors.append("cycle_id creation year must match cycle.yaml year")
    if cycle.get("status") not in VALID_CYCLE_STATUSES:
        errors.append(f"cycle.yaml status must be one of {sorted(VALID_CYCLE_STATUSES)}")
    return cycle, errors


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_priority_semantics(data: dict[str, Any], path: Path) -> list[str]:
    """Validate Mago-owned sequencing and read-only Nomia business-priority evidence."""
    errors: list[str] = []
    rejected = [key for key in ("priority", "order_hint") if key in data]
    if rejected:
        errors.append(
            f"{path.name}: unsupported generic field(s) {', '.join(rejected)}; "
            "use business_priority, technical_criticality, and execution_sequence"
        )

    business = data.get("business_priority")
    if not isinstance(business, dict):
        errors.append(f"{path.name}: business_priority must be a mapping")
    else:
        if business.get("owner") != "nomia":
            errors.append(f"{path.name}: business_priority.owner must be nomia")
        level = business.get("level")
        if level not in VALID_BUSINESS_PRIORITIES:
            errors.append(f"{path.name}: invalid business_priority.level `{level}`")
        if level != "unknown":
            if not isinstance(business.get("source"), str) or not business.get("source", "").strip():
                errors.append(f"{path.name}: non-unknown business_priority requires source")
            if _parse_timestamp(business.get("observed_at")) is None:
                errors.append(f"{path.name}: non-unknown business_priority requires ISO-8601 observed_at")

    technical = data.get("technical_criticality")
    if not isinstance(technical, dict):
        errors.append(f"{path.name}: technical_criticality must be a mapping")
    else:
        if technical.get("owner") != "mago":
            errors.append(f"{path.name}: technical_criticality.owner must be mago")
        level = technical.get("level")
        if level not in VALID_TECHNICAL_CRITICALITIES:
            errors.append(f"{path.name}: invalid technical_criticality.level `{level}`")
        rationale = technical.get("rationale")
        if level != "normal" and (not isinstance(rationale, str) or not rationale.strip()):
            errors.append(f"{path.name}: non-normal technical_criticality requires rationale")

    sequence = data.get("execution_sequence")
    if not isinstance(sequence, dict):
        errors.append(f"{path.name}: execution_sequence must be a mapping")
    else:
        if sequence.get("owner") != "mago":
            errors.append(f"{path.name}: execution_sequence.owner must be mago")
        lane = sequence.get("lane")
        if lane not in VALID_EXECUTION_LANES:
            errors.append(f"{path.name}: invalid execution_sequence.lane `{lane}`")
        rank = sequence.get("rank")
        if rank is not None and (not isinstance(rank, int) or isinstance(rank, bool) or rank < 0):
            errors.append(f"{path.name}: execution_sequence.rank must be null or a non-negative integer")
        rationale = sequence.get("rationale")
        if not isinstance(rationale, list) or any(not isinstance(item, str) or not item.strip() for item in rationale):
            errors.append(f"{path.name}: execution_sequence.rationale must be a list of non-empty strings")
        elif (lane != "standard" or rank is not None) and not rationale:
            errors.append(f"{path.name}: non-default execution_sequence requires rationale")
    return errors


def load_registry(board_root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    registry_root = board_root / "registry"
    if not registry_root.is_dir():
        return records, [f"missing registry directory: {registry_root}"]
    for path in sorted(registry_root.glob("*.yaml")):
        try:
            data = load_yaml(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        spec_id = str(data.get("spec_id", ""))
        if data.get("kind") != SPEC_KIND:
            errors.append(f"{path.name}: kind must be `{SPEC_KIND}`")
        try:
            parsed = parse_spec_id(spec_id)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        if path.name != f"{spec_id}.yaml":
            errors.append(f"{path.name}: filename must match spec_id")
        if data.get("feature_key") != parsed["feature"]:
            errors.append(f"{path.name}: feature_key must match the feature encoded in spec_id")
        if data.get("status") not in VALID_SPEC_STATUSES:
            errors.append(f"{path.name}: invalid status `{data.get('status')}`")
        errors.extend(validate_priority_semantics(data, path))
        for dependency in _as_list(data.get("depends_on_specs"), f"{path.name}.depends_on_specs", errors):
            if not isinstance(dependency, str) or not SPEC_ID_RE.fullmatch(dependency):
                errors.append(f"{path.name}: invalid depends_on_specs entry `{dependency}`")
        records[spec_id] = data
    return records, errors


def dependency_errors(records: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    graph: dict[str, list[str]] = {}
    for spec_id, record in records.items():
        deps = [str(item) for item in record.get("depends_on_specs") or []]
        graph[spec_id] = deps
        for dep in deps:
            if dep not in records:
                errors.append(f"{spec_id}: missing dependency `{dep}`")

    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(node: str, stack: list[str]) -> None:
        if node in visited:
            return
        if node in visiting:
            try:
                start = stack.index(node)
                cycle = stack[start:] + [node]
            except ValueError:
                cycle = stack + [node]
            errors.append("dependency cycle: " + " -> ".join(cycle))
            return
        visiting.add(node)
        stack.append(node)
        for dep in graph.get(node, []):
            if dep in graph:
                walk(dep, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        walk(node, [])
    return errors


def manifest_errors(board_root: Path, records: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    specs_root = board_root / "specs"
    if not specs_root.is_dir():
        return errors
    for package in sorted(path for path in specs_root.iterdir() if path.is_dir()):
        spec_id = package.name
        if spec_id not in records:
            errors.append(f"{spec_id}: package directory has no registry entry")
            continue
        manifest_path = package / "manifest.yaml"
        if not manifest_path.is_file():
            continue
        try:
            manifest = load_yaml(manifest_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        record = records[spec_id]
        if manifest.get("kind") != MANIFEST_KIND:
            errors.append(f"{spec_id}: manifest kind must be `{MANIFEST_KIND}`")
        for key in ("spec_id", "cycle_id", "feature_key"):
            if manifest.get(key) != record.get(key):
                errors.append(f"{spec_id}: manifest `{key}` must match registry")
        if manifest.get("phase") not in VALID_MANIFEST_PHASES:
            errors.append(f"{spec_id}: invalid manifest phase `{manifest.get('phase')}`")
    return errors


def validate_board(board_root: Path) -> list[str]:
    errors: list[str] = []
    cycle, cycle_errors = _cycle_errors(board_root)
    errors.extend(cycle_errors)
    for forbidden in FORBIDDEN_AGGREGATES:
        if (board_root / forbidden).exists():
            errors.append(f"{forbidden} is a generated projection and must not be an active board artifact")
    records, registry_errors = load_registry(board_root)
    errors.extend(registry_errors)
    if cycle:
        cycle_id = cycle.get("cycle_id")
        for spec_id, record in records.items():
            if record.get("cycle_id") != cycle_id:
                errors.append(f"{spec_id}: registry cycle_id must match cycle.yaml")
    errors.extend(dependency_errors(records))
    errors.extend(manifest_errors(board_root, records))
    return list(dict.fromkeys(errors))


def registry_for(board_root: Path, spec_id: str) -> dict[str, Any]:
    path = spec_registry_path(board_root, spec_id)
    if not path.is_file():
        raise FileNotFoundError(f"missing registry entry: {path}")
    return load_yaml(path)
