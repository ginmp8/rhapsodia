#!/usr/bin/env python3
"""Create and transition drift-safe MAGIA run-state JSON documents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TERMINAL = {"cancelled", "rolled_back", "handed_off", "blocked", "closed"}
VALID_STATUSES = {"active", "cancelled", "retry_pending", "rollback_pending", "rolled_back", "handed_off", "blocked", "closed"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "size": 0, "sha256": None}
    if not path.is_file():
        raise ValueError(f"tracked path must be a file: {path}")
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return {"exists": True, "size": path.stat().st_size, "sha256": hasher.hexdigest()}


def resolve_under(root: Path, raw: str) -> tuple[str, Path]:
    candidate = Path(raw)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root / candidate).resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(f"tracked path escapes repository root: {raw}") from exc
    return relative, resolved


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp_name = handle.name
    os.replace(temp_name, path)


def load_state(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("state root must be an object")
    required = {"schema_version", "run_id", "mode", "profile", "repository_root", "status", "tracked_files", "checkpoint", "pending_step"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"state missing fields: {missing}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {data['schema_version']}")
    if data["status"] not in VALID_STATUSES:
        raise ValueError(f"invalid state status: {data['status']}")
    return data


def add_tracking(state: dict[str, Any], files: list[str]) -> None:
    root = Path(state["repository_root"]).resolve()
    tracked = state.setdefault("tracked_files", {})
    for raw in files:
        relative, resolved = resolve_under(root, raw)
        tracked[relative] = digest(resolved)


def verify_drift(state: dict[str, Any]) -> list[dict[str, Any]]:
    root = Path(state["repository_root"]).resolve()
    drift: list[dict[str, Any]] = []
    for relative, expected in state.get("tracked_files", {}).items():
        _, resolved = resolve_under(root, relative)
        actual = digest(resolved)
        if actual != expected:
            drift.append({"path": relative, "expected": expected, "actual": actual})
    return drift


def initialize(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        raise ValueError(f"repository root does not exist: {root}")
    if args.profile not in {"quick", "standard", "governed"}:
        raise ValueError("profile must be quick, standard, or governed")
    if args.mode not in {"adhoc", "ralph", "adapt"}:
        raise ValueError("mode must be adhoc, ralph, or adapt")
    timestamp = now()
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "mode": args.mode,
        "profile": args.profile,
        "repository_root": str(root),
        "scope": args.scope,
        "task": args.task,
        "allowed_writes": list(dict.fromkeys(args.allowed_write or [])),
        "tracked_files": {},
        "inspected_files": [],
        "planned_writes": [],
        "completed_writes": [],
        "commands": [],
        "checkpoint": "initialized",
        "pending_step": "inspect",
        "status": "active",
        "retry_count": 0,
        "cancellation_reason": None,
        "rollback_evidence": [],
        "handoff": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    add_tracking(state, args.track or [])
    return state


def update_common(state: dict[str, Any]) -> None:
    state["updated_at"] = now()


def command_result(raw: str) -> dict[str, Any]:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("--command-json must contain an object")
    if value.get("status") not in {"pass", "fail", "not_run"}:
        raise ValueError("command status must be pass, fail, or not_run")
    return value


def transition(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    state_path = Path(args.state).resolve()
    state = load_state(state_path)
    action = args.action
    if action == "resume":
        if state["status"] in TERMINAL:
            return {"status": "blocked", "reason": f"terminal run state: {state['status']}"}, 2
        drift = verify_drift(state)
        if drift:
            state["status"] = "blocked"
            state["checkpoint"] = "resume_blocked"
            state["pending_step"] = "reinspect_after_drift"
            update_common(state)
            atomic_write(state_path, state)
            return {"status": "repository_drift", "drift": drift, "state": state}, 2
        state["status"] = "active"
        update_common(state)
        atomic_write(state_path, state)
        return {"status": "resume_allowed", "state": state}, 0

    if state["status"] in TERMINAL and action not in {"show"}:
        raise ValueError(f"cannot transition terminal state: {state['status']}")

    if action == "checkpoint":
        state["checkpoint"] = args.checkpoint
        state["pending_step"] = args.pending_step
        state["inspected_files"] = list(dict.fromkeys(state.get("inspected_files", []) + (args.inspected_file or [])))
        state["planned_writes"] = list(dict.fromkeys(state.get("planned_writes", []) + (args.planned_write or [])))
        state["completed_writes"] = list(dict.fromkeys(state.get("completed_writes", []) + (args.completed_write or [])))
        add_tracking(state, args.track or [])
        if args.command_json:
            state.setdefault("commands", []).append(command_result(args.command_json))
    elif action == "cancel":
        state["status"] = "cancelled"
        state["cancellation_reason"] = args.reason
        state["pending_step"] = "assess_rollback"
    elif action == "retry":
        drift = verify_drift(state)
        if drift:
            state["status"] = "blocked"
            state["pending_step"] = "reinspect_after_drift"
            update_common(state)
            atomic_write(state_path, state)
            return {"status": "repository_drift", "drift": drift, "state": state}, 2
        state["status"] = "retry_pending"
        state["retry_count"] = int(state.get("retry_count", 0)) + 1
        state["pending_step"] = args.pending_step
    elif action == "rollback":
        state["status"] = "rolled_back" if args.result == "pass" else "blocked"
        state["checkpoint"] = "rollback_complete" if args.result == "pass" else "rollback_failed"
        state["pending_step"] = None if args.result == "pass" else "escalate_rollback_failure"
        state.setdefault("rollback_evidence", []).append({"status": args.result, "evidence": args.evidence})
    elif action == "handoff":
        state["status"] = "handed_off"
        state["pending_step"] = None
        state["handoff"] = {"owner": args.owner, "reason": args.reason, "evidence": args.evidence}
    elif action == "close":
        drift = verify_drift(state)
        if drift:
            return {"status": "repository_drift", "drift": drift, "state": state}, 2
        state["status"] = "closed"
        state["checkpoint"] = "closed"
        state["pending_step"] = None
    elif action == "show":
        return state, 0
    else:
        raise ValueError(f"unsupported action: {action}")

    update_common(state)
    atomic_write(state_path, state)
    return state, 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="action", required=True)
    init = sub.add_parser("init")
    init.add_argument("--state", required=True)
    init.add_argument("--run-id", required=True)
    init.add_argument("--mode", required=True)
    init.add_argument("--profile", required=True)
    init.add_argument("--repo-root", required=True)
    init.add_argument("--scope", required=True)
    init.add_argument("--task")
    init.add_argument("--allowed-write", action="append")
    init.add_argument("--track", action="append")

    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("--state", required=True)
    checkpoint.add_argument("--checkpoint", required=True)
    checkpoint.add_argument("--pending-step", required=True)
    checkpoint.add_argument("--inspected-file", action="append")
    checkpoint.add_argument("--planned-write", action="append")
    checkpoint.add_argument("--completed-write", action="append")
    checkpoint.add_argument("--track", action="append")
    checkpoint.add_argument("--command-json")

    for name in ("resume", "show", "close"):
        item = sub.add_parser(name)
        item.add_argument("--state", required=True)

    cancel = sub.add_parser("cancel")
    cancel.add_argument("--state", required=True)
    cancel.add_argument("--reason", required=True)

    retry = sub.add_parser("retry")
    retry.add_argument("--state", required=True)
    retry.add_argument("--pending-step", required=True)

    rollback = sub.add_parser("rollback")
    rollback.add_argument("--state", required=True)
    rollback.add_argument("--result", choices=["pass", "fail", "not_run"], required=True)
    rollback.add_argument("--evidence", required=True)

    handoff = sub.add_parser("handoff")
    handoff.add_argument("--state", required=True)
    handoff.add_argument("--owner", choices=["mago", "nomia", "repository_owner", "operator"], required=True)
    handoff.add_argument("--reason", required=True)
    handoff.add_argument("--evidence", required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.action == "init":
            state = initialize(args)
            atomic_write(Path(args.state).resolve(), state)
            result, code = state, 0
        else:
            result, code = transition(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
