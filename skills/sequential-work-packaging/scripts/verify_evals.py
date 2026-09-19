#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _swp_common import sha256_file  # noqa: E402


def verify(root: Path) -> dict:
    manifest_path = root / "evals" / "frozen-manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    for item in data.get("files", []):
        path = root / item["path"]
        if not path.is_file():
            errors.append({"code": "FROZEN_EVAL_MISSING", "path": item["path"]})
            continue
        actual = sha256_file(path)
        if actual != item["sha256"]:
            errors.append({"code": "FROZEN_EVAL_CHANGED", "path": item["path"], "expected": item["sha256"], "actual": actual})
    return {"status": "fail" if errors else "pass", "manifest_version": data.get("manifest_version"), "errors": errors}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = verify(root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
