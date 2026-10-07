#!/usr/bin/env python3
"""Validate that every advertised PDF capability has an executable helper or canonical example."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(root: Path) -> dict:
    registry_path = root / "references" / "capability-registry.json"
    errors: list[str] = []
    covered: list[str] = []
    if not registry_path.is_file():
        return {"status": "fail", "covered_operations": [], "errors": [f"missing registry: {registry_path}"]}

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "fail", "covered_operations": [], "errors": [f"invalid registry JSON: {exc}"]}

    operations = registry.get("operations")
    if not isinstance(operations, dict) or not operations:
        return {"status": "fail", "covered_operations": [], "errors": ["registry.operations must be a non-empty object"]}

    for name, record in operations.items():
        if not isinstance(record, dict):
            errors.append(f"{name}: record must be an object")
            continue

        script_ok = False
        example_ok = False

        script = record.get("script")
        if script:
            script_path = root / script
            if script_path.is_file():
                script_ok = True
            else:
                errors.append(f"{name}: missing script {script}")

        example = record.get("example")
        token = record.get("example_token")
        if example:
            example_path = root / example
            if not example_path.is_file():
                errors.append(f"{name}: missing example file {example}")
            elif token:
                text = example_path.read_text(encoding="utf-8", errors="replace")
                if token in text:
                    example_ok = True
                else:
                    errors.append(f"{name}: example token {token!r} not found in {example}")
            else:
                example_ok = True

        if not script_ok and not example_ok:
            errors.append(f"{name}: no executable helper or canonical example is available")
        else:
            covered.append(name)

    return {
        "status": "pass" if not errors else "fail",
        "covered_operations": sorted(covered),
        "operation_count": len(operations),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    result = validate(args.root.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for err in result["errors"]:
            print(f"- {err}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
