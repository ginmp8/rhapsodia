#!/usr/bin/env python3
"""Report canonical skill-improver run status from existing evidence.

This helper does not maintain a second session state. It derives status from the
runner's .skill-improver/runs.jsonl, stop file, and report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Report canonical skill-improver run status.")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="Target or repository path used to resolve the state directory.")
    parser.add_argument("--state-dir", type=Path, default=Path(".skill-improver"))
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()

    base = args.target.resolve()
    if base.is_file():
        base = base.parent
    state_dir = args.state_dir if args.state_dir.is_absolute() else (base / args.state_dir).resolve()
    stop_file = args.stop_file if args.stop_file and args.stop_file.is_absolute() else ((base / args.stop_file).resolve() if args.stop_file else state_dir / "stop")
    report_path = args.report_path if args.report_path and args.report_path.is_absolute() else ((base / args.report_path).resolve() if args.report_path else state_dir / "improvement-report.md")
    log_path = state_dir / "runs.jsonl"
    rows = load_jsonl(log_path)

    accepted = sum(1 for row in rows if row.get("accepted") is True)
    rejected = sum(1 for row in rows if row.get("accepted") is False)
    last = rows[-1] if rows else None

    if stop_file.exists():
        status = "cancellation-requested"
    elif report_path.exists() and accepted:
        status = "accepted"
    elif report_path.exists():
        status = "completed-without-accepted-candidate"
    elif rows:
        status = "interrupted-or-running"
    else:
        status = "not-started"

    payload = {
        "status": status,
        "target": str(base),
        "state_dir": str(state_dir),
        "iterations_recorded": len(rows),
        "accepted": accepted,
        "rejected": rejected,
        "last_iteration": None if last is None else last.get("iteration"),
        "last_decision": None if last is None else {
            "hypothesis_id": last.get("hypothesis_id"),
            "accepted": last.get("accepted"),
            "reason": last.get("reason"),
            "change_gate_status": last.get("change_gate_status"),
        },
        "stop_file": str(stop_file),
        "stop_requested": stop_file.exists(),
        "report_path": str(report_path),
        "report_exists": report_path.exists(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
