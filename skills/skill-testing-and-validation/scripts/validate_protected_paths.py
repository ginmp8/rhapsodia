#!/usr/bin/env python3
"""Detect changes to fixtures, snapshots, expected outputs, golden files, and benchmark evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROTECTED_COMPONENTS = {
    ".git",
    "fixtures",
    "fixture",
    "snapshots",
    "snapshot",
    "expected",
    "expected-output",
    "expected-outputs",
    "expected_output",
    "expected_outputs",
    "golden",
    "goldens",
    "benchmark-evidence",
    "benchmark_evidence",
}
PROTECTED_NAME_PREFIXES = ("expected_", "golden_", "snapshot_")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_files(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            result[rel] = sha256(path)
    return result


def is_protected(rel: str) -> bool:
    parts = tuple(part.lower() for part in Path(rel).parts)
    if any(part in PROTECTED_COMPONENTS for part in parts):
        return True
    name = Path(rel).name.lower()
    return name.startswith(PROTECTED_NAME_PREFIXES) or ".golden." in name or ".snapshot." in name


def validate(baseline: Path, candidate: Path, allow: set[str]) -> dict[str, Any]:
    baseline = baseline.resolve()
    candidate = candidate.resolve()
    before = rel_files(baseline)
    after = rel_files(candidate)
    diagnostics: list[dict[str, Any]] = []
    for rel in sorted(set(before) | set(after)):
        if not is_protected(rel) or rel in allow:
            continue
        if rel not in before:
            diagnostics.append({"code": "protected/added", "path": rel, "evidence": {"candidate_sha256": after[rel]}})
        elif rel not in after:
            diagnostics.append({"code": "protected/deleted", "path": rel, "evidence": {"baseline_sha256": before[rel]}})
        elif before[rel] != after[rel]:
            diagnostics.append({"code": "protected/modified", "path": rel, "evidence": {"baseline_sha256": before[rel], "candidate_sha256": after[rel]}})
    return {
        "receipt_version": 1,
        "status": "pass" if not diagnostics else "fail",
        "baseline": str(baseline),
        "candidate": str(candidate),
        "protected_policy": {"components": sorted(PROTECTED_COMPONENTS), "name_prefixes": list(PROTECTED_NAME_PREFIXES), "allowed": sorted(allow)},
        "diagnostics": diagnostics,
        "errors": len(diagnostics),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect unauthorized changes to protected test/evaluation evidence.")
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--allow", action="append", default=[], help="Explicitly allowed relative protected path; repeatable")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()
    result = validate(Path(args.baseline), Path(args.candidate), set(args.allow))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PROTECTED PATHS: {result['status'].upper()} errors={result['errors']}")
        for item in result["diagnostics"]:
            print(f"- {item['code']} {item['path']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
