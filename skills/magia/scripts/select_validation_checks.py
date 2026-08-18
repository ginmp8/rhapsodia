#!/usr/bin/env python3
"""Select validation categories from explicit change surfaces without running checks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_SURFACES = {
    "docs", "code", "config", "api", "event", "schema", "migration", "auth",
    "secrets", "pii", "performance", "availability", "multi-repo",
}
GOVERNED_SURFACES = {"api", "event", "schema", "migration", "auth", "secrets", "pii", "availability", "multi-repo"}

REQUIRED_BY_SURFACE = {
    "docs": ["documentation-validation"],
    "code": ["targeted-test"],
    "config": ["configuration-validation", "smoke"],
    "api": ["contract-validation", "compatibility", "integration"],
    "event": ["contract-validation", "compatibility", "integration"],
    "schema": ["contract-validation", "compatibility"],
    "migration": ["migration-forward", "data-integrity", "rollback-recovery"],
    "auth": ["authorization", "abuse-case", "targeted-integration"],
    "secrets": ["security-static", "secret-handling"],
    "pii": ["security-static", "sensitive-data"],
    "performance": ["performance"],
    "availability": ["resilience", "observability", "smoke"],
    "multi-repo": ["per-repo-validation", "cross-repo-integration", "reconciliation"],
}

RECOMMENDED_BY_SURFACE = {
    "docs": ["link-check"],
    "code": ["build", "lint-static"],
    "config": ["rollback-recovery"],
    "api": ["consumer-check"],
    "event": ["consumer-check", "ordering-idempotency"],
    "schema": ["consumer-check"],
    "migration": ["observability", "smoke"],
    "auth": ["security-static"],
    "secrets": ["rotation-review"],
    "pii": ["logging-review", "retention-review"],
    "performance": ["baseline-comparison"],
    "availability": ["rollback-recovery"],
    "multi-repo": ["rollout-order"],
}

PROOF_PRIORITY = [
    "targeted-test", "documentation-validation", "configuration-validation", "contract-validation",
    "authorization", "migration-forward", "security-static", "performance", "resilience",
    "per-repo-validation", "integration", "smoke",
]


def unique_order(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def analyze(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"status": "blocked", "errors": ["input root must be an object"]}
    surfaces = data.get("surfaces")
    available = data.get("available_checks", [])
    errors: list[str] = []
    if not isinstance(surfaces, list) or not surfaces or not all(isinstance(x, str) and x for x in surfaces):
        errors.append("surfaces must be a non-empty string list")
        surfaces = []
    if not isinstance(available, list) or not all(isinstance(x, str) and x for x in available):
        errors.append("available_checks must be a string list")
        available = []
    unknown = sorted(set(surfaces) - ALLOWED_SURFACES)
    if unknown:
        errors.append(f"unknown surfaces: {', '.join(unknown)}")
    if errors:
        return {"kind": "magia-validation-selection", "version": 1, "selection_stage": "explicit-proof-category-selection", "status": "blocked", "errors": errors}

    normalized = unique_order(surfaces)
    required = unique_order([check for surface in normalized for check in REQUIRED_BY_SURFACE[surface]])
    recommended = unique_order([check for surface in normalized for check in RECOMMENDED_BY_SURFACE[surface] if check not in required])
    available_set = set(available)
    blocked = [check for check in required if check not in available_set]
    narrowest = next((check for check in PROOF_PRIORITY if check in required), required[0])
    profile = "governed" if set(normalized) & GOVERNED_SURFACES else "standard"
    return {
        "kind": "magia-validation-selection",
        "version": 1,
        "selection_stage": "explicit-proof-category-selection",
        "status": "blocked-required-checks" if blocked else "ready-to-execute-checks",
        "read_only": True,
        "checks_executed": [],
        "risk_profile": profile,
        "surfaces": normalized,
        "narrowest_proving_category": narrowest,
        "required_checks": required,
        "recommended_checks": recommended,
        "available_checks": sorted(set(available)),
        "blocked_required_checks": blocked,
        "limitations": [
            "categories require repository-specific commands or methods before execution",
            "selection does not alter product acceptance criteria",
            "no check result is implied or executed",
        ],
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines = ["# MAGIA Validation Selection", "", f"- Status: `{result['status']}`"]
    if result.get("errors"):
        return "\n".join(lines + ["", "## Errors", *[f"- {item}" for item in result["errors"]], ""])
    lines += [
        f"- Risk profile: `{result['risk_profile']}`",
        f"- Narrowest proving category: `{result['narrowest_proving_category']}`",
        "",
        "## Required checks",
        *[f"- `{item}`" for item in result["required_checks"]],
        "",
        "## Recommended checks",
        *([f"- `{item}`" for item in result["recommended_checks"]] or ["- `none`"]),
        "",
        "## Blocked required checks",
        *([f"- `{item}`" for item in result["blocked_required_checks"]] or ["- `none`"]),
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select required validation categories from explicit change surfaces.")
    parser.add_argument("--input", required=True, help="JSON request containing surfaces and available_checks.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", help="Optional output path. Defaults to stdout.")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read input: {exc}")
    result = analyze(data)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n" if args.format == "json" else to_markdown(result)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
