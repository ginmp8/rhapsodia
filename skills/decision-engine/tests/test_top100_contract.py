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


def error_codes(payload: dict) -> set[str]:
    return {item.get("code") for item in payload.get("errors", [])}


def copy_candidate(root: Path, work: Path, name: str) -> Path:
    candidate = work / name / "decision-engine"
    shutil.copytree(root, candidate, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    return candidate


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = []
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)

        too_long = copy_candidate(root, work, "too-long")
        skill = too_long / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + ("\n<!-- padding -->" * 40) + "\n", encoding="utf-8")
        code, payload = run_validator(too_long, work / "too-long.json")
        if code == 0 or "SK080" not in error_codes(payload):
            failures.append("validator did not reject a SKILL.md beyond 100 physical lines")

        no_preview = copy_candidate(root, work, "no-preview")
        examples = no_preview / "examples" / "examples.md"
        text = examples.read_text(encoding="utf-8").replace("## At a Glance\n", "## Preview\n", 1)
        examples.write_text(text, encoding="utf-8")
        code, payload = run_validator(no_preview, work / "no-preview.json")
        if code == 0 or "SK083" not in error_codes(payload):
            failures.append("validator did not reject long Markdown without preview-first structure")

        vague_preview = copy_candidate(root, work, "vague-preview")
        examples = vague_preview / "examples" / "examples.md"
        text = examples.read_text(encoding="utf-8")
        purpose_line = next(line for line in text.splitlines() if line.startswith("- **Purpose:**"))
        text = text.replace(purpose_line, "- **Purpose:** Primary topics: Binary, Choice, Score, escalation.", 1)
        examples.write_text(text, encoding="utf-8")
        code, payload = run_validator(vague_preview, work / "vague-preview.json")
        if code == 0 or "SK084" not in error_codes(payload):
            failures.append("validator did not reject a vague semantic preview")

        stale_contents = copy_candidate(root, work, "stale-contents")
        examples = stale_contents / "examples" / "examples.md"
        text = examples.read_text(encoding="utf-8").replace("- Escalation\n", "", 1)
        examples.write_text(text, encoding="utf-8")
        code, payload = run_validator(stale_contents, work / "stale-contents.json")
        if code == 0 or "SK085" not in error_codes(payload):
            failures.append("validator did not reject Contents/heading drift")

        missing_critical = copy_candidate(root, work, "missing-critical")
        skill = missing_critical / "SKILL.md"
        text = skill.read_text(encoding="utf-8").replace(
            "option order alone must not determine the winner",
            "ordering details live only in a supporting reference",
            1,
        )
        skill.write_text(text, encoding="utf-8")
        code, payload = run_validator(missing_critical, work / "missing-critical.json")
        if code == 0 or "SK086" not in error_codes(payload):
            failures.append("validator did not reject loss/displacement of decision-critical Top-100 knowledge")

    if failures:
        print("\n".join(failures))
        return 1
    print("Top-100, semantic-preview, navigation, and critical-knowledge regression: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
