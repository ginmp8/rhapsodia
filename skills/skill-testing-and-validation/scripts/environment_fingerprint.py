#!/usr/bin/env python3
"""Emit a stable environment/runtime fingerprint without timestamps."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

TOOL_VERSION_ARGS: dict[str, list[str]] = {
    "node": ["--version"],
    "npm": ["--version"],
    "dotnet": ["--version"],
    "go": ["version"],
    "cargo": ["--version"],
    "java": ["-version"],
    "mvn": ["--version"],
    "gradle": ["--version"],
    "make": ["--version"],
    "bash": ["--version"],
}


def first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:240]
    return ""


def tool_identity(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    item: dict[str, Any] = {"name": name, "available": bool(path), "path": str(Path(path).resolve()) if path else None, "version": None}
    if not path:
        return item
    args = TOOL_VERSION_ARGS.get(name)
    if not args:
        return item
    try:
        proc = subprocess.run([path, *args], text=True, capture_output=True, timeout=3)
        text = proc.stdout if proc.stdout.strip() else proc.stderr
        item["version"] = first_line(text)
    except Exception:
        item["version"] = None
    return item


def fingerprint(target: Path, tools: list[str] | None = None) -> dict[str, Any]:
    root = target.resolve()
    requested = sorted(set(TOOL_VERSION_ARGS.keys() if tools is None else tools))
    return {
        "fingerprint_version": 1,
        "target": str(root),
        "os": {
            "name": os.name,
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": {
            "executable": str(Path(sys.executable).resolve()),
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "tools": [tool_identity(name) for name in requested],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Emit a stable environment/runtime fingerprint without timestamps.")
    ap.add_argument("target", nargs="?", default=".")
    ap.add_argument("--tool", action="append", dest="tools", help="Tool name to fingerprint; repeatable")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()
    result = fingerprint(Path(args.target), args.tools)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Target: {result['target']}")
        print(f"Python: {result['python']['version']} ({result['python']['executable']})")
        for item in result["tools"]:
            print(f"{item['name']}: {'available' if item['available'] else 'missing'} {item['version'] or ''}".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
