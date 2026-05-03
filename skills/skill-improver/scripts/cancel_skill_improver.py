#!/usr/bin/env python3
"""Request graceful cancellation for a running skill-improver loop.

The loop exits before the next candidate iteration when it sees the stop file.
Accepted target changes are preserved; rejected candidates remain reverted by the
runner's normal accept/reject logic.
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path


def git_root_for(target: Path | None) -> Path:
    cwd = (target or Path.cwd()).resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        ).stdout.strip()
    except Exception:
        return cwd if cwd.is_dir() else cwd.parent
    return Path(out).resolve()


def resolve_stop_file(args: argparse.Namespace) -> Path:
    root = git_root_for(args.target)
    if args.stop_file:
        return args.stop_file if args.stop_file.is_absolute() else (root / args.stop_file).resolve()
    state_dir = args.state_dir if args.state_dir.is_absolute() else (root / args.state_dir).resolve()
    return state_dir / "stop"


def main() -> int:
    parser = argparse.ArgumentParser(description="Request graceful cancellation for skill_improver_loop.py.")
    parser.add_argument("--target", type=Path, help="Target skill or repository path used to resolve the git root.")
    parser.add_argument("--state-dir", type=Path, default=Path(".skill-improver"), help="State directory used by the loop when --stop-file is omitted.")
    parser.add_argument("--stop-file", type=Path, help="Exact stop-file path configured on the running loop.")
    parser.add_argument("--reason", default="cancel requested", help="Human-readable cancellation reason written to the stop file.")
    args = parser.parse_args()

    stop_file = resolve_stop_file(args)
    stop_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    stop_file.write_text(f"{timestamp} - {args.reason}\n", encoding="utf-8")
    print(f"wrote stop request: {stop_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
