#!/usr/bin/env python3
"""Render deterministic noncanonical catalog and queue views from registry files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

from mago_utils import CANONICAL_CATALOG_KIND, CANONICAL_QUEUE_KIND
from concurrent_model import dependency_errors, load_cycle, load_registry, registry_digest, topological_order, validate_cycle, validate_record


def dump_yaml(data: dict[str, Any]) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def build_views(board_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    cycle = load_cycle(board_root)
    records = load_registry(board_root)
    errors = validate_cycle(board_root, cycle)
    for record in records:
        errors.extend(validate_record(board_root, cycle, record))
    errors.extend(dependency_errors(records))
    if errors:
        raise ValueError("; ".join(errors))
    ordered = topological_order(records)
    digest = registry_digest(records)
    specs = []
    queue = []
    for index, record in enumerate(ordered, start=1):
        data = record.data
        specs.append({
            "order": index * 10,
            "order_hint": data.get("order_hint"),
            "spec_id": data["spec_id"],
            "feature_key": data["feature_key"],
            "title": data["title"],
            "type": data["type"],
            "classification": data["classification"],
            "depends_on_features": data.get("depends_on_features", []),
            "depends_on_specs": data.get("depends_on_specs", []),
            "status": data["status"],
            "feature_version": data["feature_version"],
        })
        handoff = data.get("handoff") or {}
        if handoff.get("status") in {"ready_for_prepare_define", "blocked", "needs_discovery"}:
            queue.append({
                "spec_id": data["spec_id"],
                "feature_key": data["feature_key"],
                "title": data["title"],
                "handoff_status": handoff.get("status"),
                "downstream_mode": handoff.get("downstream_mode"),
                "package_shape": handoff.get("package_shape"),
                "source_candidates": handoff.get("source_candidates", []),
                "seed_artifacts": handoff.get("seed_artifacts", []),
                "define_target": f"specs/{data['spec_id']}/",
                "blockers": handoff.get("blockers", []),
            })
    catalog = {
        "kind": CANONICAL_CATALOG_KIND,
        "generated": True,
        "cycle_id": cycle["cycle_id"],
        "cycle_status": cycle["status"],
        "registry_digest": digest,
        "specs": specs,
    }
    define_queue = {
        "kind": CANONICAL_QUEUE_KIND,
        "generated": True,
        "cycle_id": cycle["cycle_id"],
        "registry_digest": digest,
        "entries": queue,
    }
    return catalog, define_queue


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render deterministic registry views.")
    parser.add_argument("board_root")
    parser.add_argument("--output", required=True, help="External output directory; must not be inside BOARD_ROOT")
    args = parser.parse_args(argv)
    board_root = Path(args.board_root).resolve()
    output = Path(args.output).resolve()
    try:
        output.relative_to(board_root)
        print("ERROR: generated views must be written outside BOARD_ROOT")
        return 1
    except ValueError:
        pass
    try:
        catalog, queue = build_views(board_root)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    output.mkdir(parents=True, exist_ok=True)
    (output / "spec-catalog.yaml").write_text(dump_yaml(catalog), encoding="utf-8")
    (output / "define-queue.yaml").write_text(dump_yaml(queue), encoding="utf-8")
    print(f"OK: rendered 2 deterministic views to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
