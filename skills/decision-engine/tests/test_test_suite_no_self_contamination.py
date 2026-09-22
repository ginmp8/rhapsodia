#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cache = root / "scripts" / "__pycache__"
    shutil.rmtree(cache, ignore_errors=True)

    result = subprocess.run(
        [sys.executable, str(root / "tests" / "test_decision_contract.py")],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    errors = []
    if result.returncode != 0:
        errors.append(f"contract tests returned {result.returncode}: {result.stdout}{result.stderr}")
    if cache.exists():
        errors.append("contract tests created scripts/__pycache__ inside the target")

    if errors:
        print("\n".join(errors))
        return 1
    print("contract test self-contamination regression: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
