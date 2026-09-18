from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from test_board_contract import build_board  # noqa: E402


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_clean_state_projection_is_read_only(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    summary = load_script("summarize_execution_state.py")
    before = (root / "specs" / spec_id / "manifest.yaml").read_bytes()
    payload = summary.summarize(root, spec_id)
    assert payload["projection"] == "non_authoritative"
    assert payload["recovery"]["safe_to_mutate"] is True
    assert payload["tasks"][0]["task_id"] == "task001"
    assert (root / "specs" / spec_id / "manifest.yaml").read_bytes() == before


def test_live_lock_blocks_mutation(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / ".magia-state.lock").write_text(f"pid={os.getpid()}\n", encoding="utf-8")
    payload = load_script("summarize_execution_state.py").summarize(root, spec_id)
    assert payload["recovery"]["lock"] == "live_owner"
    assert payload["recovery"]["recovery_action"] == "wait_for_owner"
    assert payload["recovery"]["safe_to_mutate"] is False


def test_dead_lock_requests_existing_recovery_path(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / ".magia-state.lock").write_text("pid=99999999\n", encoding="utf-8")
    payload = load_script("summarize_execution_state.py").summarize(root, spec_id)
    assert payload["recovery"]["lock"] == "dead_owner"
    assert payload["recovery"]["recovery_action"] == "run_recovery"


def test_valid_prepared_journal_lists_targets_without_recovery(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    journal = package / ".magia-state-transaction"
    journal.mkdir()
    (journal / "backup-0.bin").write_bytes((package / "tasks.md").read_bytes())
    (journal / "transaction.json").write_text(
        json.dumps({"state": "prepared", "entries": [{"target": f"specs/{spec_id}/tasks.md", "backup": "backup-0.bin"}]}),
        encoding="utf-8",
    )
    payload = load_script("summarize_execution_state.py").summarize(root, spec_id)
    assert payload["recovery"]["journal"] == "prepared"
    assert payload["recovery"]["journal_targets"] == [f"specs/{spec_id}/tasks.md"]
    assert (journal / "transaction.json").is_file()


def test_malformed_journal_requires_manual_inspection(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    journal = root / "specs" / spec_id / ".magia-state-transaction"
    journal.mkdir()
    (journal / "transaction.json").write_text("{}", encoding="utf-8")
    payload = load_script("summarize_execution_state.py").summarize(root, spec_id)
    assert payload["recovery"]["journal"] == "invalid"
    assert payload["recovery"]["recovery_action"] == "manual_inspection"
    assert payload["recovery"]["safe_to_mutate"] is False
