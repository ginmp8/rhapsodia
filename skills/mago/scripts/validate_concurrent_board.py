#!/usr/bin/env python3
"""Validate a canonical MAGO cycle board and its concurrent registry model."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from concurrent_model import dependency_errors, load_cycle, load_registry, validate_cycle, validate_record
from mago_utils import SPEC_ID_RE

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


@dataclass
class Report:
    status: str = "pass"
    model: str = "canonical"
    registry_records: int = 0
    packages: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.status = "fail"
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def validate_manifest_identity(package: Path, cycle_id: str, registry: dict[str, object], report: Report) -> None:
    manifest = package / "manifest.yaml"
    if not manifest.exists():
        if (package / "tasks.md").exists():
            report.error(f"{package}: package with tasks.md is missing manifest.yaml")
        return
    if yaml is None:
        report.error("PyYAML is required to validate package manifest identity")
        return
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        report.error(f"{manifest}: invalid YAML: {exc}")
        return
    if not isinstance(data, dict):
        report.error(f"{manifest}: top-level value must be a mapping")
        return
    expected = {
        "spec_id": registry.get("spec_id"),
        "cycle_id": cycle_id,
        "feature_key": registry.get("feature_key"),
        "profile": registry.get("profile"),
    }
    for key, value in expected.items():
        if data.get(key) != value:
            report.error(f"{manifest}: `{key}` must match registry value `{value}`")


def validate(board_root: Path) -> Report:
    board_root = board_root.resolve()
    report = Report()
    if not (board_root / "cycle.yaml").is_file():
        report.error(f"{board_root}: missing canonical cycle.yaml")
        return report
    try:
        cycle = load_cycle(board_root)
    except Exception as exc:
        report.error(str(exc))
        return report
    for error in validate_cycle(board_root, cycle):
        report.error(error)
    records = load_registry(board_root)
    report.registry_records = len(records)
    by_id = {}
    for record in records:
        by_id[record.spec_id] = record
        for error in validate_record(board_root, cycle, record):
            report.error(error)
    for error in dependency_errors(records):
        report.error(error)

    for forbidden in ("spec-catalog.yaml", "define-queue.yaml"):
        if (board_root / forbidden).exists():
            report.error(f"{board_root / forbidden}: aggregate files are noncanonical; render them outside BOARD_ROOT")

    specs_root = board_root / "specs"
    if specs_root.is_dir():
        for package in sorted(path for path in specs_root.iterdir() if path.is_dir()):
            report.packages += 1
            if not SPEC_ID_RE.fullmatch(package.name):
                report.error(f"{package}: package directory must use canonical spec-YYYY-MM-DD-feature-key spec_id")
                continue
            record = by_id.get(package.name)
            if record is None:
                report.error(f"{package}: package has no matching registry record")
                continue
            validate_manifest_identity(package, str(cycle.get("cycle_id", "")), record.data, report)
            from validate_package import validate_package

            errors, warnings = validate_package(package)
            for error in errors:
                report.error(error)
            for warning in warnings:
                report.warning(warning)

    for spec_id, record in by_id.items():
        package = specs_root / spec_id
        handoff = record.data.get("handoff") or {}
        if isinstance(handoff, dict) and handoff.get("status") == "ready_for_prepare_define" and package.exists():
            report.warning(f"{record.path}: handoff is still ready_for_prepare_define although package exists")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a canonical concurrent MAGO board.")
    parser.add_argument("board_root")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    report = validate(Path(args.board_root))
    payload = asdict(report)
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    for error in report.errors:
        print(f"ERROR: {error}")
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    if report.status == "fail":
        print(f"FAILED: {len(report.errors)} errors, {len(report.warnings)} warnings")
        return 1
    print(f"OK: canonical board validated ({report.registry_records} registry records, {report.packages} packages, {len(report.warnings)} warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
