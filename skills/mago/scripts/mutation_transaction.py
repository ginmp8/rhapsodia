#!/usr/bin/env python3
"""Execute recoverable multi-artifact Mago planning transactions.

The transaction workspace must be outside the canonical package. The script
never treats a successful filesystem write as runtime/product evidence; it only
protects Mago-owned planning artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

STATE_FILE = "transaction.json"
STAGED_DIR = "staged"
BACKUP_DIR = "backup"
VALID_ACTIVE = {"in_progress", "cancelled", "rollback_required"}


class TransactionError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_relative(raw: str) -> str:
    candidate = PurePosixPath(raw.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts:
        raise TransactionError(f"unsafe write path: {raw!r}")
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise TransactionError(f"unsafe write path: {raw!r}")
    normalized = candidate.as_posix()
    if normalized == "manifest.yaml":
        raise TransactionError("manifest.yaml is transaction metadata and cannot be in planned_writes")
    return normalized


def require_regular_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise TransactionError(f"{label} must be a regular non-symlink file: {path}")


def load_manifest(package: Path) -> dict[str, Any]:
    path = package / "manifest.yaml"
    require_regular_file(path, "manifest")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TransactionError("manifest.yaml must contain a mapping")
    return data


def write_manifest(package: Path, data: dict[str, Any]) -> None:
    destination = package / "manifest.yaml"
    atomic_write(destination, yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode("utf-8"))


def canonical_manifest_hash(data: dict[str, Any]) -> str:
    normalized = dict(data)
    normalized["mutation_state"] = {
        "status": "clean",
        "transaction_id": None,
        "inspected_digest": None,
        "planned_writes": [],
        "completed_writes": [],
        "checkpoint": None,
        "cancellation_requested": False,
        "rollback_required": False,
    }
    payload = yaml.safe_dump(normalized, sort_keys=True, allow_unicode=True).encode("utf-8")
    return sha256_bytes(payload)


def package_snapshot(package: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(package.rglob("*")):
        if path.is_symlink():
            raise TransactionError(f"symlinks are not allowed in transaction scope: {path}")
        if not path.is_file():
            continue
        rel = path.relative_to(package).as_posix()
        if rel == "manifest.yaml":
            continue
        snapshot[rel] = sha256_file(path)
    return snapshot


def snapshot_digest(files: dict[str, str], manifest_hash: str) -> str:
    payload = json.dumps(
        {"files": files, "manifest": manifest_hash},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + sha256_bytes(payload)


def atomic_write(destination: Path, content: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.parent.is_symlink():
        raise TransactionError(f"destination parent cannot be a symlink: {destination.parent}")
    fd, raw_temp = tempfile.mkstemp(prefix=f".{destination.name}.", dir=str(destination.parent))
    temp_path = Path(raw_temp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def state_path(workspace: Path) -> Path:
    return workspace / STATE_FILE


def save_state(workspace: Path, state: dict[str, Any]) -> None:
    atomic_write(state_path(workspace), (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def load_state(workspace: Path) -> dict[str, Any]:
    path = state_path(workspace)
    require_regular_file(path, "transaction state")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TransactionError("transaction state must be an object")
    return data


def resolve_package(state: dict[str, Any]) -> Path:
    package = Path(str(state.get("package", ""))).resolve()
    if not package.is_dir():
        raise TransactionError(f"package no longer exists: {package}")
    return package


def mutation_projection(state: dict[str, Any], *, status: str | None = None, checkpoint: str | None = None) -> dict[str, Any]:
    selected_status = status or str(state["status"])
    return {
        "status": selected_status,
        "transaction_id": state["transaction_id"],
        "inspected_digest": state["inspected_digest"],
        "planned_writes": list(state["planned_writes"]),
        "completed_writes": list(state["completed_writes"]),
        "checkpoint": checkpoint or state.get("checkpoint") or "unknown",
        "cancellation_requested": bool(state.get("cancellation_requested", False)),
        "rollback_required": selected_status == "rollback_required" or bool(state.get("rollback_required", False)),
    }


def update_manifest_state(package: Path, state: dict[str, Any], *, status: str | None = None, checkpoint: str | None = None) -> None:
    manifest = load_manifest(package)
    manifest["mutation_state"] = mutation_projection(state, status=status, checkpoint=checkpoint)
    write_manifest(package, manifest)


def set_manifest_clean(package: Path) -> None:
    manifest = load_manifest(package)
    manifest["mutation_state"] = {
        "status": "clean",
        "transaction_id": None,
        "inspected_digest": None,
        "planned_writes": [],
        "completed_writes": [],
        "checkpoint": None,
        "cancellation_requested": False,
        "rollback_required": False,
    }
    write_manifest(package, manifest)


def assert_manifest_matches_transaction(package: Path, state: dict[str, Any], allowed_statuses: set[str]) -> None:
    manifest = load_manifest(package)
    mutation = manifest.get("mutation_state")
    if not isinstance(mutation, dict):
        raise TransactionError("manifest mutation_state is missing")
    if mutation.get("transaction_id") != state.get("transaction_id"):
        raise TransactionError("manifest belongs to a different transaction")
    status = str(mutation.get("status", ""))
    if status not in allowed_statuses:
        raise TransactionError(f"transaction cannot continue from manifest status {status!r}")


def verify_preconditions(package: Path, workspace: Path, state: dict[str, Any]) -> None:
    manifest = load_manifest(package)
    current_manifest_hash = canonical_manifest_hash(manifest)
    if current_manifest_hash != state["baseline_manifest_hash"]:
        raise TransactionError("canonical manifest fields drifted after transaction begin")

    current = package_snapshot(package)
    baseline: dict[str, str] = state["baseline_files"]
    planned = set(state["planned_writes"])
    completed = set(state["completed_writes"])
    staged_hashes: dict[str, str] = state.get("staged_hashes", {})

    expected_paths = set(baseline)
    expected_paths.update(rel for rel in completed if rel in staged_hashes)
    unexpected = sorted(set(current) - expected_paths - (planned - completed))
    if unexpected:
        raise TransactionError(f"unrelated package files appeared during transaction: {unexpected}")

    for rel, original_hash in baseline.items():
        if rel in completed:
            expected = staged_hashes.get(rel)
            if not expected or current.get(rel) != expected:
                raise TransactionError(f"completed write drifted: {rel}")
        elif current.get(rel) != original_hash:
            raise TransactionError(f"canonical input drifted: {rel}")

    for rel in completed:
        if rel not in baseline:
            expected = staged_hashes.get(rel)
            if not expected or current.get(rel) != expected:
                raise TransactionError(f"new completed write drifted: {rel}")


def begin(args: argparse.Namespace) -> int:
    package = Path(args.package).resolve()
    workspace = Path(args.workspace).resolve()
    if not package.is_dir():
        raise TransactionError(f"package is not a directory: {package}")
    try:
        workspace.relative_to(package)
    except ValueError:
        pass
    else:
        raise TransactionError("transaction workspace must be outside the canonical package")
    if workspace.exists():
        raise TransactionError(f"transaction workspace already exists: {workspace}")

    writes = [safe_relative(item) for item in args.write]
    if not writes or len(set(writes)) != len(writes):
        raise TransactionError("planned writes must be a non-empty unique list")

    manifest = load_manifest(package)
    mutation = manifest.get("mutation_state")
    if not isinstance(mutation, dict) or mutation.get("status") != "clean":
        raise TransactionError("package must have a clean mutation_state before begin")

    files = package_snapshot(package)
    manifest_hash = canonical_manifest_hash(manifest)
    digest = snapshot_digest(files, manifest_hash)
    workspace.mkdir(parents=True, exist_ok=False)
    (workspace / STAGED_DIR).mkdir()
    (workspace / BACKUP_DIR).mkdir()

    originals: dict[str, dict[str, Any]] = {}
    for rel in writes:
        source = package / rel
        backup = workspace / BACKUP_DIR / rel
        if source.exists():
            require_regular_file(source, "planned destination")
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, backup)
            originals[rel] = {"existed": True, "sha256": sha256_file(source)}
        else:
            originals[rel] = {"existed": False, "sha256": None}

    state: dict[str, Any] = {
        "schema_version": 1,
        "transaction_id": args.transaction_id or f"tx-{uuid.uuid4().hex}",
        "package": str(package),
        "status": "in_progress",
        "checkpoint": "begun",
        "inspected_digest": digest,
        "baseline_manifest_hash": manifest_hash,
        "baseline_files": files,
        "planned_writes": writes,
        "completed_writes": [],
        "staged_hashes": {},
        "originals": originals,
        "cancellation_requested": False,
        "rollback_required": False,
    }
    save_state(workspace, state)
    update_manifest_state(package, state)
    print(json.dumps({"status": "in_progress", "transaction_id": state["transaction_id"], "digest": digest}))
    return 0


def stage(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    source_dir = Path(args.source_dir).resolve()
    state = load_state(workspace)
    package = resolve_package(state)
    assert_manifest_matches_transaction(package, state, {"in_progress"})
    verify_preconditions(package, workspace, state)
    if not source_dir.is_dir():
        raise TransactionError(f"source_dir is not a directory: {source_dir}")

    staged_hashes: dict[str, str] = {}
    for rel in state["planned_writes"]:
        source = source_dir / rel
        require_regular_file(source, "staged source")
        destination = workspace / STAGED_DIR / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        staged_hashes[rel] = sha256_file(destination)
    state["staged_hashes"] = staged_hashes
    state["checkpoint"] = "staged"
    save_state(workspace, state)
    update_manifest_state(package, state)
    print(json.dumps({"status": "in_progress", "checkpoint": "staged", "files": len(staged_hashes)}))
    return 0


def _promote(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    state = load_state(workspace)
    package = resolve_package(state)
    assert_manifest_matches_transaction(package, state, {"in_progress"})
    if state.get("checkpoint") not in {"staged", "promoting", "interrupted"}:
        raise TransactionError(f"transaction is not staged: checkpoint={state.get('checkpoint')!r}")
    if set(state.get("staged_hashes", {})) != set(state["planned_writes"]):
        raise TransactionError("staged write set does not match planned write set")
    verify_preconditions(package, workspace, state)

    promoted_this_call = 0
    state["checkpoint"] = "promoting"
    save_state(workspace, state)
    update_manifest_state(package, state)

    try:
        for rel in state["planned_writes"]:
            if rel in state["completed_writes"]:
                continue
            staged = workspace / STAGED_DIR / rel
            require_regular_file(staged, "staged file")
            destination = package / rel
            atomic_write(destination, staged.read_bytes())
            state["completed_writes"].append(rel)
            promoted_this_call += 1
            state["checkpoint"] = f"promoted:{rel}"
            save_state(workspace, state)
            update_manifest_state(package, state)

            if args.interrupt_after is not None and promoted_this_call >= args.interrupt_after:
                state["checkpoint"] = "interrupted"
                save_state(workspace, state)
                update_manifest_state(package, state)
                print(json.dumps({"status": "in_progress", "checkpoint": "interrupted", "completed": state["completed_writes"]}))
                return 75
            if args.fail_after is not None and promoted_this_call >= args.fail_after:
                raise TransactionError("injected promotion failure")
    except Exception:
        state["status"] = "rollback_required"
        state["rollback_required"] = True
        state["checkpoint"] = "promotion_failed"
        save_state(workspace, state)
        update_manifest_state(package, state, status="rollback_required")
        raise

    state["status"] = "completed"
    state["checkpoint"] = "completed"
    save_state(workspace, state)
    set_manifest_clean(package)
    print(json.dumps({"status": "completed", "completed": state["completed_writes"]}))
    return 0


def cancel(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    state = load_state(workspace)
    package = resolve_package(state)
    assert_manifest_matches_transaction(package, state, {"in_progress"})
    if state["completed_writes"]:
        raise TransactionError("cannot cancel after promotion; rollback is required")
    state["status"] = "cancelled"
    state["cancellation_requested"] = True
    state["checkpoint"] = "cancelled"
    save_state(workspace, state)
    update_manifest_state(package, state, status="cancelled")
    print(json.dumps({"status": "cancelled"}))
    return 0


def rollback(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    state = load_state(workspace)
    package = resolve_package(state)
    assert_manifest_matches_transaction(package, state, VALID_ACTIVE)

    errors: list[str] = []
    for rel in reversed(state["planned_writes"]):
        destination = package / rel
        original = state["originals"][rel]
        try:
            if original["existed"]:
                backup = workspace / BACKUP_DIR / rel
                require_regular_file(backup, "backup")
                atomic_write(destination, backup.read_bytes())
                if sha256_file(destination) != original["sha256"]:
                    raise TransactionError(f"restored hash mismatch: {rel}")
            elif destination.exists():
                if destination.is_symlink() or not destination.is_file():
                    raise TransactionError(f"cannot safely remove non-file destination: {rel}")
                destination.unlink()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel}: {exc}")

    if errors:
        state["status"] = "rollback_required"
        state["rollback_required"] = True
        state["checkpoint"] = "rollback_failed"
        save_state(workspace, state)
        update_manifest_state(package, state, status="rollback_required")
        raise TransactionError("rollback failed: " + "; ".join(errors))

    current_files = package_snapshot(package)
    if current_files != state["baseline_files"]:
        raise TransactionError("rollback did not restore the baseline file snapshot")
    if canonical_manifest_hash(load_manifest(package)) != state["baseline_manifest_hash"]:
        raise TransactionError("rollback did not restore canonical manifest fields")

    state["status"] = "rolled_back"
    state["rollback_required"] = False
    state["checkpoint"] = "rolled_back"
    save_state(workspace, state)
    set_manifest_clean(package)
    print(json.dumps({"status": "rolled_back"}))
    return 0


def status(args: argparse.Namespace) -> int:
    state = load_state(Path(args.workspace).resolve())
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recoverable transaction runner for Mago planning artifacts.")
    sub = parser.add_subparsers(dest="command", required=True)

    begin_parser = sub.add_parser("begin")
    begin_parser.add_argument("--package", required=True)
    begin_parser.add_argument("--workspace", required=True)
    begin_parser.add_argument("--write", action="append", required=True)
    begin_parser.add_argument("--transaction-id")
    begin_parser.set_defaults(handler=begin)

    stage_parser = sub.add_parser("stage")
    stage_parser.add_argument("--workspace", required=True)
    stage_parser.add_argument("--source-dir", required=True)
    stage_parser.set_defaults(handler=stage)

    for name in ("promote", "resume"):
        promote_parser = sub.add_parser(name)
        promote_parser.add_argument("--workspace", required=True)
        promote_parser.add_argument("--interrupt-after", type=int)
        promote_parser.add_argument("--fail-after", type=int)
        promote_parser.set_defaults(handler=_promote)

    cancel_parser = sub.add_parser("cancel")
    cancel_parser.add_argument("--workspace", required=True)
    cancel_parser.set_defaults(handler=cancel)

    rollback_parser = sub.add_parser("rollback")
    rollback_parser.add_argument("--workspace", required=True)
    rollback_parser.set_defaults(handler=rollback)

    status_parser = sub.add_parser("status")
    status_parser.add_argument("--workspace", required=True)
    status_parser.set_defaults(handler=status)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except TransactionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
