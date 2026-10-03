#!/usr/bin/env python3
"""Build a portable Agent Plugins 1.0 package from the canonical RhapsodIA skills tree."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from generate_marketplace_manifests import ROOT, json_bytes, load_catalog, render_portable_manifest


def build(output: Path) -> None:
    output = output.resolve()
    root = ROOT.resolve()
    if output == root or output in root.parents:
        raise ValueError("output must not be the repository root or an ancestor of it")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    (output / "plugin.json").write_bytes(json_bytes(render_portable_manifest(load_catalog())))
    shutil.copytree(ROOT / "skills", output / "skills")

    portable_mcp = ROOT / "mcp.json"
    if portable_mcp.is_file():
        shutil.copy2(portable_mcp, output / "mcp.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.output)
    except (OSError, ValueError, KeyError) as exc:
        print(f"portable plugin build failed: {exc}", file=sys.stderr)
        return 2
    print(f"built portable Agent Plugins package at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
