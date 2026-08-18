#!/usr/bin/env python3
"""Validate nomia canonical identity, path, and independence contracts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from nomia_utils import (
    CANONICAL_BOARD_ROOT_TEMPLATE,
    CANONICAL_SPEC_PACKAGE_TEMPLATE,
    CANONICAL_SPEC_REGISTRY_TEMPLATE,
)

EXPECTED_BOARD_ROOT = "docs/boards/<board_id>/<year>/cycles/<cycle_id>/"
EXPECTED_SPEC_PACKAGE = EXPECTED_BOARD_ROOT + "specs/<spec_id>/"
EXPECTED_SPEC_REGISTRY = EXPECTED_BOARD_ROOT + "registry/<spec_id>.yaml"
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".template", ".txt", ".toml"}
RETIRED_CYCLE_FIELD = "cycle" + "_version"
RETIRED_SPEC_PROSE = "spec" + "NNN"
LEGACY_PATTERNS = {
    "former ULID cycle id": re.compile(r"(?<![a-z0-9-])(?:cycle-)?\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*--[0-9a-hjkmnp-tv-z]{26}(?![a-z0-9])"),
    "former ULID spec id": re.compile(r"\bspec-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*--[0-9a-hjkmnp-tv-z]{26}\b"),
    "retired cycle identity field": re.compile(rf"\b{re.escape(RETIRED_CYCLE_FIELD)}\b"),
    "sequential spec id prose": re.compile(rf"\b{re.escape(RETIRED_SPEC_PROSE)}\b"),
    "sequential spec id literal": re.compile(r"\bspec\d{3}\b"),
    "sequential spec id regex": re.compile("spec" + r"(?:\\d|\[0-9\])"),
}
# Preservation metadata and negative unit tests intentionally name retired forms.
EXCLUDED_LEGACY_SCAN = {
    "tests/original-contract.json",
    "tests/test_identity_model.py",
    "examples/activation-scenarios.json",
    "examples/hardening-scenarios.json",
    "evals/activation-boundary-scenarios.json",
    "scripts/nomia_utils.py",
    "scripts/validate_identity_contract.py",
    "references/canonical-paths.md",
}
EXTERNAL_SKILL_PATTERNS = [
    re.compile(r"/home/oai/skills/(?:mago|magia)(?:/|\b)"),
    re.compile(r"from\s+(?:mago|magia)(?:\.|\s+import)"),
    re.compile(r"import\s+(?:mago|magia)(?:\.|\s|$)"),
]


def scan_text_files(root: Path) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        if rel in EXCLUDED_LEGACY_SCAN:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "SKILL.md":
            continue
        try:
            items.append((rel, path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            continue
    return items


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if CANONICAL_BOARD_ROOT_TEMPLATE != EXPECTED_BOARD_ROOT:
        errors.append("nomia_utils canonical board root does not match the agreed model")
    if CANONICAL_SPEC_PACKAGE_TEMPLATE != EXPECTED_SPEC_PACKAGE:
        errors.append("nomia_utils canonical spec package does not match the agreed model")
    if CANONICAL_SPEC_REGISTRY_TEMPLATE != EXPECTED_SPEC_REGISTRY:
        errors.append("nomia_utils canonical registry path does not match the agreed model")

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    canonical_text = (root / "references" / "canonical-paths.md").read_text(encoding="utf-8")
    required_phrases = [
        EXPECTED_BOARD_ROOT,
        "cycle-YYYY-MM-DD-cycle-key",
        "spec-YYYY-MM-DD-feature-key",
        "candidate_spec_id_provenance",
        "does not require Mago or Magia skill files",
        "must not mint planning identities",
        "never create or modify them",
    ]
    combined = skill_text + "\n" + canonical_text + "\n" + (root / "references" / "common-governance.md").read_text(encoding="utf-8")
    for phrase in required_phrases:
        if phrase not in combined:
            errors.append(f"canonical contract phrase is missing: {phrase}")

    for rel, text in scan_text_files(root):
        for label, pattern in LEGACY_PATTERNS.items():
            for match in pattern.finditer(text):
                errors.append(f"legacy {label} remains in {rel}:{text.count(chr(10), 0, match.start()) + 1}")
        for pattern in EXTERNAL_SKILL_PATTERNS:
            if pattern.search(text):
                errors.append(f"operational dependency on another skill package detected in {rel}")

    agent_text = (root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if agent_text.count("assets/icon.svg") < 2:
        errors.append("agents/openai.yaml must keep assets/icon.svg for both icon sizes")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate nomia canonical identity and package independence.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="Path to the nomia skill root.")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} identity-contract errors")
        return 1
    print("OK: canonical identity, paths, independence, and icon references are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
