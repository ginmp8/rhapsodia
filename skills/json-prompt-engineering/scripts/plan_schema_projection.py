#!/usr/bin/env python3
"""Plan canonical JSON Schema projection against a provider capability profile.

The script reports potentially unsupported keyword paths and provider object-rule
mismatches. It never mutates or weakens the canonical schema.
"""
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

_HELPERS = runpy.run_path(str(Path(__file__).with_name("validate_json_artifact.py")))
load_json = _HELPERS["load_json"]
validate_provider_profile = _HELPERS["validate_provider_profile"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        schema = load_json(Path(args.schema).resolve())
        profile = load_json(Path(args.profile).resolve())
        provider_status, findings, warnings = validate_provider_profile(schema, profile)
        unsupported = [item for item in findings if item.get("code") == "provider/unsupported-keyword"]
        obligations = [
            {
                "path": item["path"],
                "keyword": item.get("keyword"),
                "obligation": "Preserve this canonical constraint in application-side validation or explicitly accept the semantic trade-off."
            }
            for item in unsupported
        ]
        report = {
            "status": "pass",
            "compatibility": "compatible" if provider_status == "pass" else "projection-required",
            "lossy": bool(unsupported),
            "canonical_schema": str(Path(args.schema).resolve()),
            "provider_profile": profile.get("id", str(Path(args.profile).resolve())),
            "profile_verified_at": profile.get("verified_at"),
            "provider_findings": findings,
            "application_side_constraints": obligations,
            "warnings": warnings,
            "note": "This is a projection plan, not proof of provider runtime acceptance or semantic equivalence."
        }
    except Exception as exc:
        report = {"status": "fail", "error": str(exc)}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json_output:
        Path(args.json_output).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
