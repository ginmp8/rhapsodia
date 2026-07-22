"""Self-contained canonical planning-board contract used by MAGIA."""

from __future__ import annotations

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
VALID_BUSINESS_PRIORITIES = {"unknown", "low", "medium", "high", "urgent"}
VALID_TECHNICAL_CRITICALITIES = {"low", "normal", "high", "critical"}
VALID_EXECUTION_LANES = {"expedite", "fixed_date", "standard", "deferred"}
FORBIDDEN_AGGREGATES = {"spec-catalog.yaml", "define-queue.yaml"}


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
        errors.extend(validate_priority_semantics(data, path.name))
        for dependency in _as_list(data.get("depends_on_specs"), f"{path.name}.depends_on_specs", errors):
            if not isinstance(dependency, str) or not SPEC_ID_RE.fullmatch(dependency):
                errors.append(f"{path.name}: invalid depends_on_specs entry `{dependency}`")
        records[spec_id] = data
    return records, errors



def validate_priority_semantics(data: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    rejected = [key for key in ("priority", "order_hint") if key in data]
    if rejected:
        errors.append(
            f"{label}: unsupported generic field(s) {', '.join(rejected)}; "
            "the Mago source must provide canonical priority-contract fields"
        )

    business = data.get("business_priority")
    if not isinstance(business, dict) or business.get("owner") != "nomia" or business.get("level") not in VALID_BUSINESS_PRIORITIES:
        errors.append(f"{label}: invalid business_priority projection")
    elif business.get("level") != "unknown" and (not business.get("source") or not business.get("observed_at")):
        errors.append(f"{label}: non-unknown business_priority requires source and observed_at")

    technical = data.get("technical_criticality")
    if not isinstance(technical, dict) or technical.get("owner") != "mago" or technical.get("level") not in VALID_TECHNICAL_CRITICALITIES:
        errors.append(f"{label}: invalid technical_criticality")

    sequence = data.get("execution_sequence")
    if not isinstance(sequence, dict) or sequence.get("owner") != "mago" or sequence.get("lane") not in VALID_EXECUTION_LANES:
        errors.append(f"{label}: invalid execution_sequence")
    else:
        rank = sequence.get("rank")
        rationale = sequence.get("rationale")
        if rank is not None and (not isinstance(rank, int) or isinstance(rank, bool) or rank < 0):
            errors.append(f"{label}: execution_sequence.rank must be null or non-negative integer")
        if not isinstance(rationale, list) or any(not isinstance(item, str) or not item.strip() for item in rationale):
            errors.append(f"{label}: execution_sequence.rationale must be a list of non-empty strings")
    return errors

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
