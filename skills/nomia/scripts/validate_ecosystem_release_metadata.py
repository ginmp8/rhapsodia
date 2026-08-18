#!/usr/bin/env python3
"""Validate release metadata shared by the coordinated SDD skill packages."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ALLOWED_SKILLS = {"mago", "magia", "nomia"}
ALLOWED_PRODUCTS = {"chatgpt", "codex", "api", "atlas"}
REQUIRED_FIELDS = {
    "name", "version", "ecosystem_release", "released_at", "package_schema",
    "python", "products", "compatibility_policy", "ecosystem_contract",
    "routing_contract", "provenance_contract", "development_requirements",
    "changelog", "breaking_changes", "support_boundary", "runtime_dependencies",
}


def _load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    return data


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    release_path = root / "release.json"
    version_path = root / "VERSION"
    if not release_path.is_file() or release_path.is_symlink():
        return {"status": "fail", "errors": ["release.json must be a regular file"]}
    if not version_path.is_file() or version_path.is_symlink():
        return {"status": "fail", "errors": ["VERSION must be a regular file"]}
    try:
        data = _load_object(release_path)
    except Exception as exc:  # noqa: BLE001
        return {"status": "fail", "errors": [f"release.json is invalid: {exc}"]}

    missing = sorted(REQUIRED_FIELDS - set(data))
    if missing:
        errors.append(f"release.json missing fields: {missing}")
    name = str(data.get("name", ""))
    if name not in ALLOWED_SKILLS:
        errors.append(f"release name `{name}` must be one of {sorted(ALLOWED_SKILLS)}")
    version = version_path.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        errors.append(f"VERSION must be stable semver, got `{version}`")
    if data.get("version") != version or data.get("ecosystem_release") != version:
        errors.append("release version, ecosystem_release, and VERSION must be identical")
    try:
        dt.date.fromisoformat(str(data.get("released_at", "")))
    except ValueError:
        errors.append("released_at must be YYYY-MM-DD")
    if not isinstance(data.get("breaking_changes"), bool):
        errors.append("breaking_changes must be boolean")
    products = data.get("products")
    if not isinstance(products, list) or not products or any(item not in ALLOWED_PRODUCTS for item in products):
        errors.append(f"products must be a non-empty subset of {sorted(ALLOWED_PRODUCTS)}")
    dependencies = data.get("runtime_dependencies")
    if not isinstance(dependencies, list):
        errors.append("runtime_dependencies must be a list, including an empty list when none are required")
    else:
        for index, item in enumerate(dependencies):
            if not isinstance(item, dict) or not all(str(item.get(key, "")).strip() for key in ("distribution", "import", "specifier")):
                errors.append(f"runtime_dependencies[{index}] needs distribution, import, and specifier")
    for key in ("python", "package_schema", "support_boundary"):
        if not str(data.get(key, "")).strip():
            errors.append(f"{key} must be explicit")
    for key in ("compatibility_policy", "ecosystem_contract", "routing_contract", "provenance_contract", "development_requirements", "changelog"):
        rel = data.get(key)
        path = root / str(rel or "")
        if not isinstance(rel, str) or not rel or not path.is_file() or path.is_symlink():
            errors.append(f"{key} must reference a regular package file: {rel}")
    changelog = root / str(data.get("changelog", ""))
    if changelog.is_file():
        text = changelog.read_text(encoding="utf-8")
        released_at = str(data.get("released_at", ""))
        if not re.search(rf"(?m)^##\s+(?:\[{re.escape(version)}\]|{re.escape(version)})\s+-\s+{re.escape(released_at)}\s*$", text):
            errors.append(f"changelog has no release heading for {version} on {released_at}")
        release_block = text.split("\n## ", 2)[1] if "\n## " in text else text
        if "Compatibility" not in release_block and "compatib" not in release_block.lower():
            errors.append("current changelog release must state compatibility impact")
    agents = root / "agents/openai.yaml"
    if not agents.is_file() or agents.is_symlink():
        errors.append("agents/openai.yaml must be a regular file")
    else:
        agent_text = agents.read_text(encoding="utf-8")
        for product in products if isinstance(products, list) else []:
            if not re.search(rf"(?m)^\s*-\s*{re.escape(product)}\s*$", agent_text):
                errors.append(f"agents/openai.yaml does not declare product `{product}`")
    return {"status": "pass" if not errors else "fail", "skill": name, "version": version, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate coordinated SDD release metadata.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate(Path(args.target))
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for error in result["errors"]:
        print(f"ERROR: {error}")
    print(f"status: {result['status']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
