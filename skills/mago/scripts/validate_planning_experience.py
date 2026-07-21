#!/usr/bin/env python3
"""Validate Mago onboarding, projection, clarification, discovery, and adapter integration."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

REQUIRED = {
    "SKILL.md": [
        "references/getting-started.md",
        "references/clarification-prioritization.md",
        "references/planning-compass.md",
        "references/execution-wave-projection.md",
        "references/adapter-development-contract.md",
        "references/brownfield-discovery-summary.md",
        "scripts/render_planning_compass.py",
        "scripts/render_execution_waves.py",
    ],
    "references/getting-started.md": ["Nomia", "Magia", "Quick", "Standard", "Governed"],
    "references/planning-compass.md": ["authoritative", "not_observed", "render_planning_compass.py"],
    "references/execution-wave-projection.md": ["Magia", "dependency", "render_execution_waves.py"],
    "references/adapter-development-contract.md": ["version", "loss", "non-authoritative"],
    "references/brownfield-discovery-summary.md": ["repository evidence", "assets/templates/brownfield-discovery-summary.md.template"],
    "references/clarification-prioritization.md": ["Question budget", "Handoff blocking", "affected IDs"],
}
SCRIPTS = ("scripts/render_planning_compass.py", "scripts/render_execution_waves.py")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    errors: list[str] = []
    for relative, markers in REQUIRED.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required planning-experience resource: {relative}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing integration marker {marker!r}")
    template = root / "assets/templates/brownfield-discovery-summary.md.template"
    if not template.is_file():
        errors.append("missing brownfield discovery summary template")
    for relative in SCRIPTS:
        path = root / relative
        if not path.is_file():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{relative}: syntax error: {exc}")
    if errors:
        print("FAIL planning experience contract")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS planning experience contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
