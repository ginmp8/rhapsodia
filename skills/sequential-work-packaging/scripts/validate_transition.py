#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _swp_common import atomic_write_json, diagnostic, parse_catalog, parse_tasks, sha256_file, tree_hash  # noqa: E402


def _catalog(root: Path) -> dict:
    return parse_catalog(root / "spec-catalog.yaml")


def _unknown_files(root: Path, spec_ids: set[str]) -> dict[str, str]:
    known = {"spec-catalog.yaml"}
    for sid in spec_ids:
        for name in ("manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"):
            known.add(f"specs/{sid}/{name}")
    result = {}
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        rel = p.relative_to(root).as_posix()
        if rel not in known:
            result[rel] = sha256_file(p)
    return result


def validate_transition(before: Path, after: Path, mode: str, allow_order_change: bool = False) -> dict:
    diagnostics: list[dict] = []
    before = before.resolve()
    after = after.resolve()
    if before == after:
        diagnostics.append(diagnostic("INPUT_OUTPUT_ALIAS", str(after), "before and after roots resolve to same path"))
        return _report(before, after, mode, diagnostics)
    if mode == "normalize" and not (before / "spec-catalog.yaml").is_file():
        diagnostics.append(diagnostic("LEGACY_SOURCE_NO_CANONICAL_CATALOG", str(before), "identity comparison limited to preserved source evidence", "warning"))
        return _report(before, after, mode, diagnostics)
    try:
        bcat, acat = _catalog(before), _catalog(after)
    except Exception as exc:
        diagnostics.append(diagnostic("TRANSITION_PARSE_ERROR", "catalog", str(exc)))
        return _report(before, after, mode, diagnostics)

    bspecs = {s["spec_id"]: s for s in bcat.get("specs", []) if isinstance(s, dict) and isinstance(s.get("spec_id"), str)}
    aspecs = {s["spec_id"]: s for s in acat.get("specs", []) if isinstance(s, dict) and isinstance(s.get("spec_id"), str)}
    for sid, old in sorted(bspecs.items()):
        if sid not in aspecs:
            diagnostics.append(diagnostic("SPEC_ID_REMOVED", sid, "stable spec ids cannot disappear; cancel instead"))
            continue
        new = aspecs[sid]
        if old.get("feature_key") != new.get("feature_key"):
            diagnostics.append(diagnostic("FEATURE_KEY_CHANGED", sid, {"before": old.get("feature_key"), "after": new.get("feature_key")}))
        if old.get("order") != new.get("order") and not allow_order_change:
            diagnostics.append(diagnostic("ORDER_CHANGED_WITHOUT_AUTHORIZATION", sid, {"before": old.get("order"), "after": new.get("order")}))

    bunknown = _unknown_files(before, set(bspecs))
    aunknown = _unknown_files(after, set(aspecs))
    for rel, digest in bunknown.items():
        if rel not in aunknown:
            diagnostics.append(diagnostic("UNKNOWN_FILE_DELETED", rel, digest))
        elif aunknown[rel] != digest:
            diagnostics.append(diagnostic("UNKNOWN_FILE_CHANGED", rel, {"before": digest, "after": aunknown[rel]}))

    for sid in sorted(set(bspecs) & set(aspecs)):
        bpath, apath = before / "specs" / sid / "tasks.md", after / "specs" / sid / "tasks.md"
        if not bpath.is_file() or not apath.is_file():
            continue
        btasks, atasks = parse_tasks(bpath), parse_tasks(apath)
        amap = {t["task_id"]: t for t in atasks}
        for task in btasks:
            tid = task["task_id"]
            if tid not in amap:
                diagnostics.append(diagnostic("TASK_ID_REMOVED", f"{sid}.{tid}", "preserve or explicitly supersede stable task identity"))
            elif task["done"] and not amap[tid]["done"]:
                diagnostics.append(diagnostic("DONE_HISTORY_REVERSED", f"{sid}.{tid}", "completed task became incomplete"))

    return _report(before, after, mode, diagnostics)


def _report(before: Path, after: Path, mode: str, diagnostics: list[dict]) -> dict:
    errors = [d for d in diagnostics if d["severity"] == "error"]
    return {
        "report_version": 1,
        "status": "fail" if errors else "pass",
        "mode": mode,
        "before_root": str(before),
        "after_root": str(after),
        "before_tree_sha256": tree_hash(before) if before.exists() else None,
        "after_tree_sha256": tree_hash(after) if after.exists() else None,
        "error_count": len(errors),
        "warning_count": len(diagnostics) - len(errors),
        "diagnostics": diagnostics,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate invariants across a sequential-work transition.")
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--mode", required=True)
    ap.add_argument("--allow-order-change", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()
    report = validate_transition(Path(args.before), Path(args.after), args.mode, args.allow_order_change)
    if args.json:
        atomic_write_json(Path(args.json), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
