#!/usr/bin/env python3
"""Write nomia artifacts from canonical template scripts instead of freehand template copying."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "assets" / "templates"
OPS_TEMPLATE = "ops.yaml.template"


def available_templates() -> list[str]:
    return sorted(path.name for path in TEMPLATES_DIR.iterdir() if path.is_file() and path.name.endswith(".template"))


def infer_template_name(destination: Path) -> str | None:
    candidate = f"{destination.name}.template"
    if (TEMPLATES_DIR / candidate).exists():
        return candidate
    return None


def copy_template(template_name: str, destination: Path) -> None:
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"unknown template `{template_name}`")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, destination)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Write a nomia artifact scaffold from the canonical template workflow.")
    parser.add_argument("path", help="Destination artifact path.")
    parser.add_argument("--template", help="Explicit template file name, for example `roadmap.md.template`.")
    parser.add_argument("--spec-id", help="Externally supplied spec id for ops.yaml generation. Used only when the resolved template is ops.yaml.template.")
    parser.add_argument("--spec-id-provenance", help="Evidence reference for --spec-id. Used only for ops.yaml.template.")
    parser.add_argument("--list-data", help="YAML or JSON payload for scripts/update_template_lists.py.")
    parser.add_argument("--force", action="store_true", help="Overwrite the destination file if it already exists.")
    args = parser.parse_args(argv)

    destination = Path(args.path).resolve()
    if destination.exists() and not args.force:
        print(f"ERROR: destination already exists: {destination}")
        print("Use --force to overwrite.")
        return 1

    template_name = args.template or infer_template_name(destination)
    if not template_name:
        print(f"ERROR: could not infer a nomia template for `{destination.name}`")
        print(f"Available templates: {', '.join(available_templates())}")
        return 1

    if template_name == OPS_TEMPLATE:
        from write_ops_scaffold import main as write_ops_main

        forwarded: list[str] = [str(destination)]
        if args.spec_id:
            forwarded.extend(["--spec-id", args.spec_id])
        if args.spec_id_provenance:
            forwarded.extend(["--spec-id-provenance", args.spec_id_provenance])
        if args.list_data:
            forwarded.extend(["--list-data", args.list_data])
        if args.force:
            forwarded.append("--force")
        return write_ops_main(forwarded)

    try:
        copy_template(template_name, destination)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.list_data:
        from update_template_lists import main as update_lists_main

        result = update_lists_main([str(destination), "--data", args.list_data])
        if result != 0:
            return result

    print(f"OK: wrote {destination} from {template_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
