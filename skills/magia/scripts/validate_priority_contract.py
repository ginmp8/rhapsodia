#!/usr/bin/env python3
"""Validate the local Nomia/Mago/Magia priority contract and optional peer copies."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_CONTRACT_ID = "nomia-mago-magia-priority-v2"
EXPECTED_BUSINESS = ["unknown", "low", "medium", "high", "urgent"]
EXPECTED_TECHNICAL = ["low", "normal", "high", "critical"]
EXPECTED_LANES = ["expedite", "fixed_date", "standard", "deferred"]


def load_contract(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("priority contract must be a JSON object")
    return data


def contract_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != "2.0.0":
        errors.append("priority contract schema_version must be 2.0.0")
    if contract.get("contract_id") != EXPECTED_CONTRACT_ID:
        errors.append(f"priority contract_id must be {EXPECTED_CONTRACT_ID}")
    concepts = contract.get("concepts")
    if not isinstance(concepts, dict):
        return errors + ["priority contract concepts must be an object"]
    expected = {
        "business_priority": ("nomia", EXPECTED_BUSINESS),
        "technical_criticality": ("mago", EXPECTED_TECHNICAL),
    }
    for name, (owner, values) in expected.items():
        item = concepts.get(name)
        if not isinstance(item, dict):
            errors.append(f"missing concept {name}")
            continue
        if item.get("owner") != owner:
            errors.append(f"{name}.owner must be {owner}")
        if item.get("values") != values:
            errors.append(f"{name}.values must be {values}")
    sequence = concepts.get("execution_sequence")
    if not isinstance(sequence, dict):
        errors.append("missing concept execution_sequence")
    else:
        if sequence.get("owner") != "mago":
            errors.append("execution_sequence.owner must be mago")
        if sequence.get("lanes") != EXPECTED_LANES:
            errors.append(f"execution_sequence.lanes must be {EXPECTED_LANES}")
    rules = contract.get("rules")
    if not isinstance(rules, list) or len(rules) < 6:
        errors.append("priority contract must contain at least six normative rules")
    compatibility = contract.get("compatibility")
    if not isinstance(compatibility, dict) or compatibility.get("classification") != "breaking-no-legacy":
        errors.append("priority compatibility must be breaking-no-legacy")
    elif compatibility.get("legacy_read_support") is not False:
        errors.append("priority compatibility must disable legacy_read_support")
    elif compatibility.get("rejected_fields") != ["priority", "order_hint"]:
        errors.append("priority compatibility must reject priority and order_hint")
    return errors


def detect_skill(root: Path) -> str:
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return ""
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*['\"]?([a-z0-9-]+)", text)
    return match.group(1).lower() if match else ""


def local_surface_errors(root: Path) -> list[str]:
    errors: list[str] = []
    skill = detect_skill(root)
    if skill == "mago":
        template = (root / "assets/templates/spec-registry-entry.yaml.template").read_text(encoding="utf-8")
        for token in ("business_priority:", "technical_criticality:", "execution_sequence:"):
            if token not in template:
                errors.append(f"Mago registry template missing {token}")
        if re.search(r"(?m)^priority:\s*", template) or re.search(r"(?m)^order_hint:\s*", template):
            errors.append("Mago registry template must not emit unsupported priority/order_hint fields")
        script = (root / "scripts/create_planning_identity.py").read_text(encoding="utf-8")
        for token in ("--technical-criticality", "--execution-lane", "--business-priority-source"):
            if token not in script:
                errors.append(f"Mago identity writer missing {token}")
    elif skill == "magia":
        board = (root / "references/board-contract.md").read_text(encoding="utf-8")
        for token in ("business_priority", "technical_criticality", "execution_sequence"):
            if token not in board:
                errors.append(f"Magia board contract missing {token}")
        code = (root / "scripts/board_contract.py").read_text(encoding="utf-8")
        if "validate_priority_semantics" not in code:
            errors.append("Magia board contract code must validate priority semantics")
        for token in ('("priority", "order_hint")', "unsupported generic field"):
            if token not in code:
                errors.append(f"Magia board contract missing hard rejection token {token}")
    elif skill == "nomia":
        template = (root / "assets/templates/ops.yaml.template").read_text(encoding="utf-8")
        if "business_priority:" not in template:
            errors.append("Nomia ops template must emit business_priority")
        if re.search(r"(?m)^priority:\s*", template):
            errors.append("Nomia ops template must not emit unsupported priority")
        writer = (root / "scripts/write_ops_scaffold.py").read_text(encoding="utf-8")
        if "business_priority:" not in writer:
            errors.append("Nomia scaffold writer must emit business_priority")
    else:
        errors.append(f"unsupported skill package for priority validation: {root.name}")
    return errors


def collect_errors(root: Path, peer_contracts: list[Path] | None = None) -> list[str]:
    errors: list[str] = []
    contract_path = root / "references/priority-contract.json"
    if not contract_path.is_file():
        return ["missing references/priority-contract.json"]
    try:
        contract = load_contract(contract_path)
    except Exception as exc:
        return [f"cannot load priority contract: {exc}"]
    errors.extend(contract_errors(contract))
    errors.extend(local_surface_errors(root))
    local_bytes = contract_path.read_bytes()
    for peer in peer_contracts or []:
        if not peer.is_file():
            errors.append(f"peer priority contract is missing: {peer}")
        elif peer.read_bytes() != local_bytes:
            errors.append(f"peer priority contract differs from local contract: {peer}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--peer-contract", action="append", default=[])
    args = parser.parse_args(argv)
    errors = collect_errors(Path(args.target).resolve(), [Path(p).resolve() for p in args.peer_contract])
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} priority-contract errors")
        return 1
    print("OK: ecosystem priority contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
