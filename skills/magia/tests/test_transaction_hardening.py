from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from test_board_contract import build_board  # noqa: E402
from test_execution_flow import write_execution_evidence  # noqa: E402


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_recovery_rejects_target_traversal_without_touching_external_file(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("ORIGINAL\n", encoding="utf-8")

    transaction = package / ".magia-state-transaction"
    transaction.mkdir()
    (transaction / "backup-0.bin").write_text("OVERWRITTEN\n", encoding="utf-8")
    relative_escape = os.path.relpath(sentinel, root).replace(os.sep, "/")
    (transaction / "transaction.json").write_text(
        json.dumps(
            {
                "state": "prepared",
                "entries": [{"target": relative_escape, "backup": "backup-0.bin"}],
            }
        ),
        encoding="utf-8",
    )

    sync = load_script("sync_execution_state.py")
    try:
        sync.recover_interrupted_transaction(package)
    except RuntimeError as exc:
        assert "target" in str(exc).lower()
    else:
        raise AssertionError("malicious transaction journal was accepted")

    assert sentinel.read_text(encoding="utf-8") == "ORIGINAL\n"


def test_recovery_rejects_backup_traversal(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    tasks = package / "tasks.md"
    original = tasks.read_bytes()
    external_backup = tmp_path / "external-backup.bin"
    external_backup.write_text("MALICIOUS\n", encoding="utf-8")

    transaction = package / ".magia-state-transaction"
    transaction.mkdir()
    relative = tasks.relative_to(root).as_posix()
    backup_escape = os.path.relpath(external_backup, transaction).replace(os.sep, "/")
    (transaction / "transaction.json").write_text(
        json.dumps(
            {
                "state": "prepared",
                "entries": [{"target": relative, "backup": backup_escape}],
            }
        ),
        encoding="utf-8",
    )

    sync = load_script("sync_execution_state.py")
    try:
        sync.recover_interrupted_transaction(package)
    except RuntimeError as exc:
        assert "backup" in str(exc).lower()
    else:
        raise AssertionError("external transaction backup was accepted")

    assert tasks.read_bytes() == original


def test_stale_lock_without_journal_is_recovered(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    lock = package / ".magia-state.lock"
    lock.write_text("pid=99999999\n", encoding="utf-8")

    sync = load_script("sync_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 0
    assert not lock.exists()


def test_live_lock_is_not_stolen(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    write_execution_evidence(package, "task001", "done")
    lock = package / ".magia-state.lock"
    lock.write_text(f"pid={os.getpid()}\n", encoding="utf-8")

    sync = load_script("sync_execution_state.py")
    assert sync.main([str(root), "--spec-id", spec_id, "--task-id", "task001", "--status", "done"]) == 1
    assert lock.exists()


def test_dead_owner_incomplete_prejournal_transaction_is_cleaned(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    transaction = package / ".magia-state-transaction"
    transaction.mkdir()
    (transaction / "backup-0.bin").write_text("unused", encoding="utf-8")
    lock = package / ".magia-state.lock"
    lock.write_text("pid=99999999\n", encoding="utf-8")

    sync = load_script("sync_execution_state.py")
    assert sync.recover_interrupted_transaction(package) is True
    assert not transaction.exists()
    assert not lock.exists()


def test_transaction_rejects_source_drift_after_preflight(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    tasks = package / "tasks.md"
    original = tasks.read_bytes()
    expected = {tasks: original}
    tasks.write_text("concurrent change\n", encoding="utf-8")

    sync = load_script("sync_execution_state.py")
    try:
        sync.atomic_write_many(
            {tasks: "candidate change\n"},
            package,
            expected_originals=expected,
        )
    except RuntimeError as exc:
        assert "changed after preflight" in str(exc)
    else:
        raise AssertionError("source drift was not detected")

    assert tasks.read_text(encoding="utf-8") == "concurrent change\n"
    assert not (package / ".magia-state.lock").exists()


def test_live_owner_prepared_transaction_is_not_recovered(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    tasks = package / "tasks.md"
    original = tasks.read_bytes()
    transaction = package / ".magia-state-transaction"
    transaction.mkdir()
    (transaction / "backup-0.bin").write_bytes(original)
    relative = tasks.relative_to(root).as_posix()
    (transaction / "transaction.json").write_text(
        json.dumps(
            {
                "state": "prepared",
                "entries": [{"target": relative, "backup": "backup-0.bin"}],
            }
        ),
        encoding="utf-8",
    )
    tasks.write_text("active owner state\n", encoding="utf-8")
    (package / ".magia-state.lock").write_text(f"pid={os.getpid()}\n", encoding="utf-8")

    sync = load_script("sync_execution_state.py")
    try:
        sync.recover_interrupted_transaction(package)
    except RuntimeError as exc:
        assert "live process" in str(exc)
    else:
        raise AssertionError("live transaction was recovered by another execution")

    assert tasks.read_text(encoding="utf-8") == "active owner state\n"
    assert transaction.exists()
    assert (package / ".magia-state.lock").exists()


def test_invalid_lock_metadata_fails_closed(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    lock = package / ".magia-state.lock"
    lock.write_text("unparseable lock\n", encoding="utf-8")

    sync = load_script("sync_execution_state.py")
    try:
        sync.recover_interrupted_transaction(package)
    except RuntimeError as exc:
        assert "metadata is invalid" in str(exc)
    else:
        raise AssertionError("invalid lock metadata was removed without proof of stale ownership")

    assert lock.exists()


def test_recovery_rejects_symlinked_authorized_target(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    tasks = package / "tasks.md"
    external = tmp_path / "external.txt"
    external.write_text("EXTERNAL\n", encoding="utf-8")
    tasks.unlink()
    tasks.symlink_to(external)

    transaction = package / ".magia-state-transaction"
    transaction.mkdir()
    (transaction / "backup-0.bin").write_text("MALICIOUS\n", encoding="utf-8")
    relative = tasks.relative_to(root).as_posix()
    (transaction / "transaction.json").write_text(
        json.dumps(
            {
                "state": "prepared",
                "entries": [{"target": relative, "backup": "backup-0.bin"}],
            }
        ),
        encoding="utf-8",
    )

    sync = load_script("sync_execution_state.py")
    try:
        sync.recover_interrupted_transaction(package)
    except RuntimeError as exc:
        assert "symlink" in str(exc).lower()
    else:
        raise AssertionError("symlinked transaction target was accepted")

    assert external.read_text(encoding="utf-8") == "EXTERNAL\n"
