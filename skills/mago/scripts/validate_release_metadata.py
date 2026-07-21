#!/usr/bin/env python3
"""Validate Mago distribution metadata and compatibility declarations."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ALLOWED_PRODUCTS = {"chatgpt", "codex", "api", "atlas"}
REQUIRED_RELEASE_FIELDS = {
    "name",
    "version",
    "released_at",
    "package_schema",
    "python",
    "products",
    "compatibility_policy",
    "changelog",
    "breaking_changes",
    "support_boundary",
    "runtime_dependencies",
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    release_path = root / "release.json"
    if not release_path.is_file() or release_path.is_symlink():
        return [f"{release_path}: missing regular release metadata"]
    try:
        data = json.loads(release_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"{release_path}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{release_path}: root must be an object"]
    missing = sorted(REQUIRED_RELEASE_FIELDS - set(data))
    if missing:
        errors.append(f"{release_path}: missing fields {missing}")
    if data.get("name") != "mago":
        errors.append(f"{release_path}: name must be mago")
    version = str(data.get("version", ""))
    if not SEMVER_RE.fullmatch(version):
        errors.append(f"{release_path}: version must be stable semantic versioning")
    released_at = str(data.get("released_at", ""))
    try:
        dt.date.fromisoformat(released_at)
    except ValueError:
        errors.append(f"{release_path}: released_at must be YYYY-MM-DD")
    products = data.get("products")
    if not isinstance(products, list) or not products or any(item not in ALLOWED_PRODUCTS for item in products):
        errors.append(f"{release_path}: products must be a non-empty subset of {sorted(ALLOWED_PRODUCTS)}")
        products = []
    if not isinstance(data.get("breaking_changes"), bool):
        errors.append(f"{release_path}: breaking_changes must be boolean")
    runtime_dependencies = data.get("runtime_dependencies")
    if not isinstance(runtime_dependencies, list) or not runtime_dependencies:
        errors.append(f"{release_path}: runtime_dependencies must be a non-empty list")
    else:
        for index, dependency in enumerate(runtime_dependencies):
            if not isinstance(dependency, dict) or not all(str(dependency.get(key, "")).strip() for key in ("distribution", "import", "specifier")):
                errors.append(f"{release_path}: runtime_dependencies[{index}] needs distribution, import, and specifier")
    for key in ("python", "package_schema", "support_boundary"):
        if not str(data.get(key, "")).strip():
            errors.append(f"{release_path}: {key} must be explicit")

    changelog = root / str(data.get("changelog", ""))
    if not changelog.is_file() or changelog.is_symlink():
        errors.append(f"{release_path}: changelog path is missing: {changelog}")
    else:
        text = changelog.read_text(encoding="utf-8")
        if f"## [{version}] - {released_at}" not in text:
            errors.append(f"{changelog}: missing release heading for {version} on {released_at}")
        if "### Compatibility" not in text:
            errors.append(f"{changelog}: release must state compatibility impact")

    policy = root / str(data.get("compatibility_policy", ""))
    if not policy.is_file() or policy.is_symlink():
        errors.append(f"{release_path}: compatibility policy is missing: {policy}")
    else:
        text = policy.read_text(encoding="utf-8")
        for phrase in ("## Installation", "## Compatibility policy", "## Upgrade and rollback", "## Support boundary"):
            if phrase not in text:
                errors.append(f"{policy}: missing section {phrase}")

    agents = root / "agents" / "openai.yaml"
    if not agents.is_file():
        errors.append(f"{agents}: missing agent compatibility declaration")
    else:
        agents_text = agents.read_text(encoding="utf-8")
        for product in products:
            if not re.search(rf"(?m)^\s*-\s*{re.escape(product)}\s*$", agents_text):
                errors.append(f"{agents}: release product `{product}` is not declared")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Mago release metadata.")
    parser.add_argument("target", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    errors = validate(root)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} release metadata error(s)")
        return 1
    print("OK: release metadata and compatibility policy validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
