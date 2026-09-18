#!/usr/bin/env python3
"""Synchronize MAGIA execution state with semantic preflight and recoverable commit."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
import uuid
from datetime import date
from pathlib import Path, PurePosixPath

from board_contract import registry_for
from magia_utils import (
    BOARD_ROOT_TEMPLATE,
    load_local_module,
    load_yaml,
    parse_spec_id,
    print_errors,
    replace_top_level_scalar,
    spec_package_path,
    spec_package_path_error,
    spec_registry_path,
    write_text,
    yaml_quote,
)

TASK_LINE_RE = re.compile(r"^(?P<prefix>\s*-\s*)\[(?P<mark>[ xX])\](?P<suffix>\s+(?P<task_id>task\d{3}):\s+.+)$")
VALID_SYNC_STATUSES = {"in_progress", "blocked", "done"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TRANSACTION_DIR_NAME = ".magia-state-transaction"
LOCK_FILE_NAME = ".magia-state.lock"
BACKUP_NAME_RE = re.compile(r"^backup-\d+\.bin$")


def render_tasks_text(original: str, task_id: str, status: str) -> tuple[str, dict[str, bool]]:
    lines = original.splitlines()
    mark = "x" if status == "done" else " "
    found = False
    task_states: dict[str, bool] = {}
    for index, line in enumerate(lines):
        match = TASK_LINE_RE.match(line)
        if not match:
            continue
        current_id = match.group("task_id")
        if current_id == task_id:
            lines[index] = f"{match.group('prefix')}[{mark}]{match.group('suffix')}"
            found = True
            task_states[current_id] = status == "done"
        else:
            task_states[current_id] = match.group("mark").lower() == "x"
    if not found:
        raise ValueError(f"`{task_id}` not found in tasks.md")
    content = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
    return content, task_states


def update_tasks_file(tasks_path: Path, task_id: str, status: str) -> dict[str, bool]:
    """Compatibility helper for a single-file update; closure uses atomic_write_many."""
    content, task_states = render_tasks_text(tasks_path.read_text(encoding="utf-8-sig"), task_id, status)
    write_text(tasks_path, content)
    return task_states


def build_last_execution_block(task_id: str, execution_date: str, summary: str | None, files_changed: list[str]) -> list[str]:
    lines = [
        "last_execution:",
        f"  task_id: {yaml_quote(task_id)}",
        f"  date: {yaml_quote(execution_date)}",
    ]
    if summary:
        lines.append(f"  summary: {yaml_quote(summary)}")
    if files_changed:
        lines.append("  files_changed:")
        lines.extend(f"    - {yaml_quote(item)}" for item in files_changed)
    return lines


def remove_last_execution(lines: list[str]) -> list[str]:
    output: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].startswith("last_execution:"):
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                index += 1
            continue
        output.append(lines[index])
        index += 1
    while output and not output[-1].strip():
        output.pop()
    return output


def render_manifest_text(
    original: str,
    *,
    spec_status: str,
    phase: str,
    task_id: str,
    execution_date: str,
    summary: str | None,
    files_changed: list[str],
) -> str:
    lines = original.splitlines()
    replace_top_level_scalar(lines, "status", spec_status)
    replace_top_level_scalar(lines, "phase", phase)
    lines = remove_last_execution(lines)
    lines.extend(["", *build_last_execution_block(task_id, execution_date, summary, files_changed)])
    return "\n".join(lines) + "\n"


def update_manifest_file(
    manifest_path: Path,
    *,
    spec_status: str,
    phase: str,
    task_id: str,
    execution_date: str,
    summary: str | None,
    files_changed: list[str],
) -> None:
    content = render_manifest_text(
        manifest_path.read_text(encoding="utf-8-sig"),
        spec_status=spec_status,
        phase=phase,
        task_id=task_id,
        execution_date=execution_date,
        summary=summary,
        files_changed=files_changed,
    )
    write_text(manifest_path, content)


def render_registry_text(original: str, spec_status: str) -> str:
    lines = original.splitlines()
    replace_top_level_scalar(lines, "status", spec_status)
    return "\n".join(lines) + ("\n" if original.endswith("\n") else "")


def update_registry_file(registry_path: Path, spec_status: str) -> None:
    write_text(registry_path, render_registry_text(registry_path.read_text(encoding="utf-8-sig"), spec_status))


def _fsync_path(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.magia-tmp-{uuid.uuid4().hex}")
    try:
        with temporary.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _allowed_transaction_targets(spec_package: Path) -> set[Path]:
    board_root = spec_package.parent.parent.resolve()
    spec_id = spec_package.name
    return {
        (spec_package / "tasks.md").resolve(),
        (spec_package / "manifest.yaml").resolve(),
        (board_root / "registry" / f"{spec_id}.yaml").resolve(),
    }


def _resolve_write_target(spec_package: Path, target: Path) -> Path:
    if target.is_symlink():
        raise ValueError(f"transaction target must not be a symlink: {target}")
    resolved = target.resolve()
    board_root = spec_package.parent.parent.resolve()
    try:
        resolved.relative_to(board_root)
    except ValueError as exc:
        raise ValueError(f"transaction target escapes BOARD_ROOT: {target}") from exc
    if resolved not in _allowed_transaction_targets(spec_package):
        raise ValueError(f"transaction target is not an authorized execution-state file: {target}")
    if not resolved.is_file():
        raise ValueError(f"transaction target must be an existing regular file: {target}")
    return resolved


def _resolve_journal_target(spec_package: Path, raw_target: object) -> Path:
    if not isinstance(raw_target, str) or not raw_target.strip() or "\\" in raw_target:
        raise RuntimeError("transaction target must be a non-empty canonical POSIX path")
    relative = PurePosixPath(raw_target)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise RuntimeError(f"transaction target is not a safe relative path: {raw_target}")
    board_root = spec_package.parent.parent.resolve()
    candidate = board_root.joinpath(*relative.parts)
    try:
        return _resolve_write_target(spec_package, candidate)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc


def _resolve_journal_backup(transaction_dir: Path, raw_backup: object, *, required: bool) -> Path:
    if not isinstance(raw_backup, str) or not BACKUP_NAME_RE.fullmatch(raw_backup):
        raise RuntimeError(f"transaction backup has an invalid name: {raw_backup}")
    relative = PurePosixPath(raw_backup)
    if len(relative.parts) != 1:
        raise RuntimeError(f"transaction backup must be a direct journal member: {raw_backup}")
    backup = transaction_dir / raw_backup
    if backup.is_symlink():
        raise RuntimeError(f"transaction backup must not be a symlink: {backup}")
    resolved = backup.resolve()
    try:
        resolved.relative_to(transaction_dir.resolve())
    except ValueError as exc:
        raise RuntimeError(f"transaction backup escapes journal directory: {raw_backup}") from exc
    if required and not resolved.is_file():
        raise RuntimeError(f"transaction backup is missing: {resolved}")
    return resolved


def _load_transaction_journal(spec_package: Path, transaction_dir: Path) -> tuple[str, list[tuple[Path, Path]]]:
    manifest_path = transaction_dir / "transaction.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RuntimeError(f"incomplete transaction journal without manifest: {transaction_dir}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("transaction journal root must be an object")
    state = payload.get("state")
    if state not in {"prepared", "committed"}:
        raise RuntimeError(f"unknown transaction journal state `{state}`")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list) or not 1 <= len(raw_entries) <= 3:
        raise RuntimeError("transaction journal must contain one to three entries")

    entries: list[tuple[Path, Path]] = []
    seen_targets: set[Path] = set()
    seen_backups: set[Path] = set()
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict) or set(raw_entry) != {"target", "backup"}:
            raise RuntimeError("transaction journal entries must contain only target and backup")
        target = _resolve_journal_target(spec_package, raw_entry.get("target"))
        backup = _resolve_journal_backup(
            transaction_dir,
            raw_entry.get("backup"),
            required=state == "prepared",
        )
        if target in seen_targets or backup in seen_backups:
            raise RuntimeError("transaction journal contains duplicate targets or backups")
        seen_targets.add(target)
        seen_backups.add(backup)
        entries.append((target, backup))
    return state, entries


def _process_start_token(pid: int) -> str | None:
    stat_path = Path(f"/proc/{pid}/stat")
    try:
        fields = stat_path.read_text(encoding="utf-8").split()
    except OSError:
        return None
    return fields[21] if len(fields) > 21 else None


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _lock_owner_state(lock_path: Path) -> bool | None:
    if lock_path.is_symlink() or not lock_path.is_file():
        return None
    metadata: dict[str, str] = {}
    try:
        for line in lock_path.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            metadata[key.strip()] = value.strip()
        pid = int(metadata["pid"])
    except (OSError, KeyError, ValueError):
        return None
    if not _pid_is_alive(pid):
        return False
    expected_start = metadata.get("process_start")
    current_start = _process_start_token(pid)
    if expected_start and current_start and expected_start != current_start:
        return False
    return True


def recover_interrupted_transaction(spec_package: Path) -> bool:
    spec_package = spec_package.resolve()
    transaction_dir = spec_package / TRANSACTION_DIR_NAME
    lock_path = spec_package / LOCK_FILE_NAME
    owner_state = _lock_owner_state(lock_path) if lock_path.exists() else False
    if owner_state is True:
        raise RuntimeError(f"execution-state lock is owned by a live process: {lock_path}")
    if owner_state is None:
        raise RuntimeError(f"execution-state lock metadata is invalid or unsafe to recover: {lock_path}")

    if transaction_dir.exists() and (transaction_dir.is_symlink() or not transaction_dir.is_dir()):
        raise RuntimeError(f"transaction journal path must be a real directory: {transaction_dir}")
    if not transaction_dir.is_dir():
        if lock_path.exists():
            lock_path.unlink()
            _fsync_directory(spec_package)
            return True
        return False

    manifest_path = transaction_dir / "transaction.json"
    if not manifest_path.exists():
        if not lock_path.exists():
            raise RuntimeError(f"incomplete transaction journal without recoverable lock: {transaction_dir}")
        shutil.rmtree(transaction_dir)
        lock_path.unlink(missing_ok=True)
        _fsync_directory(spec_package)
        return True

    state, entries = _load_transaction_journal(spec_package, transaction_dir)
    if state == "prepared":
        for target, backup in entries:
            _atomic_write_bytes(target, backup.read_bytes())
    shutil.rmtree(transaction_dir)
    lock_path.unlink(missing_ok=True)
    _fsync_directory(spec_package)
    return True


def _acquire_lock(spec_package: Path) -> Path:
    lock_path = spec_package / LOCK_FILE_NAME
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"execution-state lock already exists: {lock_path}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(f"pid={os.getpid()}\n")
        process_start = _process_start_token(os.getpid())
        if process_start:
            handle.write(f"process_start={process_start}\n")
        handle.write(f"created_unix={time.time_ns()}\n")
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(spec_package)
    return lock_path


def atomic_write_many(
    changes: dict[Path, str],
    spec_package: Path,
    *,
    fail_after_replace: int | None = None,
    expected_originals: dict[Path, bytes] | None = None,
) -> None:
    """Commit several files with a durable journal and rollback on any caught failure."""
    spec_package = spec_package.resolve()
    recover_interrupted_transaction(spec_package)
    lock_path = _acquire_lock(spec_package)
    transaction_dir = spec_package / TRANSACTION_DIR_NAME
    staged: dict[Path, Path] = {}
    entries: list[dict[str, str]] = []
    board_root = spec_package.parent.parent
    try:
        normalized_changes = {_resolve_write_target(spec_package, target): content for target, content in changes.items()}
        if not normalized_changes:
            raise ValueError("transaction requires at least one authorized change")
        normalized_expected: dict[Path, bytes] | None = None
        if expected_originals is not None:
            normalized_expected = {
                _resolve_write_target(spec_package, target): content for target, content in expected_originals.items()
            }
            if set(normalized_expected) != set(normalized_changes):
                raise ValueError("expected originals must cover exactly the transaction targets")
            for target, expected in normalized_expected.items():
                if target.read_bytes() != expected:
                    raise RuntimeError(f"execution-state file changed after preflight: {target}")

        transaction_dir.mkdir(mode=0o700)
        _fsync_directory(spec_package)
        for index, (target, content) in enumerate(normalized_changes.items()):
            relative = target.relative_to(board_root.resolve()).as_posix()
            backup_name = f"backup-{index}.bin"
            backup = transaction_dir / backup_name
            with backup.open("wb") as handle:
                handle.write(target.read_bytes())
                handle.flush()
                os.fsync(handle.fileno())
            temporary = target.with_name(f".{target.name}.magia-tmp-{uuid.uuid4().hex}")
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            staged[target] = temporary
            entries.append({"target": relative, "backup": backup_name})
        _fsync_directory(transaction_dir)

        journal = transaction_dir / "transaction.json"
        _atomic_write_bytes(
            journal,
            (json.dumps({"state": "prepared", "entries": entries}, indent=2) + "\n").encode("utf-8"),
        )

        replaced = 0
        for target, temporary in staged.items():
            os.replace(temporary, target)
            _fsync_directory(target.parent)
            replaced += 1
            if fail_after_replace is not None and replaced >= fail_after_replace:
                raise RuntimeError(f"injected failure after replace {replaced}")

        _atomic_write_bytes(
            journal,
            (json.dumps({"state": "committed", "entries": entries}, indent=2) + "\n").encode("utf-8"),
        )
        shutil.rmtree(transaction_dir)
        _fsync_directory(spec_package)
    except Exception as original_error:
        rollback_error: Exception | None = None
        if transaction_dir.is_dir():
            payload_path = transaction_dir / "transaction.json"
            if payload_path.is_file():
                try:
                    state, validated_entries = _load_transaction_journal(spec_package, transaction_dir)
                    if state == "prepared":
                        for target, backup in validated_entries:
                            _atomic_write_bytes(target, backup.read_bytes())
                    shutil.rmtree(transaction_dir)
                    _fsync_directory(spec_package)
                except Exception as exc:  # noqa: BLE001
                    rollback_error = exc
            else:
                shutil.rmtree(transaction_dir, ignore_errors=True)
                _fsync_directory(spec_package)
        if rollback_error is not None:
            raise RuntimeError(f"transaction failed and rollback could not be verified: {rollback_error}") from original_error
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        lock_path.unlink(missing_ok=True)
        _fsync_directory(spec_package)


def validate_candidate_snapshot(
    board_root: Path,
    spec_id: str,
    changes: dict[Path, str],
    validate_module,
) -> list[str]:
    live_package = spec_package_path(board_root, spec_id)
    with tempfile.TemporaryDirectory(prefix="magia-state-candidate-") as temporary_dir:
        staged_root = Path(temporary_dir) / board_root.name
        shutil.copytree(board_root, staged_root)
        for target, content in changes.items():
            safe_target = _resolve_write_target(live_package, target)
            staged_target = staged_root / safe_target.relative_to(board_root.resolve())
            staged_target.write_text(content, encoding="utf-8", newline="\n")
        staged_package = spec_package_path(staged_root, spec_id)
        return validate_module.collect_errors(staged_package)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize canonical MAGIA execution state after semantic preflight and candidate validation."
    )
    parser.add_argument("board_root", help=f"Canonical board root under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Canonical spec ID: spec-YYYY-MM-DD-feature-key.")
    parser.add_argument("--task-id", required=True, help="Executed task ID in taskNNN form.")
    parser.add_argument("--status", required=True, choices=sorted(VALID_SYNC_STATUSES))
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--summary")
    parser.add_argument("--files-changed", nargs="*", default=[])
    args = parser.parse_args(argv)

    errors: list[str] = []
    if not DATE_RE.fullmatch(args.date):
        errors.append(f"date must use YYYY-MM-DD, got `{args.date}`")
    else:
        try:
            date.fromisoformat(args.date)
        except ValueError:
            errors.append(f"date must be a valid calendar date, got `{args.date}`")
    try:
        parse_spec_id(args.spec_id)
    except ValueError as exc:
        errors.append(str(exc))

    board_root = Path(args.board_root).resolve()
    package = spec_package_path(board_root, args.spec_id)
    path_error = spec_package_path_error(package)
    if path_error:
        errors.append(path_error)
    if errors:
        print_errors(errors)
        return 1

    tasks_path = package / "tasks.md"
    manifest_path = package / "manifest.yaml"
    registry_path = spec_registry_path(board_root, args.spec_id)
    validate_module = load_local_module(__file__, "validate_execution_state.py")
    readiness_module = load_local_module(__file__, "validate_execution_readiness.py")
    try:
        recover_interrupted_transaction(package)
        readiness_errors = readiness_module.collect_errors(board_root, args.spec_id, args.task_id)
        if readiness_errors:
            print_errors(readiness_errors)
            return 1
        for path in (tasks_path, manifest_path, registry_path):
            if not path.is_file():
                raise FileNotFoundError(f"missing required execution-state input: {path}")
        evidence_errors = validate_module.validate_task_evidence(package, args.task_id, args.status)
        if evidence_errors:
            print_errors(evidence_errors)
            return 1

        manifest = load_yaml(manifest_path)
        registry = registry_for(board_root, args.spec_id)
        for key in ("spec_id", "cycle_id", "feature_key"):
            if manifest.get(key) != registry.get(key):
                raise ValueError(f"manifest `{key}` must match registry before execution-state sync")

        original_bytes = {
            tasks_path: tasks_path.read_bytes(),
            manifest_path: manifest_path.read_bytes(),
            registry_path: registry_path.read_bytes(),
        }
        tasks_content, task_states = render_tasks_text(
            original_bytes[tasks_path].decode("utf-8-sig"), args.task_id, args.status
        )
        all_done = bool(task_states) and all(task_states.values())
        if args.status == "blocked":
            spec_status, phase = "blocked", "execute"
        elif all_done:
            spec_status, phase = "done", "done"
        else:
            spec_status, phase = "in_progress", "execute"

        manifest_content = render_manifest_text(
            original_bytes[manifest_path].decode("utf-8-sig"),
            spec_status=spec_status,
            phase=phase,
            task_id=args.task_id,
            execution_date=args.date,
            summary=args.summary,
            files_changed=args.files_changed,
        )
        registry_content = render_registry_text(original_bytes[registry_path].decode("utf-8-sig"), spec_status)
        changes = {
            tasks_path: tasks_content,
            manifest_path: manifest_content,
            registry_path: registry_content,
        }
        candidate_errors = validate_candidate_snapshot(board_root, args.spec_id, changes, validate_module)
        if candidate_errors:
            print_errors(candidate_errors)
            return 1

        fail_after = os.environ.get("MAGIA_TEST_FAIL_AFTER_REPLACE")
        atomic_write_many(
            changes,
            package,
            fail_after_replace=int(fail_after) if fail_after else None,
            expected_originals=original_bytes,
        )
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print_errors([str(exc)])
        return 1

    print(f"OK: synced {args.task_id} ({args.status}); spec status is {spec_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
