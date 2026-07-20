#!/usr/bin/env python3
"""Synchronize canonical MAGIA task, manifest, and registry execution state."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Callable, Iterator

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
    validate_iso_date,
    write_text,
    yaml_quote,
)

TASK_LINE_RE = re.compile(r"^(?P<prefix>\s*-\s*)\[(?P<mark>[ xX])\](?P<suffix>\s+(?P<task_id>task\d{3}):\s+.+)$")
VALID_SYNC_STATUSES = {"in_progress", "blocked", "done"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REPLACE_FILE = os.replace


def render_tasks_file(tasks_path: Path, task_id: str, status: str) -> tuple[str, dict[str, bool]]:
    original = tasks_path.read_text(encoding="utf-8-sig")
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
        raise ValueError(f"`{task_id}` not found in {tasks_path}")
    content = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
    return content, task_states


def update_tasks_file(tasks_path: Path, task_id: str, status: str) -> dict[str, bool]:
    content, task_states = render_tasks_file(tasks_path, task_id, status)
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


def render_manifest_file(
    manifest_path: Path,
    *,
    spec_status: str,
    phase: str,
    task_id: str,
    execution_date: str,
    summary: str | None,
    files_changed: list[str],
) -> str:
    original = manifest_path.read_text(encoding="utf-8-sig")
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
    write_text(
        manifest_path,
        render_manifest_file(
            manifest_path,
            spec_status=spec_status,
            phase=phase,
            task_id=task_id,
            execution_date=execution_date,
            summary=summary,
            files_changed=files_changed,
        ),
    )


def render_registry_file(registry_path: Path, spec_status: str) -> str:
    original = registry_path.read_text(encoding="utf-8-sig")
    lines = original.splitlines()
    replace_top_level_scalar(lines, "status", spec_status)
    return "\n".join(lines) + ("\n" if original.endswith("\n") else "")


def update_registry_file(registry_path: Path, spec_status: str) -> None:
    write_text(registry_path, render_registry_file(registry_path, spec_status))


@contextmanager
def execution_state_lock(board_root: Path, spec_id: str) -> Iterator[None]:
    """Serialize state transitions for one canonical spec without adding board artifacts."""
    try:
        import fcntl
    except ImportError as exc:  # pragma: no cover - MAGIA package validation runs on POSIX
        raise RuntimeError("execution-state locking requires POSIX fcntl support") from exc

    lock_root = Path(tempfile.gettempdir()) / "magia-execution-state-locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    identity = f"{board_root.resolve()}::{spec_id}".encode("utf-8")
    lock_path = lock_root / f"{hashlib.sha256(identity).hexdigest()}.lock"
    with lock_path.open("a+b") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _stage_bytes(target: Path, content: bytes) -> Path:
    fd, raw_path = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".magia-tmp", dir=target.parent)
    staged = Path(raw_path)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(staged, target.stat().st_mode)
        return staged
    except BaseException:
        staged.unlink(missing_ok=True)
        raise


def commit_file_set(
    changes: dict[Path, str],
    *,
    validate_after_commit: Callable[[], list[str]] | None = None,
    replace_func: Callable[[str | bytes | os.PathLike[str] | os.PathLike[bytes], str | bytes | os.PathLike[str] | os.PathLike[bytes]], None] | None = None,
) -> None:
    """Stage all files, replace them as a set, and restore originals on any failure."""
    replacer = replace_func or REPLACE_FILE
    originals = {path: path.read_bytes() for path in changes}
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    rollback_errors: list[str] = []
    try:
        for path, content in changes.items():
            staged[path] = _stage_bytes(path, content.encode("utf-8"))
        for path, staged_path in staged.items():
            replacer(staged_path, path)
            replaced.append(path)
        if validate_after_commit is not None:
            errors = validate_after_commit()
            if errors:
                raise ValueError("post-commit execution-state validation failed: " + "; ".join(errors))
    except BaseException as exc:
        for path in reversed(replaced):
            try:
                rollback_path = _stage_bytes(path, originals[path])
                try:
                    replacer(rollback_path, path)
                finally:
                    rollback_path.unlink(missing_ok=True)
            except BaseException as rollback_exc:  # noqa: BLE001
                rollback_errors.append(f"{path}: {rollback_exc}")
        if rollback_errors:
            raise RuntimeError(
                "execution-state transaction failed and rollback was incomplete: " + "; ".join(rollback_errors)
            ) from exc
        raise
    finally:
        for staged_path in staged.values():
            staged_path.unlink(missing_ok=True)


def prospective_evidence_errors(
    package: Path,
    task_states: dict[str, bool],
    task_id: str,
    status: str,
    validator_module,
) -> list[str]:
    """Reject a state transition unless current execution records already prove it."""
    notes_path = package / "implementation-notes.md"
    validation_path = package / "validation-evidence.md"
    missing = [path for path in (notes_path, validation_path) if not path.is_file()]
    if missing:
        return [f"missing required execution evidence: {path}" for path in missing]

    notes_status = validator_module.parse_notes(notes_path)
    validation_runs = validator_module.parse_validation(validation_path)
    errors: list[str] = []

    recorded_status = notes_status.get(task_id)
    if recorded_status != status:
        errors.append(
            f"implementation-notes.md must record `{task_id}` as `{status}` before execution-state sync; "
            f"found `{recorded_status or 'missing'}`"
        )
    if task_id not in validation_runs:
        errors.append(f"validation-evidence.md has no `Execution Run - {task_id}` section")

    for recorded_task, recorded_task_status in notes_status.items():
        if recorded_task not in task_states:
            errors.append(f"execution log references missing task id `{recorded_task}`")
        if recorded_task_status in VALID_SYNC_STATUSES and recorded_task not in validation_runs:
            errors.append(
                f"implementation-notes.md records `{recorded_task}` as `{recorded_task_status}` but "
                f"validation-evidence.md has no `Execution Run - {recorded_task}` section"
            )

    for current_task, is_done in task_states.items():
        recorded_task_status = notes_status.get(current_task)
        if is_done and recorded_task_status != "done":
            errors.append(
                f"prospective tasks.md marks `{current_task}` done but implementation-notes.md status is "
                f"`{recorded_task_status or 'missing'}` instead of done"
            )
        if is_done and current_task not in validation_runs:
            errors.append(
                f"prospective tasks.md marks `{current_task}` done but validation-evidence.md has no "
                f"`Execution Run - {current_task}` section"
            )
        if not is_done and recorded_task_status == "done":
            errors.append(
                f"implementation-notes.md marks `{current_task}` done but prospective tasks.md leaves the checkbox unchecked"
            )
    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize canonical MAGIA execution state from truthful task evidence.")
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
            validate_iso_date(args.date)
        except ValueError as exc:
            errors.append(str(exc))
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
    validator_module = load_local_module(__file__, "validate_execution_state.py")

    try:
        with execution_state_lock(board_root, args.spec_id):
            for path in (tasks_path, manifest_path, registry_path):
                if not path.is_file():
                    raise FileNotFoundError(f"missing required execution-state input: {path}")
            manifest = load_yaml(manifest_path)
            registry = registry_for(board_root, args.spec_id)
            for key in ("spec_id", "cycle_id", "feature_key"):
                if manifest.get(key) != registry.get(key):
                    raise ValueError(f"manifest `{key}` must match registry before execution-state sync")

            tasks_content, task_states = render_tasks_file(tasks_path, args.task_id, args.status)
            evidence_errors = prospective_evidence_errors(
                package,
                task_states,
                args.task_id,
                args.status,
                validator_module,
            )
            if evidence_errors:
                raise ValueError("; ".join(evidence_errors))

            all_done = bool(task_states) and all(task_states.values())
            if args.status == "blocked":
                spec_status, phase = "blocked", "execute"
            elif all_done:
                spec_status, phase = "done", "done"
            else:
                spec_status, phase = "in_progress", "execute"

            manifest_content = render_manifest_file(
                manifest_path,
                spec_status=spec_status,
                phase=phase,
                task_id=args.task_id,
                execution_date=args.date,
                summary=args.summary,
                files_changed=args.files_changed,
            )
            registry_content = render_registry_file(registry_path, spec_status)
            commit_file_set(
                {
                    tasks_path: tasks_content,
                    manifest_path: manifest_content,
                    registry_path: registry_content,
                },
                validate_after_commit=lambda: validator_module.collect_errors(package),
            )
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print_errors([str(exc)])
        return 1

    print(f"OK: synced {args.task_id} ({args.status}); spec status is {spec_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
