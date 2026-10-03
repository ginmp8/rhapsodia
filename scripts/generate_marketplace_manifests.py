#!/usr/bin/env python3
"""Generate deterministic host marketplace/plugin manifests from marketplace/catalog.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "marketplace" / "catalog.json"
STALE_SOURCE_PATHS = (
    ROOT / "plugin.json",
    ROOT / "com.github.copilot",
)


def load_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    if catalog.get("schema_version") != 1:
        raise ValueError("unsupported marketplace catalog schema_version")
    return catalog


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def render_portable_manifest(catalog: dict[str, Any]) -> dict[str, Any]:
    market = catalog["marketplace"]
    plugin = catalog["plugin"]
    owner = market["owner"]
    description = plugin["description"]
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": plugin["name"],
        "version": plugin["version"],
        "description": description,
        "author": plugin["author"],
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "license": plugin["license"],
        "keywords": plugin["keywords"],
        "extensions": {
            "com.openai": {
                "interface": {
                    "displayName": market["display_name"],
                    "shortDescription": "Portable engineering and agent-workflow skills",
                    "longDescription": description,
                    "developerName": owner["name"],
                    "category": "Productivity",
                    "websiteURL": plugin["homepage"],
                }
            }
        },
    }


def render_manifests(catalog: dict[str, Any]) -> dict[Path, bytes]:
    market = catalog["marketplace"]
    plugin = catalog["plugin"]
    description = plugin["description"]
    owner = market["owner"]

    common_marketplace_plugin = {
        "name": plugin["name"],
        "description": description,
        "version": plugin["version"],
        "source": ".",
        "author": plugin["author"],
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "license": plugin["license"],
        "keywords": plugin["keywords"],
        "category": "development",
    }

    github = {
        "name": market["name"],
        "owner": owner,
        "metadata": {
            "description": market["description"],
            "version": market["version"],
        },
        "plugins": [common_marketplace_plugin],
    }
    github_plugin = {
        "name": plugin["name"],
        "version": plugin["version"],
        "description": description,
        "author": plugin["author"],
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "license": plugin["license"],
        "keywords": plugin["keywords"],
        "agents": "agents/",
        "skills": "skills/",
    }

    cursor = {
        "name": market["name"],
        "owner": owner,
        "metadata": {
            "description": market["description"],
            "version": market["version"],
        },
        "plugins": [common_marketplace_plugin],
    }
    cursor_plugin = {
        "name": plugin["name"],
        "version": plugin["version"],
        "description": description,
        "author": plugin["author"],
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "license": plugin["license"],
        "keywords": plugin["keywords"],
        "agents": "agents/",
        "skills": "skills/",
    }

    claude_plugin = {
        "name": plugin["name"],
        "version": plugin["version"],
        "description": description,
        "author": plugin["author"],
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "license": plugin["license"],
        "keywords": plugin["keywords"],
    }
    claude_marketplace_plugin = dict(common_marketplace_plugin)
    claude_marketplace_plugin["source"] = "./"
    claude = {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": market["name"],
        "version": market["version"],
        "description": market["description"],
        "owner": owner,
        "plugins": [claude_marketplace_plugin],
    }

    codex_plugin = {
        "name": plugin["name"],
        "version": plugin["version"],
        "description": description,
        "author": plugin["author"],
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "license": plugin["license"],
        "keywords": plugin["keywords"],
        "skills": "./skills/",
        "interface": {
            "displayName": market["display_name"],
            "shortDescription": "Portable engineering and agent-workflow skills",
            "longDescription": description,
            "developerName": owner["name"],
            "category": "Productivity",
        },
    }
    openai = {
        "name": market["name"],
        "interface": {"displayName": market["display_name"]},
        "plugins": [
            {
                "name": plugin["name"],
                "source": {"source": "url", "url": plugin["repository_git"]},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_USE",
                },
                "category": "Productivity",
            }
        ],
    }

    return {
        ROOT / ".github" / "plugin" / "marketplace.json": json_bytes(github),
        ROOT / ".github" / "plugin" / "plugin.json": json_bytes(github_plugin),
        ROOT / ".cursor-plugin" / "marketplace.json": json_bytes(cursor),
        ROOT / ".cursor-plugin" / "plugin.json": json_bytes(cursor_plugin),
        ROOT / ".claude-plugin" / "plugin.json": json_bytes(claude_plugin),
        ROOT / ".claude-plugin" / "marketplace.json": json_bytes(claude),
        ROOT / ".codex-plugin" / "plugin.json": json_bytes(codex_plugin),
        ROOT / ".agents" / "plugins" / "marketplace.json": json_bytes(openai),
    }


def stale_source_errors() -> list[str]:
    errors: list[str] = []
    if (ROOT / "plugin.json").exists():
        errors.append("unexpected portable root manifest: plugin.json")
    if (ROOT / "com.github.copilot").exists():
        errors.append("unexpected generated Copilot adapter: com.github.copilot/")
    return errors


def check_outputs(outputs: dict[Path, bytes]) -> list[str]:
    errors = stale_source_errors()
    for path, expected in outputs.items():
        if not path.is_file():
            errors.append(f"missing: {path.relative_to(ROOT)}")
            continue
        if path.read_bytes() != expected:
            errors.append(f"out-of-sync: {path.relative_to(ROOT)}")
    return errors


def remove_stale_source_paths() -> None:
    root_manifest = ROOT / "plugin.json"
    if root_manifest.exists():
        root_manifest.unlink()

    copilot_extension = ROOT / "com.github.copilot"
    if copilot_extension.exists():
        import shutil

        shutil.rmtree(copilot_extension)


def write_outputs(outputs: dict[Path, bytes]) -> None:
    remove_stale_source_paths()
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated files without modifying the repository",
    )
    args = parser.parse_args()

    try:
        catalog = load_catalog()
        outputs = render_manifests(catalog)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"marketplace generation failed: {exc}", file=sys.stderr)
        return 2

    if args.check:
        errors = check_outputs(outputs)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("marketplace manifests are in sync; canonical agents are not duplicated")
        return 0

    write_outputs(outputs)
    print("generated host marketplace manifests from canonical skills/ and agents/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
