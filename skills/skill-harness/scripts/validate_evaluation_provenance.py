#!/usr/bin/env python3
"""Validate an evaluation-provenance receipt inspired by SLSA provenance concepts."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
import re
from pathlib import Path
from typing import Any
from _harness_common import canonical_json_sha256, dump_json

SHA = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


def _identity(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and (bool(SHA.fullmatch(value)) or len(value.strip()) >= 3)


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["provenance must be a JSON object"]}
    allowed = {"provenance_version", "invocation_id", "harness_identity", "process_identity", "external_parameters", "resolved_dependencies", "identities", "subjects"}
    if set(data) - allowed:
        errors.append("provenance contains unknown top-level properties")
    if data.get("provenance_version") != 1:
        errors.append("provenance_version must be 1")
    for key in ("invocation_id", "harness_identity", "process_identity"):
        if not _identity(data.get(key)):
            errors.append(f"{key} must be a non-empty stable identity")
    if not isinstance(data.get("external_parameters"), dict):
        errors.append("external_parameters must be an object")
    deps = data.get("resolved_dependencies")
    if not isinstance(deps, list):
        errors.append("resolved_dependencies must be an array")
        deps = []
    seen_dep: set[str] = set()
    for i, row in enumerate(deps):
        if not isinstance(row, dict) or set(row) != {"name", "identity"}:
            errors.append(f"resolved_dependencies[{i}] must contain exactly name and identity")
            continue
        if not isinstance(row.get("name"), str) or not row.get("name", "").strip() or not _identity(row.get("identity")):
            errors.append(f"resolved_dependencies[{i}] has invalid name or identity")
        elif row["name"] in seen_dep:
            errors.append(f"duplicate dependency name: {row['name']}")
        else:
            seen_dep.add(row["name"])
    identities = data.get("identities")
    if not isinstance(identities, dict) or not identities:
        errors.append("identities must be a non-empty object")
    else:
        for key, value in identities.items():
            if not isinstance(key, str) or not key.strip() or not _identity(value):
                errors.append(f"identities.{key} must be a stable identity")
    subjects = data.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        errors.append("subjects must be a non-empty array")
        subjects = []
    seen_subject: set[str] = set()
    for i, row in enumerate(subjects):
        if not isinstance(row, dict) or set(row) != {"name", "sha256"}:
            errors.append(f"subjects[{i}] must contain exactly name and sha256")
            continue
        if not isinstance(row.get("name"), str) or not row.get("name", "").strip():
            errors.append(f"subjects[{i}].name must be non-empty")
        elif row["name"] in seen_subject:
            errors.append(f"duplicate subject name: {row['name']}")
        else:
            seen_subject.add(row["name"])
        if not isinstance(row.get("sha256"), str) or not SHA.fullmatch(row["sha256"]):
            errors.append(f"subjects[{i}].sha256 must be sha256:<64hex> or 64hex")
    return {"status": "pass" if not errors else "fail", "identity_sha256": canonical_json_sha256(data), "errors": errors, "subject_count": len(seen_subject), "dependency_count": len(seen_dep)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    try:
        report = validate(json.loads(Path(args.receipt).read_text(encoding="utf-8")))
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)]}
    dump_json(report, args.json_out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
