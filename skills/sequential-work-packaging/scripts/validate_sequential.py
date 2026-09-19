#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _swp_common import (  # noqa: E402
    CANONICAL_SPEC_FILES, CLASSIFICATIONS, CYCLE_RE, CYCLE_STATUSES, FEATURE_RE,
    MODES, PHASES, SPEC_RE, SPEC_STATUSES, TASK_RE, TYPES, VERSION_RE,
    atomic_write_json, diagnostic, parse_catalog, parse_manifest, parse_tasks,
    semver_tuple, tree_hash,
)

REQUIRED_CATALOG = {"schema_version", "cycle_version", "cycle_status", "specs"}
REQUIRED_SPEC = {"order", "spec_id", "feature_key", "title", "type", "classification", "depends_on_features", "depends_on_specs", "status", "feature_version"}
REQUIRED_MANIFEST = {"schema_version", "spec_id", "feature_key", "title", "type", "classification", "status", "phase", "cycle_version", "feature_version", "source_of_truth", "traceability"}


def _cycle_nodes(specs: list[dict]) -> list[list[str]]:
    graph = {s.get("spec_id"): list(s.get("depends_on_specs") or []) for s in specs if isinstance(s.get("spec_id"), str)}
    state: dict[str, int] = {}
    stack: list[str] = []
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                continue
            if state.get(dep, 0) == 0:
                visit(dep)
            elif state.get(dep) == 1:
                idx = stack.index(dep)
                cycles.append(stack[idx:] + [dep])
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node)
    return cycles


def validate_cycle(cycle_root: Path, mode: str, spec_id: str | None = None) -> dict:
    diagnostics: list[dict] = []
    root = cycle_root.resolve()
    if mode not in MODES:
        diagnostics.append(diagnostic("MODE_INVALID", "mode", mode))
    if not root.exists() or not root.is_dir():
        diagnostics.append(diagnostic("CYCLE_ROOT_MISSING", str(root), "cycle root does not exist"))
        return _report(root, mode, spec_id, diagnostics)

    catalog_path = root / "spec-catalog.yaml"
    if not catalog_path.is_file():
        diagnostics.append(diagnostic("CATALOG_MISSING", "spec-catalog.yaml", "canonical catalog is required"))
        return _report(root, mode, spec_id, diagnostics)

    try:
        catalog = parse_catalog(catalog_path)
    except Exception as exc:
        diagnostics.append(diagnostic("CATALOG_PARSE_ERROR", "spec-catalog.yaml", str(exc)))
        return _report(root, mode, spec_id, diagnostics)

    missing = sorted(REQUIRED_CATALOG - set(catalog))
    if missing:
        diagnostics.append(diagnostic("CATALOG_FIELDS_MISSING", "spec-catalog.yaml", missing))
    if catalog.get("schema_version") != 1:
        diagnostics.append(diagnostic("CATALOG_SCHEMA_UNSUPPORTED", "schema_version", catalog.get("schema_version")))
    cycle_version = catalog.get("cycle_version")
    if not isinstance(cycle_version, str) or not CYCLE_RE.fullmatch(cycle_version):
        diagnostics.append(diagnostic("CYCLE_VERSION_INVALID", "cycle_version", cycle_version))
    elif root.name != cycle_version:
        diagnostics.append(diagnostic("CYCLE_PATH_MISMATCH", str(root), {"directory": root.name, "cycle_version": cycle_version}))
    if catalog.get("cycle_status") not in CYCLE_STATUSES:
        diagnostics.append(diagnostic("CYCLE_STATUS_INVALID", "cycle_status", catalog.get("cycle_status")))

    specs = catalog.get("specs")
    if not isinstance(specs, list):
        diagnostics.append(diagnostic("SPECS_NOT_LIST", "specs", type(specs).__name__))
        specs = []

    ids: dict[str, dict] = {}
    orders: dict[int, str] = {}
    functional_identity: dict[tuple[str, str], str] = {}
    feature_history: dict[str, list[dict]] = {}

    for idx, spec in enumerate(specs):
        subject = f"specs[{idx}]"
        if not isinstance(spec, dict):
            diagnostics.append(diagnostic("SPEC_ENTRY_INVALID", subject, type(spec).__name__))
            continue
        miss = sorted(REQUIRED_SPEC - set(spec))
        if miss:
            diagnostics.append(diagnostic("SPEC_FIELDS_MISSING", subject, miss))
        sid = spec.get("spec_id")
        if not isinstance(sid, str) or not SPEC_RE.fullmatch(sid):
            diagnostics.append(diagnostic("SPEC_ID_INVALID", subject, sid))
        elif sid in ids:
            diagnostics.append(diagnostic("SPEC_ID_DUPLICATE", sid, [ids[sid].get("order"), spec.get("order")]))
        else:
            ids[sid] = spec
        order = spec.get("order")
        if not isinstance(order, int):
            diagnostics.append(diagnostic("ORDER_INVALID", subject, order))
        elif order in orders:
            diagnostics.append(diagnostic("ORDER_DUPLICATE", str(order), [orders[order], sid]))
        else:
            orders[order] = sid
        fkey = spec.get("feature_key")
        if not isinstance(fkey, str) or not FEATURE_RE.fullmatch(fkey):
            diagnostics.append(diagnostic("FEATURE_KEY_INVALID", subject, fkey))
        fver = spec.get("feature_version")
        if not isinstance(fver, str) or not VERSION_RE.fullmatch(fver):
            diagnostics.append(diagnostic("FEATURE_VERSION_INVALID", subject, fver))
        if isinstance(fkey, str) and isinstance(fver, str):
            key = (fkey, fver)
            if key in functional_identity:
                diagnostics.append(diagnostic("FUNCTIONAL_IDENTITY_DUPLICATE", f"{fkey}@{fver}", [functional_identity[key], sid]))
            else:
                functional_identity[key] = sid
            feature_history.setdefault(fkey, []).append(spec)
        if spec.get("type") not in TYPES:
            diagnostics.append(diagnostic("TYPE_INVALID", subject, spec.get("type")))
        if spec.get("classification") not in CLASSIFICATIONS:
            diagnostics.append(diagnostic("CLASSIFICATION_INVALID", subject, spec.get("classification")))
        if spec.get("status") not in SPEC_STATUSES:
            diagnostics.append(diagnostic("SPEC_STATUS_INVALID", subject, spec.get("status")))
        for dep_key in ("depends_on_features", "depends_on_specs"):
            if not isinstance(spec.get(dep_key), list):
                diagnostics.append(diagnostic("DEPENDENCIES_NOT_LIST", f"{sid}.{dep_key}", spec.get(dep_key)))

    for sid, spec in ids.items():
        for dep in spec.get("depends_on_specs") or []:
            if dep == sid:
                diagnostics.append(diagnostic("SPEC_SELF_DEPENDENCY", sid, dep))
            elif dep not in ids:
                diagnostics.append(diagnostic("SPEC_DEPENDENCY_UNKNOWN", sid, dep))
            elif isinstance(spec.get("order"), int) and isinstance(ids[dep].get("order"), int) and ids[dep]["order"] >= spec["order"]:
                diagnostics.append(diagnostic("SPEC_DEPENDENCY_ORDER_INVALID", sid, {"dependency": dep, "dependency_order": ids[dep]["order"], "order": spec["order"]}))
        for dep in spec.get("depends_on_features") or []:
            if dep not in feature_history:
                diagnostics.append(diagnostic("FEATURE_DEPENDENCY_UNKNOWN", sid, dep))

    for cycle in _cycle_nodes(list(ids.values())):
        diagnostics.append(diagnostic("SPEC_DEPENDENCY_CYCLE", "depends_on_specs", cycle))

    for fkey, history in feature_history.items():
        if len(history) < 2:
            continue
        ordered = sorted(history, key=lambda x: (x.get("order", 0), x.get("spec_id", "")))
        for prev, cur in zip(ordered, ordered[1:]):
            pv, cv = semver_tuple(prev.get("feature_version", "")), semver_tuple(cur.get("feature_version", ""))
            if pv and cv and cv <= pv:
                diagnostics.append(diagnostic("FEATURE_VERSION_NOT_INCREASING", fkey, {"previous": prev.get("feature_version"), "current": cur.get("feature_version")}))
            if prev.get("spec_id") not in (cur.get("depends_on_specs") or []):
                diagnostics.append(diagnostic("FEATURE_EVOLUTION_DEPENDENCY_MISSING", cur.get("spec_id", "unknown"), {"feature_key": fkey, "previous_spec": prev.get("spec_id")}))

    specs_root = root / "specs"
    if specs_root.exists():
        for child in sorted(specs_root.iterdir()):
            if child.is_dir() and SPEC_RE.fullmatch(child.name) and child.name not in ids:
                diagnostics.append(diagnostic("ORPHAN_SPEC_DIRECTORY", child.relative_to(root).as_posix(), "no catalog entry"))

    target_modes = {"define", "refine", "decompose"}
    if mode in target_modes:
        if not spec_id:
            diagnostics.append(diagnostic("TARGET_SPEC_REQUIRED", "spec_id", f"required for {mode}"))
        elif spec_id not in ids:
            diagnostics.append(diagnostic("TARGET_SPEC_NOT_IN_CATALOG", spec_id, "catalog entry missing"))
        else:
            spec_dir = specs_root / spec_id
            if not spec_dir.is_dir():
                diagnostics.append(diagnostic("SPEC_DIRECTORY_MISSING", spec_id, spec_dir.as_posix()))
            else:
                missing_files = sorted(name for name in CANONICAL_SPEC_FILES if not (spec_dir / name).is_file())
                if missing_files:
                    diagnostics.append(diagnostic("SPEC_FILES_MISSING", spec_id, missing_files))

    for sid, spec in ids.items():
        spec_dir = specs_root / sid
        if not spec_dir.is_dir():
            continue
        manifest_path = spec_dir / "manifest.yaml"
        if manifest_path.is_file():
            try:
                manifest = parse_manifest(manifest_path)
                miss = sorted(REQUIRED_MANIFEST - set(manifest))
                if miss:
                    diagnostics.append(diagnostic("MANIFEST_FIELDS_MISSING", sid, miss))
                for field in ("spec_id", "feature_key", "title", "type", "classification", "status", "feature_version"):
                    if manifest.get(field) != spec.get(field):
                        diagnostics.append(diagnostic("MANIFEST_CATALOG_MISMATCH", f"{sid}.{field}", {"catalog": spec.get(field), "manifest": manifest.get(field)}))
                if manifest.get("cycle_version") != cycle_version:
                    diagnostics.append(diagnostic("MANIFEST_CATALOG_MISMATCH", f"{sid}.cycle_version", {"catalog": cycle_version, "manifest": manifest.get("cycle_version")}))
                if manifest.get("phase") not in PHASES:
                    diagnostics.append(diagnostic("PHASE_INVALID", f"{sid}.phase", manifest.get("phase")))
                sot = manifest.get("source_of_truth")
                expected_sot = {"prd": "prd.md", "tasks": "tasks.md", "validation": "validation.md", "notes": "notes.md"}
                if sot != expected_sot:
                    diagnostics.append(diagnostic("SOURCE_OF_TRUTH_INVALID", sid, sot))
            except Exception as exc:
                diagnostics.append(diagnostic("MANIFEST_PARSE_ERROR", sid, str(exc)))

        tasks_path = spec_dir / "tasks.md"
        if tasks_path.is_file():
            tasks = parse_tasks(tasks_path)
            seen_task_ids: dict[str, int] = {}
            positions: dict[str, int] = {}
            for pos, task in enumerate(tasks):
                tid = task["task_id"]
                if tid.startswith("legacy-task-"):
                    severity = "error" if mode == "define" and sid == spec_id else "warning"
                    diagnostics.append(diagnostic("LEGACY_TASK_ID", f"{sid}:line{task['line']}", tid, severity, ["add explicit Task ID: taskNNN without renumbering existing task labels"]))
                elif not TASK_RE.fullmatch(tid):
                    diagnostics.append(diagnostic("TASK_ID_INVALID", f"{sid}:line{task['line']}", tid))
                if tid in seen_task_ids:
                    diagnostics.append(diagnostic("TASK_ID_DUPLICATE", f"{sid}.{tid}", [seen_task_ids[tid], task["line"]]))
                else:
                    seen_task_ids[tid] = task["line"]
                    positions[tid] = pos
            for pos, task in enumerate(tasks):
                tid = task["task_id"]
                for dep in task["dependencies"]:
                    if dep not in positions:
                        diagnostics.append(diagnostic("TASK_DEPENDENCY_UNKNOWN", f"{sid}.{tid}", dep))
                    elif positions[dep] >= pos:
                        diagnostics.append(diagnostic("TASK_DEPENDENCY_ORDER_INVALID", f"{sid}.{tid}", {"dependency": dep, "dependency_position": positions[dep], "position": pos}))

    known_files = {"spec-catalog.yaml"}
    for sid in ids:
        for name in CANONICAL_SPEC_FILES:
            known_files.add(f"specs/{sid}/{name}")
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        rel = p.relative_to(root).as_posix()
        if rel not in known_files:
            diagnostics.append(diagnostic("UNKNOWN_FILE_PRESERVED", rel, "not part of canonical artifact set; never auto-delete", "warning"))

    return _report(root, mode, spec_id, diagnostics)


def _report(root: Path, mode: str, spec_id: str | None, diagnostics: list[dict]) -> dict:
    errors = [d for d in diagnostics if d["severity"] == "error"]
    warnings = [d for d in diagnostics if d["severity"] == "warning"]
    return {
        "report_version": 1,
        "status": "fail" if errors else "pass",
        "mode": mode,
        "cycle_root": str(root),
        "canonical_cycle_root": str(root.resolve(strict=False)),
        "spec_id": spec_id,
        "tree_sha256": tree_hash(root) if root.exists() and root.is_dir() else None,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "diagnostics": diagnostics,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate canonical sequential work packaging artifacts.")
    ap.add_argument("--cycle-root", required=True)
    ap.add_argument("--mode", choices=sorted(MODES), required=True)
    ap.add_argument("--spec-id")
    ap.add_argument("--json")
    args = ap.parse_args()
    report = validate_cycle(Path(args.cycle_root), args.mode, args.spec_id)
    if args.json:
        atomic_write_json(Path(args.json), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
