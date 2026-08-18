#!/usr/bin/env python3
"""Validate reachability and selector ownership for active MAGIA resources."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RESOURCE_ROUTES = {
    "references/convergence-and-validation.md": ("SKILL.md", "references/resource-map.md"),
    "references/public-artifact-adapters.md": ("SKILL.md", "references/resource-map.md"),
    "scripts/select_validation.py": ("SKILL.md", "references/resource-map.md", "references/convergence-and-validation.md"),
    "scripts/select_validation_checks.py": ("SKILL.md", "references/resource-map.md", "references/validation-selection.md"),
    "scripts/validate_convergence.py": ("references/resource-map.md", "references/convergence-and-validation.md"),
    "scripts/adapt_public_artifacts.py": ("references/resource-map.md", "references/public-artifact-adapters.md"),
    "scripts/validate_resource_integration.py": ("references/resource-map.md", "scripts/validate_skill_package.py"),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    for resource, consumers in RESOURCE_ROUTES.items():
        path = root / resource
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing operational resource: {resource}")
            continue
        for consumer in consumers:
            consumer_path = root / consumer
            if not consumer_path.is_file():
                errors.append(f"missing resource-routing consumer: {consumer}")
                continue
            if resource not in read_text(consumer_path):
                errors.append(f"operational resource {resource} is not routed from {consumer}")

    profile_text = read_text(root / "scripts/select_validation.py") if (root / "scripts/select_validation.py").is_file() else ""
    checks_text = read_text(root / "scripts/select_validation_checks.py") if (root / "scripts/select_validation_checks.py").is_file() else ""
    if '"kind": "magia-risk-profile-selection"' not in profile_text or '"selection_stage": "preliminary-risk-inference"' not in profile_text:
        errors.append("scripts/select_validation.py must declare the preliminary risk-profile output contract")
    if '"kind": "magia-validation-selection"' not in checks_text or '"selection_stage": "explicit-proof-category-selection"' not in checks_text:
        errors.append("scripts/select_validation_checks.py must declare the explicit proof-category output contract")

    return {
        "status": "pass" if not errors else "fail",
        "target": str(root),
        "route_count": len(RESOURCE_ROUTES),
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate(Path(args.target))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        output = Path(args.json_output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
