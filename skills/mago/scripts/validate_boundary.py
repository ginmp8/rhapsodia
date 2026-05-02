#!/usr/bin/env python3
"""
Validate that the MAGO skill stays self-contained.

The validator intentionally scans only the MAGO skill directory. It does not read
or require any sibling skill package.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from mago_utils import dedupe_preserve_order, posix_rel, read_text_file


MAGIARCA = "magiarca"

DIRECT_DEPENDENCY_PATTERNS = [
    (".github" + "/skills/" + MAGIARCA, "references the sibling skill directory"),
    (".github" + "\\skills\\" + MAGIARCA, "references the sibling skill directory"),
    ("skills://" + MAGIARCA, "uses another skill URI"),
    ("../" + MAGIARCA, "uses a relative path to another skill"),
    ("..\\" + MAGIARCA, "uses a relative path to another skill"),
]

FORBIDDEN_MODE_NAMES = [
    "delivery" + "-intake",
    "delivery" + "-triage",
    "delivery" + "-status",
    "delivery" + "-replan",
    "delivery" + "-portfolio",
    "roadmap" + "-define",
    "roadmap" + "-refine",
    "roadmap" + "-to-specs",
    "feature" + "-report",
    "release" + "-notes",
    "validate" + "-contracts",
    "normalize" + "-human-artifacts",
]

MAGIARCA_OWNED_ARTIFACTS = [
    "ops" + ".yaml",
    "status" + ".md",
    "stakeholder" + "-brief.md",
    "replanning" + ".md",
    "roadmap" + ".yaml",
    "roadmap" + ".md",
    "roadmap" + "-decisions.md",
    "feature" + "-map.yaml",
    "feature" + "-report.md",
    "release" + "-notes.md",
    "internal" + "-notes.md",
    "portfolio" + ".md",
    "portfolio" + ".yaml",
]

SCRIPT_ACTION_RE = re.compile(
    r"\b(create|created|creating|update|updated|updating|write|wrote|writing|"
    r"normalize|normalized|normalizing|validate|validated|validating)\b",
    re.IGNORECASE,
)
PY_IMPORT_RE = re.compile(r"\b(?:from|import)\s+[.\w]*" + MAGIARCA + r"\b", re.IGNORECASE)

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".template",
    ".txt",
}


def skill_root() -> Path:
    root = Path(__file__).resolve().parents[1]
    if not (root / "SKILL.md").is_file():
        raise RuntimeError(f"validate_boundary.py must live under an extracted MAGO skill root, got: {root}")
    return root


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix in TEXT_SUFFIXES or path.name.endswith(".template"):
            files.append(path)
    return files


def validate_direct_dependencies(root: Path, path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for pattern, reason in DIRECT_DEPENDENCY_PATTERNS:
        pattern_lower = pattern.lower()
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern_lower in line.lower():
                errors.append(f"{posix_rel(path, root)}:{line_number}: {reason}: `{pattern}`")

    if path.suffix == ".py" and PY_IMPORT_RE.search(text):
        for line_number, line in enumerate(text.splitlines(), start=1):
            if PY_IMPORT_RE.search(line):
                errors.append(f"{posix_rel(path, root)}:{line_number}: imports a module named `{MAGIARCA}`")

    return errors


def validate_modes(root: Path) -> list[str]:
    errors: list[str] = []
    skill_md = root / "SKILL.md"
    if skill_md.exists():
        text = read_text_file(skill_md).lower()
        for mode in FORBIDDEN_MODE_NAMES:
            if mode in text:
                errors.append(f"{posix_rel(skill_md, root)}: defines or references forbidden mode `{mode}`")

    references_root = root / "references"
    if references_root.exists():
        mode_paths = list(sorted(references_root.glob("modes/*.md")))
        for path in mode_paths:
            stem = path.stem
            if stem in FORBIDDEN_MODE_NAMES:
                errors.append(f"{posix_rel(path, root)}: forbidden mode reference file")

    return errors


def validate_script_artifact_targets(root: Path) -> list[str]:
    errors: list[str] = []
    scripts_root = root / "scripts"
    if not scripts_root.exists():
        return errors

    boundary_script = Path(__file__).resolve()
    for path in sorted(scripts_root.glob("*.py")):
        if path.resolve() == boundary_script:
            continue
        text = read_text_file(path)
        lower_text = text.lower()
        for artifact in MAGIARCA_OWNED_ARTIFACTS:
            if artifact not in lower_text:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                line_lower = line.lower()
                if artifact in line_lower and SCRIPT_ACTION_RE.search(line):
                    errors.append(
                        f"{posix_rel(path, root)}:{line_number}: script appears to act on `{artifact}`"
                    )
    return errors


def main() -> int:
    root = skill_root()
    files = iter_text_files(root)
    errors: list[str] = []

    for path in files:
        text = read_text_file(path)
        errors.extend(validate_direct_dependencies(root, path, text))

    errors.extend(validate_modes(root))
    errors.extend(validate_script_artifact_targets(root))

    errors = dedupe_preserve_order(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1

    print(f"OK: validated {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
