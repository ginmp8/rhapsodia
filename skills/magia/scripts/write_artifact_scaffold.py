#!/usr/bin/env python3
"""Write MAGIA artifacts from canonical templates instead of freehand copying."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "assets" / "templates"


def available_templates() -> list[str]:
    return sorted(path.name for path in TEMPLATES_DIR.iterdir() if path.is_file() and path.name.endswith(".template"))


def infer_template_name(destination: Path) -> str | None:
    candidate = f"{destination.name}.template"
    if (TEMPLATES_DIR / candidate).exists():
        return candidate
    return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Write a MAGIA artifact scaffold from the canonical template workflow.")
    parser.add_argument("path", help="Destination artifact path.")
    parser.add_argument("--template", help="Explicit template file name, for example `notes.md.template`.")
    parser.add_argument("--list-data", help="YAML payload for scripts/update_template_lists.py.")
    parser.add_argument("--force", action="store_true", help="Overwrite the destination file if it already exists.")
    args = parser.parse_args(argv)

    destination = Path(args.path).resolve()
    if destination.exists() and not args.force:
        print(f"ERROR: destination already exists: {destination}")
        print("Use --force to overwrite.")
        return 1

    template_name = args.template or infer_template_name(destination)
    if not template_name:
        print(f"ERROR: could not infer a MAGIA template for `{destination.name}`")
        print(f"Available templates: {', '.join(available_templates())}")
        return 1

    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        print(f"ERROR: unknown template `{template_name}`")
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, destination)
    if args.list_data:
        from update_template_lists import main as update_lists_main

        result = update_lists_main([str(destination), "--data", args.list_data])
        if result != 0:
            return result

    print(f"OK: wrote {destination} from {template_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
