#!/usr/bin/env python3
"""Canonical MAGIA closure path for syncing and validating execution state."""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

from magia_utils import BOARD_ROOT_TEMPLATE, load_local_module, print_errors, spec_package_path, spec_package_path_error



def _run_module_main(module, argv: list[str]) -> tuple[int, list[str]]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        rc = module.main(argv)
    return rc, [line for line in output.getvalue().splitlines() if line.strip()]



def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize MAGIA task state and validate cross-artifact execution records in one closure step."
    )
    parser.add_argument("board_root", help=f"Path to the active BOARD_ROOT under {BOARD_ROOT_TEMPLATE}.")
    parser.add_argument("--spec-id", required=True, help="Selected spec id in the form specNNN.")
    parser.add_argument("--task-id", required=True, help="Executed task id in the form taskNNN.")
    parser.add_argument(
        "--status",
        required=True,
        choices=["in_progress", "blocked", "done"],
        help="Truthful task execution status for this closure pass.",
    )
    parser.add_argument("--date", help="Execution date in YYYY-MM-DD format.")
    parser.add_argument("--summary", help="Short truthful execution summary for manifest.yaml last_execution.")
    parser.add_argument(
        "--files-changed",
        nargs="*",
        default=[],
        help="Repository-relative POSIX paths changed by the executed task.",
    )
    args = parser.parse_args(argv)

    board_root = Path(args.board_root).resolve()
    spec_package = spec_package_path(board_root, args.spec_id)
    canonical_error = spec_package_path_error(spec_package)
    if canonical_error:
        print_errors([canonical_error])
        return 1

    sync_module = load_local_module(__file__, "sync_execution_state.py")
    heal_module = load_local_module(__file__, "heal_execution_state.py")
    validate_module = load_local_module(__file__, "validate_execution_state.py")

    sync_args = [str(board_root), "--spec-id", args.spec_id, "--task-id", args.task_id, "--status", args.status]
    if args.date:
        sync_args.extend(["--date", args.date])
    if args.summary:
        sync_args.extend(["--summary", args.summary])
    if args.files_changed:
        sync_args.extend(["--files-changed", *args.files_changed])

    sync_rc, sync_output = _run_module_main(sync_module, sync_args)
    if sync_rc != 0:
        print("\n".join(sync_output))
        return sync_rc

    validate_rc, validate_output = _run_module_main(validate_module, [str(board_root), "--spec-id", args.spec_id])
    if validate_rc != 0:
        heal_rc, heal_output = _run_module_main(heal_module, [str(board_root), "--spec-id", args.spec_id])
        if heal_rc != 0:
            print("\n".join(heal_output or validate_output))
            return validate_rc
        validate_rc, validate_output = _run_module_main(validate_module, [str(board_root), "--spec-id", args.spec_id])
        if validate_rc != 0:
            print("\n".join(validate_output))
            return validate_rc

    print(f"OK: closed {args.task_id} ({args.status})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
