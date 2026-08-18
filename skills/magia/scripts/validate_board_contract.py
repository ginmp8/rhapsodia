#!/usr/bin/env python3
"""Validate the self-contained board contract expected by MAGIA."""

from __future__ import annotations

import argparse
from pathlib import Path

from board_contract import validate_board
from magia_utils import print_errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate one canonical board root for MAGIA execution.")
    parser.add_argument("board_root", help="Canonical board root under docs/boards/<board_id>/<year>/cycles/<cycle_id>/.")
    args = parser.parse_args(argv)
    errors = validate_board(Path(args.board_root).resolve())
    if errors:
        print_errors(errors)
        return 1
    print("OK: board contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
