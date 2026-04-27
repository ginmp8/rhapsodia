#!/usr/bin/env python3
"""Normalize Magnomo human artifacts without inventing content."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from magnomo_utils import compact_yaml_exception, unique

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


ENUM_KEYS = {"state", "level", "commitment", "confidence", "horizon"}
REQUIRED_HEADINGS_BY_NAME = {
    "status.md": ["# Status", "## Summary", "## Current State", "## Risks And Blockers", "## Next Steps", "## Unknowns"],
    "stakeholder-brief.md": [
        "# Stakeholder Brief",
        "## Summary",
        "## Decision Needed",
        "## Impact",
        "## Timing",
        "## Risks",
    ],
    "replanning.md": ["# Replanning", "## Entries"],
    "roadmap.md": ["# Roadmap", "## Context", "## Themes", "## Sequencing", "## Dependencies", "## Risks", "## Open Decisions"],
    "rfc-proposals.md": ["# RFC Proposals", "## Entries"],
    "adr-records.md": ["# ADR Records", "## Entries"],
    "feature-report.md": [
        "# Feature Report",
        "## Summary",
        "## Delivered Scope",
        "## Evidence",
        "## Validation",
        "## Risks And Limitations",
        "## Follow-ups",
    ],
    "release-notes.md": [
        "# Release Notes",
        "## Summary",
        "## User Impact",
        "## Changes",
        "## Rollout",
        "## Known Limitations",
    ],
    "internal-notes.md": ["# Internal Notes", "## Summary", "## Internal Details", "## Follow-ups"],
    "portfolio.md": ["# Portfolio", "## Summary", "## Items", "## Blocked", "## Risks", "## Replans"],
}


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if value == "":
        return None
    return value


def normalize_enums(value: Any, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {item_key: normalize_enums(item_value, item_key) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [normalize_enums(item) for item in value]
    if key in ENUM_KEYS and isinstance(value, str):
        return value.strip().lower()
    return value


def normalize_yaml(path: Path, check: bool) -> bool:
    if yaml is None:
        raise RuntimeError("PyYAML is required to normalize Magnomo YAML artifacts.")
    original = path.read_text(encoding="utf-8")
    data = yaml.safe_load(original) or {}
    normalized = normalize_enums(normalize_value(data))
    rendered = yaml.safe_dump(normalized, sort_keys=False, allow_unicode=False)
    if rendered != original:
        if not check:
            path.write_text(rendered, encoding="utf-8")
        return True
    return False


def normalize_markdown(path: Path, check: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in original.splitlines()]
    headings = REQUIRED_HEADINGS_BY_NAME.get(path.name, [])
    if "".join(lines).strip():
        present = {line.strip() for line in lines}
        for heading in headings:
            if heading not in present:
                if lines and lines[-1].strip():
                    lines.append("")
                lines.extend([heading, ""])
                present.add(heading)
    rendered = "\n".join(lines).rstrip() + "\n"
    if rendered != original:
        if not check:
            path.write_text(rendered, encoding="utf-8")
        return True
    return False



def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Normalize Magnomo artifacts without inventing content.")
    parser.add_argument("paths", nargs="+", help="YAML or Markdown artifacts to normalize.")
    parser.add_argument("--check", action="store_true", help="Report files that would change without writing them.")
    args = parser.parse_args(argv)

    changed_paths: list[Path] = []
    errors: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path).resolve()
        if not path.exists():
            errors.append(f"{path}: missing file")
            continue
        try:
            if path.suffix in {".yaml", ".yml"}:
                changed = normalize_yaml(path, args.check)
            elif path.suffix == ".md":
                changed = normalize_markdown(path, args.check)
            else:
                errors.append(f"{path}: unsupported artifact type")
                continue
        except Exception as exc:
            errors.append(f"{path}: {compact_yaml_exception(exc)}")
            continue
        if changed:
            changed_paths.append(path)

    if args.check:
        errors.extend(f"{path}: would normalize" for path in changed_paths)

    errors = unique(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1

    if changed_paths:
        print(f"OK: normalized {len(changed_paths)} files")
    elif args.check:
        print(f"OK: checked {len(args.paths)} files")
    else:
        print("OK: completed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
