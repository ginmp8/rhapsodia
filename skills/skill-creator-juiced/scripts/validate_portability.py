#!/usr/bin/env python3
"""Validate an Agent Skills package against the portable core or OpenAI adapter profile."""
from __future__ import annotations

import argparse
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path

from skill_spec import validate_agent_skill


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills portability constraints.")
    parser.add_argument("target", help="Path to a skill directory")
    parser.add_argument("--profile", choices=["portable", "openai"], default="portable")
    parser.add_argument("--json", dest="json_path", help="Optional JSON output path")
    args = parser.parse_args()

    report = validate_agent_skill(Path(args.target).resolve(), args.profile)
    if args.json_path:
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
