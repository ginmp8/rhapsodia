#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as td:
        candidate = Path(td) / "decision-engine"
        shutil.copytree(root, candidate, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        example = candidate / "examples" / "examples.md"
        injected = "Q" + "ual " + "op" + chr(0xE7) + chr(0xE3) + "o " + "de" + "ve rodar " + "ago" + "ra?"
        example.write_text(example.read_text(encoding="utf-8") + "\n" + injected + "\n", encoding="utf-8")
        report = Path(td) / "report.json"
        result = subprocess.run(
            [sys.executable, str(candidate / "scripts" / "validate_skill.py"), str(candidate), "--json-output", str(report)],
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        payload = json.loads(report.read_text(encoding="utf-8"))

    codes = {item.get("code") for item in payload.get("errors", [])}
    if result.returncode == 0 or "SK012" not in codes:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1
    print("English-only regression gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
