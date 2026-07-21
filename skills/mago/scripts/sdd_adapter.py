#!/usr/bin/env python3
"""Bounded, version-explicit adapters between Mago and SDD file conventions.

The adapter maps canonical planning files and emits a non-authoritative report.
It does not claim compatibility with an unspecified or latest external schema.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

MAPPINGS: dict[str, dict[str, str]] = {
    "spec-kit": {
        "prd.md": "spec.md",
        "technical-design.md": "plan.md",
        "tasks.md": "tasks.md",
    },
    "openspec": {
        "prd.md": "proposal.md",
        "technical-design.md": "design.md",
        "tasks.md": "tasks.md",
        "change-delta.md": "spec-delta.md",
    },
}
SOURCE_ONLY = [
    "board_identity",
    "registry_state",
    "rigor_profile",
    "evidence_provenance",
    "authority_boundaries",
    "artifact_decisions",
    "mutation_state",
    "magia_reconciliation",
]
METADATA_FILE = "mago-adapter-metadata.json"


class AdapterError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_directory(path: Path, label: str) -> None:
    if not path.is_dir() or path.is_symlink():
        raise AdapterError(f"{label} must be a non-symlink directory: {path}")


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise AdapterError(f"{label} must be a regular non-symlink file: {path}")


def safe_output(path: Path, source: Path) -> None:
    resolved = path.resolve()
    try:
        resolved.relative_to(source.resolve())
    except ValueError:
        return
    raise AdapterError("adapter output must be outside the source package/directory")


def prepare_output(path: Path) -> None:
    if path.exists():
        if not path.is_dir() or path.is_symlink():
            raise AdapterError(f"output is not a safe directory: {path}")
        if any(path.iterdir()):
            raise AdapterError(f"output directory must be empty: {path}")
    else:
        path.mkdir(parents=True)


def spec_id_from_package(package: Path) -> str:
    manifest = package / "manifest.yaml"
    if not manifest.is_file():
        return "unknown"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    if isinstance(data, dict) and str(data.get("spec_id", "")).strip():
        return str(data["spec_id"])
    return "unknown"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export_package(
    package: Path,
    output: Path,
    target_format: str,
    source_version: str,
    target_version: str,
) -> dict[str, Any]:
    require_directory(package, "Mago package")
    safe_output(output, package)
    prepare_output(output)
    mapping = MAPPINGS[target_format]
    required = {"prd.md", "tasks.md"}
    missing = sorted(name for name in required if not (package / name).is_file())
    if missing:
        raise AdapterError(f"Mago package is missing required files: {missing}")

    generated: list[str] = []
    checksums: dict[str, dict[str, str]] = {}
    omitted: list[str] = []
    for source_name, target_name in mapping.items():
        source = package / source_name
        if not source.exists():
            omitted.append(source_name)
            continue
        require_file(source, "mapped Mago artifact")
        target = output / target_name
        shutil.copy2(source, target)
        generated.append(target_name)
        checksums[source_name] = {
            "source_sha256": sha256(source),
            "target_file": target_name,
            "target_sha256": sha256(target),
        }

    metadata = {
        "kind": "mago-sdd-adapter-metadata",
        "schema_version": 1,
        "authoritative": False,
        "source_format": "mago",
        "source_version": source_version,
        "target_format": target_format,
        "target_version": target_version,
        "source_spec_id": spec_id_from_package(package),
        "mapping": mapping,
        "checksums": checksums,
        "source_only_concepts": SOURCE_ONLY,
    }
    write_json(output / METADATA_FILE, metadata)
    generated.append(METADATA_FILE)
    return {
        "metadata": metadata,
        "generated_files": generated,
        "mapped_fields": sorted(checksums),
        "omitted_fields": omitted,
    }


def import_package(
    source: Path,
    output: Path,
    source_format: str,
    source_version: str,
    target_version: str,
    require_metadata: bool,
) -> dict[str, Any]:
    require_directory(source, "external adapter source")
    safe_output(output, source)
    prepare_output(output)
    mapping = MAPPINGS[source_format]
    reverse = {target: original for original, target in mapping.items()}
    metadata_path = source / METADATA_FILE
    metadata: dict[str, Any] | None = None
    if metadata_path.exists():
        require_file(metadata_path, "adapter metadata")
        loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or loaded.get("kind") != "mago-sdd-adapter-metadata":
            raise AdapterError("invalid adapter metadata")
        if loaded.get("target_format") != source_format:
            raise AdapterError("adapter metadata target format does not match import format")
        metadata = loaded
    elif require_metadata:
        raise AdapterError(f"{METADATA_FILE} is required for strict round-trip import")

    generated: list[str] = []
    mapped: list[str] = []
    omitted: list[str] = []
    changed_external_files: list[str] = []
    metadata_checksums = metadata.get("checksums", {}) if metadata else {}
    for external_name, mago_name in reverse.items():
        external = source / external_name
        if not external.exists():
            omitted.append(mago_name)
            continue
        require_file(external, "external mapped artifact")
        destination = output / mago_name
        shutil.copy2(external, destination)
        generated.append(mago_name)
        mapped.append(mago_name)
        expected = metadata_checksums.get(mago_name, {}).get("target_sha256") if isinstance(metadata_checksums, dict) else None
        if expected and sha256(external) != expected:
            changed_external_files.append(external_name)

    identity = {
        "kind": "mago-adapter-import-projection",
        "authoritative": False,
        "source_format": source_format,
        "source_version": source_version,
        "target_version": target_version,
        "source_spec_id": metadata.get("source_spec_id", "unknown") if metadata else "unknown",
        "changed_external_files": changed_external_files,
    }
    write_json(output / "import-projection.json", identity)
    generated.append("import-projection.json")
    return {
        "metadata": metadata,
        "generated_files": generated,
        "mapped_fields": mapped,
        "omitted_fields": omitted,
        "changed_external_files": changed_external_files,
        "identity": identity,
    }


def build_report(
    *,
    direction: str,
    source_format: str,
    source_version: str,
    target_format: str,
    target_version: str,
    source_spec_id: str,
    generated_files: list[str],
    mapped_fields: list[str],
    omitted_fields: list[str],
    differences: list[str],
    validations: list[dict[str, str]],
) -> dict[str, Any]:
    losses: list[dict[str, str]] = []
    for concept in SOURCE_ONLY:
        losses.append(
            {
                "source_field": concept,
                "target_field": "metadata-sidecar-only",
                "severity": "medium" if concept in {"authority_boundaries", "evidence_provenance", "mutation_state"} else "low",
                "reason": "The bounded external file convention has no native Mago authority for this concept; the sidecar preserves provenance only.",
            }
        )
    for field in omitted_fields:
        losses.append(
            {
                "source_field": field,
                "target_field": "none",
                "severity": "medium",
                "reason": "The optional source artifact was absent and could not be projected.",
            }
        )
    if direction == "round-trip":
        round_trip_status = "lossless" if not differences and not omitted_fields else "lossy_reported"
    else:
        round_trip_status = "not_run"
    return {
        "kind": "mago-sdd-adapter-report",
        "authoritative": False,
        "direction": direction,
        "source": {"format": source_format, "version": source_version},
        "target": {"format": target_format, "version": target_version},
        "source_spec_id": source_spec_id,
        "generated_files": generated_files,
        "mapped_fields": mapped_fields,
        "omitted_fields": omitted_fields,
        "lossy_mappings": losses,
        "unsupported_target_concepts": [],
        "source_only_concepts": SOURCE_ONLY,
        "round_trip": {"status": round_trip_status, "differences": differences},
        "validation": validations,
    }


def compare_round_trip(package: Path, imported: Path, mapped: list[str]) -> list[str]:
    differences: list[str] = []
    for name in mapped:
        source = package / name
        target = imported / name
        if not source.is_file() or not target.is_file():
            differences.append(f"missing mapped file after round trip: {name}")
        elif sha256(source) != sha256(target):
            differences.append(f"content changed after round trip: {name}")
    return differences


def command_export(args: argparse.Namespace) -> int:
    package = Path(args.package).resolve()
    output = Path(args.output).resolve()
    result = export_package(package, output, args.format, args.source_version, args.target_version)
    report = build_report(
        direction="export",
        source_format="mago",
        source_version=args.source_version,
        target_format=args.format,
        target_version=args.target_version,
        source_spec_id=result["metadata"]["source_spec_id"],
        generated_files=result["generated_files"],
        mapped_fields=result["mapped_fields"],
        omitted_fields=result["omitted_fields"],
        differences=[],
        validations=[{"command": "file mapping and checksum generation", "status": "pass"}],
    )
    write_json(Path(args.report).resolve(), report)
    print(json.dumps({"status": "pass", "generated_files": result["generated_files"]}))
    return 0


def command_import(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    result = import_package(source, output, args.format, args.source_version, args.target_version, args.require_metadata)
    report = build_report(
        direction="import",
        source_format=args.format,
        source_version=args.source_version,
        target_format="mago",
        target_version=args.target_version,
        source_spec_id=result["identity"]["source_spec_id"],
        generated_files=result["generated_files"],
        mapped_fields=result["mapped_fields"],
        omitted_fields=result["omitted_fields"],
        differences=[f"external file changed since export: {name}" for name in result["changed_external_files"]],
        validations=[{"command": "mapped file import and sidecar verification", "status": "pass"}],
    )
    write_json(Path(args.report).resolve(), report)
    print(json.dumps({"status": "pass", "changed_external_files": result["changed_external_files"]}))
    return 0


def command_round_trip(args: argparse.Namespace) -> int:
    package = Path(args.package).resolve()
    output = Path(args.output).resolve()
    safe_output(output, package)
    prepare_output(output)
    with tempfile.TemporaryDirectory(prefix=f"mago-{args.format}-roundtrip-") as tmp:
        root = Path(tmp)
        exported = root / "exported"
        imported = root / "imported"
        export_result = export_package(package, exported, args.format, args.source_version, args.target_version)
        import_result = import_package(exported, imported, args.format, args.target_version, args.source_version, True)
        differences = compare_round_trip(package, imported, import_result["mapped_fields"])
        shutil.copytree(exported, output / "exported")
        shutil.copytree(imported, output / "imported")

    generated = [f"exported/{name}" for name in export_result["generated_files"]]
    generated.extend(f"imported/{name}" for name in import_result["generated_files"])
    report = build_report(
        direction="round-trip",
        source_format="mago",
        source_version=args.source_version,
        target_format=args.format,
        target_version=args.target_version,
        source_spec_id=export_result["metadata"]["source_spec_id"],
        generated_files=generated,
        mapped_fields=import_result["mapped_fields"],
        omitted_fields=sorted(set(export_result["omitted_fields"] + import_result["omitted_fields"])),
        differences=differences,
        validations=[
            {"command": "export checksums", "status": "pass"},
            {"command": "strict metadata import", "status": "pass"},
            {"command": "mapped file sha256 comparison", "status": "pass" if not differences else "fail"},
        ],
    )
    report_path = Path(args.report).resolve()
    write_json(report_path, report)
    if differences:
        print(json.dumps({"status": "fail", "differences": differences}))
        return 1
    print(json.dumps({"status": "pass", "format": args.format, "mapped_files": import_result["mapped_fields"]}))
    return 0


def version_value(value: str) -> str:
    if not value.strip() or value.strip().lower() in {"latest", "current", "unknown"}:
        raise argparse.ArgumentTypeError("versions must be explicit; latest/current/unknown are not accepted")
    return value.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded Mago SDD file-convention adapters.")
    sub = parser.add_subparsers(dest="command", required=True)

    export_parser = sub.add_parser("export")
    export_parser.add_argument("--package", required=True)
    export_parser.add_argument("--format", choices=sorted(MAPPINGS), required=True)
    export_parser.add_argument("--source-version", type=version_value, required=True)
    export_parser.add_argument("--target-version", type=version_value, required=True)
    export_parser.add_argument("--output", required=True)
    export_parser.add_argument("--report", required=True)
    export_parser.set_defaults(handler=command_export)

    import_parser = sub.add_parser("import")
    import_parser.add_argument("--source", required=True)
    import_parser.add_argument("--format", choices=sorted(MAPPINGS), required=True)
    import_parser.add_argument("--source-version", type=version_value, required=True)
    import_parser.add_argument("--target-version", type=version_value, required=True)
    import_parser.add_argument("--output", required=True)
    import_parser.add_argument("--report", required=True)
    import_parser.add_argument("--require-metadata", action="store_true")
    import_parser.set_defaults(handler=command_import)

    roundtrip_parser = sub.add_parser("round-trip")
    roundtrip_parser.add_argument("--package", required=True)
    roundtrip_parser.add_argument("--format", choices=sorted(MAPPINGS), required=True)
    roundtrip_parser.add_argument("--source-version", type=version_value, required=True)
    roundtrip_parser.add_argument("--target-version", type=version_value, required=True)
    roundtrip_parser.add_argument("--output", required=True)
    roundtrip_parser.add_argument("--report", required=True)
    roundtrip_parser.set_defaults(handler=command_round_trip)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (AdapterError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
