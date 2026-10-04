#!/usr/bin/env python3
"""Statically assess whether target-owned executable content requires isolation before execution."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from typing import Any
from _harness_common import dump_json, is_secret_like

EXEC_SUFFIXES = {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".ps1", ".cmd", ".bat", ".exe", ".dll", ".so", ".dylib"}
SOURCE_CLASSES = {"trusted-owned", "trusted-local", "external-untrusted", "unknown"}


def assess(root: Path, source_class: str) -> dict[str, Any]:
    errors: list[str] = []
    if source_class not in SOURCE_CLASSES:
        return {"status": "fail", "errors": [f"source_class must be one of {sorted(SOURCE_CLASSES)}"]}
    if not root.is_dir():
        return {"status": "fail", "errors": ["target must be a directory"]}
    executable: list[str] = []
    secret_like: list[str] = []
    symlinks: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            try:
                target = str(path.resolve(strict=False))
            except RuntimeError:
                target = "<cycle>"
            symlinks.append({"path": rel, "target": target})
            continue
        if path.is_file():
            if path.suffix.lower() in EXEC_SUFFIXES:
                executable.append(rel)
            else:
                try:
                    first = path.open("rb").read(128)
                    if first.startswith(b"#!"):
                        executable.append(rel)
                except OSError:
                    pass
            if is_secret_like(rel):
                secret_like.append(rel)
    if secret_like:
        policy = "inspect-only"
        errors.append("secret-like files are present; do not execute target-owned code until secrets are removed or explicitly isolated")
    elif source_class in {"external-untrusted", "unknown"} and executable:
        policy = "sandbox-required"
    elif source_class in {"external-untrusted", "unknown"}:
        policy = "inspect-only"
    else:
        policy = "trusted"
    requirements = []
    if policy == "sandbox-required":
        requirements = [
            "fresh isolated workspace or stronger process/container boundary",
            "no application or third-party secrets exposed to target code",
            "network disabled or restricted to approved endpoints",
            "evaluator-only assets outside the candidate execution surface",
        ]
    return {
        "status": "pass" if not errors else "fail",
        "source_class": source_class,
        "execution_policy": policy,
        "executable_files": executable,
        "secret_like_files": secret_like,
        "symlinks": symlinks,
        "requirements": requirements,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True)
    ap.add_argument("--source-class", required=True, choices=sorted(SOURCE_CLASSES))
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    report = assess(Path(args.target).resolve(), args.source_class)
    dump_json(report, args.json_out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
