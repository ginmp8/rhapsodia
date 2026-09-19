#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _swp_common import SPEC_RE, TASK_RE, parse_catalog, parse_tasks, sha256_file  # noqa: E402


def next_spec(catalog_path: Path) -> dict:
    catalog = parse_catalog(catalog_path)
    specs = [s for s in catalog.get("specs", []) if isinstance(s, dict)]
    nums = [int(SPEC_RE.fullmatch(s.get("spec_id", "")).group("n")) for s in specs if SPEC_RE.fullmatch(s.get("spec_id", ""))]
    orders = [s.get("order") for s in specs if isinstance(s.get("order"), int)]
    n = max(nums, default=0) + 1
    width = max(3, len(str(n)))
    return {
        "status": "pass",
        "catalog_sha256": sha256_file(catalog_path),
        "next_spec_id": f"spec{n:0{width}d}",
        "append_order": max(orders, default=0) + 10,
    }


def insertion_order(catalog_path: Path, after_spec: str, before_spec: str) -> dict:
    catalog = parse_catalog(catalog_path)
    by_id = {s.get("spec_id"): s for s in catalog.get("specs", []) if isinstance(s, dict)}
    if after_spec not in by_id or before_spec not in by_id:
        return {"status": "fail", "code": "ORDER_ANCHOR_UNKNOWN", "after_spec": after_spec, "before_spec": before_spec}
    a, b = by_id[after_spec].get("order"), by_id[before_spec].get("order")
    if not isinstance(a, int) or not isinstance(b, int) or a >= b:
        return {"status": "fail", "code": "ORDER_ANCHOR_INVALID", "after_order": a, "before_order": b}
    used = {s.get("order") for s in by_id.values() if isinstance(s.get("order"), int)}
    candidates = [x for x in range(a + 1, b) if x not in used]
    if not candidates:
        return {"status": "fail", "code": "ORDER_REBALANCE_REQUIRED", "after_order": a, "before_order": b}
    midpoint = (a + b) // 2
    candidates.sort(key=lambda x: (abs(x - midpoint), x))
    return {
        "status": "pass",
        "catalog_sha256": sha256_file(catalog_path),
        "after_spec": after_spec,
        "before_spec": before_spec,
        "order": candidates[0],
    }


def next_task(tasks_path: Path) -> dict:
    tasks = parse_tasks(tasks_path)
    nums = []
    for task in tasks:
        tid = task.get("task_id", "")
        m = TASK_RE.fullmatch(tid)
        if m:
            nums.append(int(m.group("n")))
        nums.append(int(task.get("display_number", 0)))
    n = max(nums, default=0) + 1
    width = max(3, len(str(n)))
    return {"status": "pass", "tasks_sha256": sha256_file(tasks_path), "next_task_id": f"task{n:0{width}d}"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive stable sequential identities from exact source bytes.")
    sub = ap.add_subparsers(dest="command", required=True)
    p_spec = sub.add_parser("spec")
    p_spec.add_argument("--catalog", required=True)
    p_insert = sub.add_parser("insert-order")
    p_insert.add_argument("--catalog", required=True)
    p_insert.add_argument("--after-spec", required=True)
    p_insert.add_argument("--before-spec", required=True)
    p_task = sub.add_parser("task")
    p_task.add_argument("--tasks", required=True)
    args = ap.parse_args()
    if args.command == "spec":
        result = next_spec(Path(args.catalog))
    elif args.command == "insert-order":
        result = insertion_order(Path(args.catalog), args.after_spec, args.before_spec)
    else:
        result = next_task(Path(args.tasks))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
