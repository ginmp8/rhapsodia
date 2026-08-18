#!/usr/bin/env python3
"""Validate that generated-view templates document the renderer's complete output shape."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

CATALOG_TOP = ["kind", "generated", "cycle_id", "cycle_status", "registry_digest", "specs"]
CATALOG_ITEM = [
    "order", "business_priority", "technical_criticality", "execution_lane", "execution_rank",
    "spec_id", "feature_key", "title", "type", "classification",
    "depends_on_features", "depends_on_specs", "status", "feature_version",
]
QUEUE_TOP = ["kind", "generated", "cycle_id", "registry_digest", "entries"]
QUEUE_ITEM = [
    "spec_id", "feature_key", "title", "handoff_status", "downstream_mode", "package_shape",
    "source_candidates", "seed_artifacts", "define_target", "blockers",
]


def keys(value: object) -> list[str]:
    return list(value.keys()) if isinstance(value, dict) else []


def validate_template(path: Path, top: list[str], collection: str, item: list[str]) -> list[str]:
    if yaml is None:
        return ["PyYAML is required"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path.name}: invalid YAML: {exc}"]
    errors: list[str] = []
    if keys(data) != top:
        errors.append(f"{path.name}: top-level keys must be {top}, found {keys(data)}")
    values = data.get(collection) if isinstance(data, dict) else None
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        errors.append(f"{path.name}: `{collection}` must contain exactly one structural example item")
    elif keys(values[0]) != item:
        errors.append(f"{path.name}: item keys must be {item}, found {keys(values[0])}")
    return errors


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0] if argv else ".").resolve()
    errors = []
    errors.extend(validate_template(root / "assets/templates/spec-catalog.yaml.template", CATALOG_TOP, "specs", CATALOG_ITEM))
    errors.extend(validate_template(root / "assets/templates/define-queue.yaml.template", QUEUE_TOP, "entries", QUEUE_ITEM))
    renderer = (root / "scripts/render_registry_views.py").read_text(encoding="utf-8")
    for field in CATALOG_TOP + CATALOG_ITEM + QUEUE_TOP + QUEUE_ITEM:
        if f'"{field}"' not in renderer:
            errors.append(f"render_registry_views.py: missing generated-view field `{field}`")
    if errors:
        print("FAIL generated-view contract")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS generated-view contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
