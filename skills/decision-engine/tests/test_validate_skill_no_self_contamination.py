#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cache = root / "scripts" / "__pycache__"
    shutil.rmtree(cache, ignore_errors=True)

    with tempfile.TemporaryDirectory() as td:
        report = Path(td) / "report.json"
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "validate_skill.py"), str(root), "--json-output", str(report)],
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(report.read_text(encoding="utf-8"))

    errors = []
    if result.returncode != 0:
        errors.append(f"validator returned {result.returncode}: {payload.get('errors')}")
    if cache.exists():
        errors.append("validator created scripts/__pycache__ inside the target")

    if errors:
        print("\n".join(errors))
        return 1
    print("validate_skill self-contamination regression: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
