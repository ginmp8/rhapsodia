#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_validator(candidate: Path, report: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(candidate / "scripts" / "validate_skill.py"), str(candidate), "--json-output", str(report)],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return result.returncode, json.loads(report.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = []
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)

        too_long = work / "too-long" / "decision-engine"
        shutil.copytree(root, too_long, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        skill = too_long / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + ("\n<!-- padding -->" * 40) + "\n", encoding="utf-8")
        code, payload = run_validator(too_long, work / "too-long.json")
        codes = {item.get("code") for item in payload.get("errors", [])}
        if code == 0 or "SK080" not in codes:
            failures.append("validator did not reject a SKILL.md beyond 100 physical lines")

        no_preview = work / "no-preview" / "decision-engine"
        shutil.copytree(root, no_preview, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        examples = no_preview / "examples" / "examples.md"
        text = examples.read_text(encoding="utf-8")
        text = text.replace("## At a Glance\n", "## Preview\n", 1)
        examples.write_text(text, encoding="utf-8")
        code, payload = run_validator(no_preview, work / "no-preview.json")
        codes = {item.get("code") for item in payload.get("errors", [])}
        if code == 0 or "SK083" not in codes:
            failures.append("validator did not reject long Markdown without preview-first structure")

    if failures:
        print("\n".join(failures))
        return 1
    print("Top-100 and long-Markdown preview regression: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
