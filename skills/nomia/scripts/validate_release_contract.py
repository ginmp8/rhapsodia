#!/usr/bin/env python3
"""Validate the current Nomia release contract and explicit protected-file migrations."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path, label: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def migration_index(data: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("protected-file migrations schema_version must be 1")
    raw = data.get("migrations")
    if not isinstance(raw, list):
        return {}, errors + ["protected-file migrations must contain a migrations list"]
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            errors.append(f"migration {index} must be an object")
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"migration {index} path is required")
            continue
        if path in result:
            errors.append(f"duplicate protected-file migration: {path}")
            continue
        result[path] = item
    return result, errors


def validate_release_contract(
    root: Path,
    original_contract_path: Path | None = None,
    release_contract_path: Path | None = None,
    migrations_path: Path | None = None,
) -> list[str]:
    root = root.resolve()
    original_path = (original_contract_path or root / "tests" / "original-contract.json").resolve()
    release_path = (release_contract_path or root / "tests" / "current-release-contract.json").resolve()
    migration_path = (migrations_path or root / "tests" / "protected-file-migrations.json").resolve()
    errors: list[str] = []

    try:
        original = load_object(original_path, "original contract")
        release = load_object(release_path, "current release contract")
        migrations = load_object(migration_path, "protected-file migrations")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]

    if release.get("schema_version") != 1:
        errors.append("current release contract schema_version must be 1")
    if release.get("skill") != "nomia":
        errors.append("current release contract skill must be nomia")
    version_path = root / "VERSION"
    if not version_path.is_file():
        errors.append("VERSION is missing")
        current_version = None
    else:
        current_version = version_path.read_text(encoding="utf-8").strip()
        if release.get("version") != current_version:
            errors.append(f"release contract version {release.get('version')} does not match VERSION {current_version}")
    if release.get("package_root") != "nomia":
        errors.append("current release contract package_root must be nomia")
    if release.get("source_contract") != "tests/original-contract.json":
        errors.append("current release contract source_contract must be tests/original-contract.json")
    expected_original_hash = release.get("original_contract_sha256")
    actual_original_hash = sha256_file(original_path)
    if expected_original_hash != actual_original_hash:
        errors.append(
            "current release contract does not match the immutable original contract: "
            f"expected {expected_original_hash}, got {actual_original_hash}"
        )

    historical = dict(original.get("protected_files") or {})
    current = release.get("protected_files")
    if not isinstance(current, dict) or not current:
        errors.append("current release contract protected_files must be a non-empty object")
        current = {}
    migration_by_path, migration_errors = migration_index(migrations)
    errors.extend(migration_errors)
    if migrations.get("skill") != "nomia":
        errors.append("protected-file migrations skill must be nomia")

    known_paths = set(historical) | set(current)
    for path in sorted(known_paths):
        current_expected = current.get(path)
        protected_path = root / path
        if not protected_path.is_file():
            errors.append(f"protected file is missing: {path}")
            continue
        actual = sha256_file(protected_path)
        if not isinstance(current_expected, str) or len(current_expected) != 64:
            errors.append(f"current protected hash is invalid for {path}")
        elif actual != current_expected:
            errors.append(f"current protected file hash changed for {path}: expected {current_expected}, got {actual}")

        historical_expected = historical.get(path)
        changed = historical_expected is not None and current_expected != historical_expected
        migration = migration_by_path.get(path)
        if changed:
            if migration is None:
                errors.append(f"protected-file migration is required for {path}")
                continue
            if migration.get("from_sha256") != historical_expected:
                errors.append(f"migration from_sha256 does not match historical contract for {path}")
            if migration.get("to_sha256") != current_expected:
                errors.append(f"migration to_sha256 does not match current release contract for {path}")
            if migration.get("version") != current_version:
                errors.append(f"migration version does not match VERSION for {path}")
            if not isinstance(migration.get("authority"), str) or len(migration["authority"].strip()) < 8:
                errors.append(f"migration authority is required for {path}")
            if not isinstance(migration.get("reason"), str) or len(migration["reason"].strip()) < 40:
                errors.append(f"migration reason is too short for {path}")
            try:
                date.fromisoformat(str(migration.get("recorded_at")))
            except ValueError:
                errors.append(f"migration recorded_at must be ISO date for {path}")
        elif migration is not None:
            errors.append(f"unexpected migration for unchanged protected file: {path}")

    for path in sorted(set(migration_by_path) - known_paths):
        errors.append(f"migration references unknown protected file: {path}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Nomia current-release protected-file integrity.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--original-contract")
    parser.add_argument("--release-contract")
    parser.add_argument("--migrations")
    args = parser.parse_args(argv)
    errors = validate_release_contract(
        Path(args.target),
        Path(args.original_contract) if args.original_contract else None,
        Path(args.release_contract) if args.release_contract else None,
        Path(args.migrations) if args.migrations else None,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} release-contract errors")
        return 1
    print("OK: current release contract and protected-file migrations are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
