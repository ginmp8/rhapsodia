#!/usr/bin/env python3
"""Validate that the canonical identity update preserves the original nomia surface."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_release_contract import load_object, migration_index, sha256_file, validate_release_contract

HEADING_RE = re.compile(r"(?m)^#{1,6}\s+(.+?)\s*$")


def public_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    }


def load_contract(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("contract must be a JSON object")
    return data


def validate(root: Path, contract_path: Path) -> list[str]:
    errors: list[str] = []
    contract = load_contract(contract_path)

    for rel in contract.get("required_files", []):
        if not (root / rel).is_file():
            errors.append(f"original package file is missing: {rel}")

    for rel, required in contract.get("required_headings", {}).items():
        path = root / rel
        if not path.is_file():
            continue
        current = set(HEADING_RE.findall(path.read_text(encoding="utf-8")))
        for heading in required:
            if heading not in current:
                errors.append(f"original heading is missing from {rel}: {heading}")

    replacements = contract.get("allowed_symbol_replacements", {})
    for rel, required in contract.get("required_public_symbols", {}).items():
        path = root / rel
        if not path.is_file():
            continue
        current = public_symbols(path)
        mapping = replacements.get(rel, {}) if isinstance(replacements, dict) else {}
        for symbol in required:
            if symbol in current:
                continue
            replacement = mapping.get(symbol) if isinstance(mapping, dict) else None
            if replacement and replacement in current:
                continue
            errors.append(f"original public symbol is missing from {rel}: {symbol}")

    release_contract_path = root / "tests" / "current-release-contract.json"
    migrations_path = root / "tests" / "protected-file-migrations.json"
    release_errors = validate_release_contract(root, contract_path, release_contract_path, migrations_path)
    errors.extend(release_errors)

    release = load_object(release_contract_path, "current release contract") if release_contract_path.is_file() else {}
    migrations = load_object(migrations_path, "protected-file migrations") if migrations_path.is_file() else {}
    migration_by_path, _ = migration_index(migrations)
    current_protected = dict(release.get("protected_files") or {})

    protected_files = dict(contract.get("protected_files") or {})
    for rel, historical_expected in protected_files.items():
        protected_path = root / str(rel)
        if not protected_path.is_file():
            errors.append(f"protected file is missing: {rel}")
            continue
        actual = sha256_file(protected_path)
        if actual == str(historical_expected):
            continue
        current_expected = current_protected.get(rel)
        migration = migration_by_path.get(rel)
        if current_expected == actual and isinstance(migration, dict):
            if migration.get("from_sha256") == str(historical_expected) and migration.get("to_sha256") == actual:
                continue
        errors.append(
            f"protected file hash changed for {rel} without an accepted migration: "
            f"historical {historical_expected}, current {actual}"
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate preservation of the original nomia functional surface.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="Path to the nomia skill root.")
    parser.add_argument("--contract", help="Optional preservation contract path.")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    contract = Path(args.contract).resolve() if args.contract else root / "tests" / "original-contract.json"
    try:
        errors = validate(root, contract)
    except Exception as exc:
        errors = [str(exc)]

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} preservation errors")
        return 1
    print("OK: original nomia functional surface and protected files are preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
