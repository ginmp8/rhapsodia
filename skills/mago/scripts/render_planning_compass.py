#!/usr/bin/env python3
"""Render a disposable planning-state projection from one canonical Mago package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

CORE_BY_PROFILE = {
    "quick": ["manifest.yaml", "prd.md", "tasks.md", "validation.md"],
    "standard": ["manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"],
    "governed": ["manifest.yaml", "prd.md", "tasks.md", "validation.md", "notes.md"],
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_manifest(package: Path) -> tuple[Path, dict[str, Any]]:
    if yaml is None:
        fail("PyYAML is required")
    manifest_path = package / "manifest.yaml"
    if not manifest_path.is_file():
        fail("missing canonical manifest.yaml")
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(data, dict):
        fail("manifest.yaml must contain a mapping")
    return manifest_path, data


def required_artifacts(manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    profile = str(manifest.get("profile", ""))
    if profile not in CORE_BY_PROFILE:
        fail(f"manifest profile must be one of {sorted(CORE_BY_PROFILE)}, got {profile!r}")
    required = list(CORE_BY_PROFILE[profile])
    conflicts: list[str] = []
    decisions = manifest.get("artifact_decisions", {})
    if decisions is None:
        decisions = {}
    if not isinstance(decisions, dict):
        fail("manifest artifact_decisions must be a mapping")
    for name, raw in decisions.items():
        if not isinstance(name, str) or not isinstance(raw, dict):
            conflicts.append(f"invalid artifact decision entry: {name!r}")
            continue
        status = raw.get("status")
        if status == "required" and name not in required:
            required.append(name)
        elif status not in {"required", "not_applicable"}:
            conflicts.append(f"{name}: invalid decision status {status!r}")
    return required, conflicts


def build_projection(package: Path) -> dict[str, Any]:
    manifest_path, manifest = load_manifest(package)
    required, conflicts = required_artifacts(manifest)
    existing = sorted(path.name for path in package.iterdir() if path.is_file())
    missing = [name for name in required if name not in existing]
    decisions = manifest.get("artifact_decisions", {}) or {}
    unexpected = sorted(
        name for name, raw in decisions.items()
        if isinstance(raw, dict) and raw.get("status") == "not_applicable" and (package / name).exists()
    )
    conflicts.extend(f"{name}: present but declared not_applicable" for name in unexpected)

    mutation = manifest.get("mutation_state", {}) or {}
    if not isinstance(mutation, dict):
        fail("manifest mutation_state must be a mapping")
    mutation_status = mutation.get("status", "unknown")
    if missing:
        stage = "define"
        next_action = f"create or repair required artifacts: {', '.join(missing)}"
    elif mutation_status != "clean":
        stage = "define-recovery"
        next_action = "resume or roll back the recorded mutation before any handoff"
    elif conflicts:
        stage = "analyze"
        next_action = "resolve artifact-decision conflicts and rerun package validation"
    else:
        stage = "analyze"
        next_action = "run profile, traceability, triggered-artifact, mutation, and handoff validators"

    observed_blockers = list(missing) + conflicts
    if mutation_status != "clean":
        observed_blockers.append(f"mutation_state.status={mutation_status}")

    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    return {
        "kind": "mago-planning-compass",
        "authoritative": False,
        "runtime_evidence": "not_observed",
        "delivery_governance": "not_observed",
        "package": str(package),
        "source_manifest": str(manifest_path),
        "source_manifest_sha256": digest,
        "identity": {
            "cycle_id": manifest.get("cycle_id"),
            "spec_id": manifest.get("spec_id"),
            "feature_key": manifest.get("feature_key"),
        },
        "profile": manifest.get("profile"),
        "manifest_phase": manifest.get("phase"),
        "manifest_status": manifest.get("status"),
        "public_lifecycle_stage": stage,
        "artifacts": {
            "required": required,
            "existing": existing,
            "missing": missing,
            "decision_conflicts": conflicts,
        },
        "mutation_state": mutation,
        "gates": [
            {"name": "identity_fields_present", "status": "pass" if all(manifest.get(k) for k in ("cycle_id", "spec_id", "feature_key")) else "fail"},
            {"name": "artifact_completeness", "status": "pass" if not missing else "fail"},
            {"name": "artifact_decision_consistency", "status": "pass" if not conflicts else "fail"},
            {"name": "mutation_state_clean", "status": "pass" if mutation_status == "clean" else "fail"},
            {"name": "profile_validators", "status": "not_observed"},
            {"name": "traceability_and_handoff", "status": "not_observed"},
        ],
        "blockers": observed_blockers,
        "next_owner": "mago",
        "next_action": next_action,
        "handoff_boundary": "Magia receives only validated intended work; Nomia receives only governance consequences.",
    }


def render_markdown(data: dict[str, Any]) -> str:
    identity = data["identity"]
    artifacts = data["artifacts"]
    lines = [
        "# Mago Planning Compass",
        "",
        "- Authoritative: false",
        f"- Spec: `{identity.get('spec_id')}`",
        f"- Cycle: `{identity.get('cycle_id')}`",
        f"- Profile: `{data.get('profile')}`",
        f"- Public lifecycle stage: `{data.get('public_lifecycle_stage')}`",
        f"- Mutation state: `{data.get('mutation_state', {}).get('status', 'unknown')}`",
        "",
        "## Artifact State",
        "",
        f"- Required: {', '.join(artifacts['required']) or 'none'}",
        f"- Missing: {', '.join(artifacts['missing']) or 'none'}",
        f"- Decision conflicts: {', '.join(artifacts['decision_conflicts']) or 'none'}",
        "",
        "## Gates",
        "",
    ]
    lines.extend(f"- `{gate['name']}`: `{gate['status']}`" for gate in data["gates"])
    lines.extend([
        "",
        "## Next Action",
        "",
        data["next_action"],
        "",
        "## Evidence Limits",
        "",
        "Runtime evidence and delivery governance were not observed. File presence is not validation success.",
        "",
    ])
    return "\n".join(lines)


def write_output(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        fail(f"output exists; pass --force to replace: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="Canonical Mago spec package")
    parser.add_argument("--output", required=True, help="External output path")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    package = Path(args.package).resolve()
    if not package.is_dir():
        raise SystemExit(f"package directory not found: {package}")
    output = Path(args.output).resolve()
    if output == package or package in output.parents:
        raise SystemExit("output must be outside the canonical package directory")
    try:
        data = build_projection(package)
        text = json.dumps(data, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_markdown(data)
        write_output(output, text, args.force)
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"status: {'pass' if not data['blockers'] else 'blocked'}")
    print(f"stage: {data['public_lifecycle_stage']}")
    print(f"output: {output}")
    return 0 if not data["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
