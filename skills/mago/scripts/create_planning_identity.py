#!/usr/bin/env python3
"""Atomically create canonical MAGO cycle and spec identities."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

from mago_utils import (
    atomic_write_text,
    board_root as canonical_board_root,
    CANONICAL_CYCLE_KIND,
    CANONICAL_SPEC_KIND,
    make_cycle_id,
    make_spec_id,
    normalize_utc_timestamp,
    parse_cycle_id,
    parse_spec_id,
    slugify,
    SEMVER_RE,
)


def dump_yaml(data: dict[str, Any]) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_or_reuse_identical(path: Path, payload: dict[str, Any]) -> None:
    text = dump_yaml(payload)
    try:
        atomic_write_text(path, text)
        return
    except FileExistsError:
        if yaml is None:
            raise RuntimeError("PyYAML is required")
        try:
            existing = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            raise FileExistsError(f"{path}: identity path exists but cannot be verified: {exc}") from exc
        if existing == payload:
            print(f"REUSED: identical identity already exists: {path}", file=sys.stderr)
            return
        raise FileExistsError(f"{path}: identity path already exists with a different record")


def create_cycle(args: argparse.Namespace) -> Path:
    repo_root = Path(args.repo_root).resolve()
    board_id = slugify(args.board_id)
    cycle_key = slugify(args.cycle_key)
    created_at = normalize_utc_timestamp(args.created_at or utc_now())
    created_date = created_at[:10]
    cycle_id = make_cycle_id(cycle_key, created_date)
    parse_cycle_id(cycle_id)
    board_root = canonical_board_root(repo_root, board_id, created_date[:4], cycle_id)
    cycle_path = board_root / "cycle.yaml"
    if args.proposed_version and not SEMVER_RE.fullmatch(args.proposed_version):
        raise ValueError("proposed_version must use semantic versioning")
    payload = {
        "kind": CANONICAL_CYCLE_KIND,
        "cycle_id": cycle_id,
        "cycle_key": cycle_key,
        "board_id": board_id,
        "year": int(created_date[:4]),
        "created_at": created_at,
        "created_by": args.created_by,
        "status": "proposed",
        "proposed_version": args.proposed_version,
        "accepted_version": None,
        "planning_revision": 1,
        "imported_from": None,
    }
    board_root.mkdir(parents=True, exist_ok=True)
    write_or_reuse_identical(cycle_path, payload)
    (board_root / "registry").mkdir(exist_ok=True)
    (board_root / "specs").mkdir(exist_ok=True)
    (board_root / "candidates").mkdir(exist_ok=True)
    return board_root


def load_cycle(board_root: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    path = board_root / "cycle.yaml"
    if not path.is_file():
        raise ValueError(f"canonical cycle.yaml not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or data.get("kind") != CANONICAL_CYCLE_KIND:
        raise ValueError(f"invalid canonical cycle metadata: {path}")
    return data


def create_spec(args: argparse.Namespace) -> Path:
    board_root = Path(args.board_root).resolve()
    cycle = load_cycle(board_root)
    feature_key = slugify(args.feature_key)
    title = args.title.strip()
    if not title:
        raise ValueError("title is required")
    created_at = normalize_utc_timestamp(args.created_at or utc_now())
    if not SEMVER_RE.fullmatch(args.feature_version):
        raise ValueError("feature_version must use semantic versioning")
    spec_id = make_spec_id(feature_key, created_at[:10])
    parse_spec_id(spec_id)
    registry_path = board_root / "registry" / f"{spec_id}.yaml"
    payload = {
        "kind": CANONICAL_SPEC_KIND,
        "spec_id": spec_id,
        "cycle_id": cycle["cycle_id"],
        "feature_key": feature_key,
        "feature_version": args.feature_version,
        "title": title,
        "type": args.type,
        "classification": args.classification,
        "created_at": created_at,
        "status": "planned",
        "priority": args.priority,
        "order_hint": args.order_hint,
        "depends_on_features": [],
        "depends_on_specs": [],
        "supersedes": [],
        "superseded_by": None,
        "handoff": {
            "status": args.handoff_status,
            "downstream_mode": args.downstream_mode,
            "package_shape": args.package_shape,
            "source_candidates": [],
            "seed_artifacts": ["manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"],
            "blockers": [],
        },
        "imported_from": None,
    }
    write_or_reuse_identical(registry_path, payload)
    return registry_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create concurrent-safe MAGO identities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cycle = subparsers.add_parser("cycle", help="Create one canonical cycle atomically.")
    cycle.add_argument("--repo-root", required=True)
    cycle.add_argument("--board-id", required=True)
    cycle.add_argument("--cycle-key", required=True)
    cycle.add_argument("--created-by", default="mago")
    cycle.add_argument("--created-at", help="ISO-8601 UTC timestamp; defaults to now")
    cycle.add_argument("--proposed-version")

    spec = subparsers.add_parser("spec", help="Create one independent registry entry atomically.")
    spec.add_argument("--board-root", required=True)
    spec.add_argument("--feature-key", required=True)
    spec.add_argument("--title", required=True)
    spec.add_argument("--feature-version", default="0.1.0")
    spec.add_argument("--type", choices=("feature", "fix"), default="feature")
    spec.add_argument("--classification", default="internal")
    spec.add_argument("--priority", choices=("critical", "high", "normal", "low"), default="normal")
    spec.add_argument("--order-hint", type=int)
    spec.add_argument("--handoff-status", choices=("ready_for_prepare_define", "blocked", "needs_discovery"), default="needs_discovery")
    spec.add_argument("--downstream-mode", choices=("define", "define-product", "define-tasks"), default="define")
    spec.add_argument("--package-shape", choices=("full", "product_only", "tasks_only"), default="full")
    spec.add_argument("--created-at", help="ISO-8601 UTC timestamp; defaults to now")

    args = parser.parse_args(argv)
    try:
        path = create_cycle(args) if args.command == "cycle" else create_spec(args)
    except FileExistsError as exc:
        print(f"ERROR: identity collision; no suffix or counter was generated: {exc}")
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
