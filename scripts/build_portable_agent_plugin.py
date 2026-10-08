#!/usr/bin/env python3
"""Build a clean portable package in a new destination; never destroy user output."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_marketplace_manifests import ROOT, json_bytes, load_catalog, render_portable_manifest
from package_policy import copy_ignore


def build(output: Path) -> None:
    if output.is_symlink():
        raise ValueError('output may not be a symbolic link')
    output = output.resolve()
    root = ROOT.resolve()
    if output == root or output in root.parents or (output.is_relative_to(root) and not output.is_relative_to(root / 'dist')):
        raise ValueError('output must be outside source paths, or within the dedicated dist/ directory')
    if output.exists():
        raise ValueError('output already exists; choose a new destination to preserve existing files')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.rhapsodia-plugin-', dir=output.parent))
    try:
        (staging / 'plugin.json').write_bytes(json_bytes(render_portable_manifest(load_catalog())))
        shutil.copytree(ROOT / 'skills', staging / 'skills', ignore=copy_ignore)
        portable_mcp = ROOT / 'mcp.json'
        if portable_mcp.is_symlink():
            raise ValueError('MCP configuration may not be a symbolic link')
        if portable_mcp.is_file():
            shutil.copy2(portable_mcp, staging / 'mcp.json')
        if output.exists():
            raise ValueError('output was created concurrently; nothing was replaced')
        os.rename(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.output)
    except (OSError, ValueError, KeyError) as exc:
        print(f'portable plugin build failed: {exc}', file=sys.stderr)
        return 2
    print(f'built portable Agent Plugins package at {args.output.resolve()}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
