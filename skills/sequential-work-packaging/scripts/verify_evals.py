#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _swp_common import sha256_file  # noqa: E402


def verify(root: Path) -> dict:
    evals_root = root / "evals"
    manifest_paths = sorted(evals_root.glob("frozen-manifest*.json"))
    errors = []
    manifests = []
    if not manifest_paths:
        errors.append({"code": "FROZEN_MANIFEST_MISSING", "path": "evals/frozen-manifest.json"})
    for manifest_path in manifest_paths:
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append({"code": "FROZEN_MANIFEST_INVALID", "path": manifest_path.relative_to(root).as_posix(), "error": str(exc)})
            continue
        manifests.append({
            "path": manifest_path.relative_to(root).as_posix(),
            "manifest_version": data.get("manifest_version"),
        })
        for item in data.get("files", []):
            path = root / item["path"]
            if not path.is_file():
                errors.append({"code": "FROZEN_EVAL_MISSING", "manifest": manifest_path.relative_to(root).as_posix(), "path": item["path"]})
                continue
            actual = sha256_file(path)
            if actual != item["sha256"]:
                errors.append({
                    "code": "FROZEN_EVAL_CHANGED",
                    "manifest": manifest_path.relative_to(root).as_posix(),
                    "path": item["path"],
                    "expected": item["sha256"],
                    "actual": actual,
                })
    base_version = None
    for item in manifests:
        if item["path"] == "evals/frozen-manifest.json":
            base_version = item["manifest_version"]
            break
    return {
        "status": "fail" if errors else "pass",
        "manifest_version": base_version,
        "manifests": manifests,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = verify(root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
