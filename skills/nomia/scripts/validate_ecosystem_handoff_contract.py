#!/usr/bin/env python3
"""Validate the local handoff contract, role declarations, and package integration."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from ecosystem_handoff import CONTRACT_FILE, contract_errors, load_contract, package_role

REQUIRED_SKILL_PHRASES = {
    "mago": ["ecosystem handoff contract", "scripts/ecosystem_handoff.py", "mago_to_magia", "mago_to_nomia"],
    "magia": ["ecosystem handoff contract", "scripts/ecosystem_handoff.py", "magia_to_mago", "magia_to_nomia"],
    "nomia": ["ecosystem handoff contract", "scripts/ecosystem_handoff.py", "nomia_to_mago", "mago_to_nomia", "magia_to_nomia"],
}


def collect_errors(root: Path) -> list[str]:
    root = root.resolve()
    errors = contract_errors(load_contract(root))
    role = package_role(root)
    skill = root / "SKILL.md"
    if not skill.is_file():
        errors.append("missing SKILL.md")
    else:
        text = skill.read_text(encoding="utf-8").lower()
        for phrase in REQUIRED_SKILL_PHRASES[role]:
            if phrase.lower() not in text:
                errors.append(f"SKILL.md missing handoff integration phrase: {phrase}")
    for rel in (CONTRACT_FILE, "references/ecosystem-handoff-contract.md", "scripts/ecosystem_handoff.py"):
        if not (root / rel).is_file():
            errors.append(f"missing ecosystem handoff resource: {rel}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local ecosystem handoff contract integration.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--print-hash", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    errors = collect_errors(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} ecosystem handoff contract error(s)")
        return 1
    contract_path = root / CONTRACT_FILE
    digest = hashlib.sha256(contract_path.read_bytes()).hexdigest()
    print(f"OK: ecosystem handoff contract validated for {package_role(root)}")
    if args.print_hash:
        print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
