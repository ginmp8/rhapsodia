#!/usr/bin/env python3
"""Minimal portable evaluator example for --evaluator command."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.target.resolve()
    score = 0
    if (root / "SKILL.md").is_file():
        score += 30
    if (root / "references").is_dir():
        score += 20
    if (root / "scripts").is_dir():
        score += 20
    text = (root / "SKILL.md").read_text(encoding="utf-8", errors="replace") if (root / "SKILL.md").is_file() else ""
    if any(word in text.lower() for word in ("validation", "gate", "benchmark", "test")):
        score += 30
    status = "pass" if (root / "SKILL.md").is_file() else "fail"
    print(json.dumps({"score": score, "status": status, "gates": {"skill_md": status}}))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
