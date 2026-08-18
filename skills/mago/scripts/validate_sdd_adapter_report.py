#!/usr/bin/env python3
"""Validate disclosure completeness for generated Mago SDD adapter reports."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

FORMATS = {"mago", "spec-kit", "kiro", "openspec"}
REQUIRED_LISTS = {"generated_files", "mapped_fields", "omitted_fields", "lossy_mappings", "unsupported_target_concepts", "source_only_concepts", "validation"}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report")
    ap.add_argument("--json-output")
    args = ap.parse_args()
    path = Path(args.report)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if data.get("kind") != "mago-sdd-adapter-report": errors.append("invalid kind")
    if data.get("authoritative") is not False: errors.append("adapter report must be non-authoritative")
    if data.get("direction") not in {"import", "export", "round-trip"}: errors.append("invalid direction")
    for side in ("source", "target"):
        obj = data.get(side)
        if not isinstance(obj, dict) or obj.get("format") not in FORMATS or not obj.get("version"):
            errors.append(f"invalid {side} descriptor")
    for field in REQUIRED_LISTS:
        if not isinstance(data.get(field), list): errors.append(f"{field} must be a list")
    for index, loss in enumerate(data.get("lossy_mappings", [])):
        if not isinstance(loss, dict) or not loss.get("source_field") or not loss.get("reason") or loss.get("severity") not in {"low", "medium", "high", "blocking"}:
            errors.append(f"lossy_mappings[{index}] is incomplete")
    round_trip = data.get("round_trip")
    if not isinstance(round_trip, dict) or round_trip.get("status") not in {"not_run", "lossless", "lossy_reported", "fail"} or not isinstance(round_trip.get("differences"), list):
        errors.append("invalid round_trip result")
    if data.get("direction") == "round-trip" and round_trip.get("status") == "lossy_reported" and not data.get("lossy_mappings"):
        errors.append("lossy round trip must disclose lossy_mappings")
    result = {"status": "pass" if not errors else "fail", "errors": errors, "report": str(path.resolve())}
    if args.json_output: Path(args.json_output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__": raise SystemExit(main())
