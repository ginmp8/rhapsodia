#!/usr/bin/env python3
"""Write MAGIA-owned artifact scaffolds from canonical MAGIA templates."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "assets" / "templates"
PLANNING_OWNED_ARTIFACTS = {
    "cycle.yaml",
    "manifest.yaml",
    "tasks.md",
    "notes.md",
    "validation.md",
}


def available_templates() -> list[str]:
    return sorted(path.name for path in TEMPLATES_DIR.iterdir() if path.is_file() and path.name.endswith(".template"))


def artifact_name_from_template(template_name: str) -> str:
    return template_name[:-9] if template_name.endswith(".template") else template_name


def infer_template_name(destination: Path) -> str | None:
    if destination.name in PLANNING_OWNED_ARTIFACTS or destination.parent.name == "registry":
        return None
    candidate = f"{destination.name}.template"
    if (TEMPLATES_DIR / candidate).exists():
        return candidate
    return None


def planning_artifact_error(artifact_name: str) -> str:
    return (
        f"`{artifact_name}` is a planning-owned artifact. MAGIA must not scaffold it. "
        "Use the planning workflow to create or normalize the package, then use MAGIA execution-state "
        "scripts only to update existing records from truthful execution evidence."
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Write a MAGIA-owned artifact scaffold from canonical MAGIA templates.")
    parser.add_argument("path", help="Destination artifact path.")
    parser.add_argument("--template", help="Explicit MAGIA template file name, for example `implementation-notes.md.template`.")
    parser.add_argument("--force", action="store_true", help="Overwrite the destination file if it already exists.")
    args = parser.parse_args(argv)

    destination = Path(args.path).resolve()
    if destination.name in PLANNING_OWNED_ARTIFACTS or destination.parent.name == "registry":
        print(f"ERROR: {planning_artifact_error(destination.name)}")
        return 1

    if destination.exists() and not args.force:
        print(f"ERROR: destination already exists: {destination}")
        print("Use --force to overwrite.")
        return 1

    template_name = args.template or infer_template_name(destination)
    if not template_name:
        print(f"ERROR: could not infer a MAGIA-owned template for `{destination.name}`")
        print(f"Available MAGIA templates: {', '.join(available_templates())}")
        return 1

    template_artifact = artifact_name_from_template(Path(template_name).name)
    if template_artifact in PLANNING_OWNED_ARTIFACTS:
        print(f"ERROR: {planning_artifact_error(template_artifact)}")
        return 1

    template_path = TEMPLATES_DIR / Path(template_name).name
    if not template_path.exists():
        print(f"ERROR: unknown MAGIA template `{template_name}`")
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, destination)
    print(f"OK: wrote {destination} from {template_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
