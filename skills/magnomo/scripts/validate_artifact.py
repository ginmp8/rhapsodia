#!/usr/bin/env python3
"""Dispatch Magnomo artifact validation without relying on manual validator selection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def existing_sibling(path: Path, name: str) -> Path:
    candidate = path.parent / name
    return candidate


def validate_one(path: Path) -> int:
    name = path.name
    if name == "ops.yaml":
        from validate_ops import main as validate_ops_main

        return validate_ops_main([str(path)])

    if name in {"roadmap.yaml", "feature-map.yaml"}:
        from validate_roadmap import main as validate_roadmap_main

        roadmap = path if name == "roadmap.yaml" else existing_sibling(path, "roadmap.yaml")
        feature_map = path if name == "feature-map.yaml" else existing_sibling(path, "feature-map.yaml")
        return validate_roadmap_main(["--roadmap", str(roadmap), "--feature-map", str(feature_map)])

    if name in {"feature-report.md", "release-notes.md", "internal-notes.md"}:
        from validate_reporting import main as validate_reporting_main

        if name == "feature-report.md":
            return validate_reporting_main(
                [
                    "--mode",
                    "feature-report",
                    "--feature-report",
                    str(path),
                    "--internal-notes",
                    str(existing_sibling(path, "internal-notes.md")),
                ]
            )

        return validate_reporting_main(
            [
                "--mode",
                "release-notes",
                "--release-notes",
                str(path if name == "release-notes.md" else existing_sibling(path, "release-notes.md")),
                "--internal-notes",
                str(path if name == "internal-notes.md" else existing_sibling(path, "internal-notes.md")),
            ]
        )

    if name in {"portfolio.yaml", "portfolio.md"}:
        from validate_portfolio import main as validate_portfolio_main

        return validate_portfolio_main(
            [
                "--portfolio-yaml",
                str(path if name == "portfolio.yaml" else existing_sibling(path, "portfolio.yaml")),
                "--portfolio-md",
                str(path if name == "portfolio.md" else existing_sibling(path, "portfolio.md")),
            ]
        )

    if name in {"status.md", "stakeholder-brief.md", "replanning.md", "roadmap.md", "rfc-proposals.md", "governance-decisions.md"}:
        from validate_human_artifacts import main as validate_human_main

        return validate_human_main([str(path)])

    print(f"ERROR: unsupported Magnomo artifact `{name}`")
    return 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a Magnomo artifact with the canonical validator for its template family.")
    parser.add_argument("paths", nargs="+", help="Artifact path(s) to validate.")
    args = parser.parse_args(argv)

    exit_code = 0
    for raw_path in args.paths:
        result = validate_one(Path(raw_path).resolve())
        if result != 0:
            exit_code = result
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
