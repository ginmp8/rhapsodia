#!/usr/bin/env python3
"""Project an ordered SDD lifecycle without mutation or authority transfer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

OWNER = {
    **dict.fromkeys(("intake", "governance", "roadmap", "status", "reporting", "release"), "nomia"),
    **dict.fromkeys(("planning", "requirements", "design", "tasks", "reconcile"), "mago"),
    **dict.fromkeys(("implementation", "debug", "tests", "validation", "execution-docs"), "magia"),
}
EDGE = {
    ("nomia", "mago"): "nomia_to_mago",
    ("mago", "magia"): "mago_to_magia",
    ("magia", "mago"): "magia_to_mago",
    ("mago", "nomia"): "mago_to_nomia",
    ("magia", "nomia"): "magia_to_nomia",
}
ROLES = {"nomia", "mago", "magia"}


def _owner_phases(intents: list[str]) -> tuple[list[str], list[str]]:
    clean: list[str] = []
    phases: list[str] = []
    for raw in intents:
        intent = str(raw).strip().lower()
        if intent not in OWNER:
            raise ValueError(f"unsupported intent: {intent}")
        clean.append(intent)
        owner = OWNER[intent]
        if not phases or phases[-1] != owner:
            phases.append(owner)
    if not phases:
        raise ValueError("at least one intent is required")
    return clean, phases


def _bridge_required_transitions(phases: list[str]) -> list[str]:
    """Insert only the mandatory planning bridge for forbidden Nomia -> Magia edges."""
    out: list[str] = []
    for owner in phases:
        if out and out[-1] == "nomia" and owner == "magia":
            out.append("mago")
        out.append(owner)
    return out


def route(intents: list[str], current_owner: str | None = None) -> dict[str, object]:
    clean, phases = _owner_phases(intents)

    if current_owner:
        current_owner = str(current_owner).strip().lower()
        if current_owner not in ROLES:
            raise ValueError("invalid current_owner")
        if phases[0] != current_owner:
            phases.insert(0, current_owner)

    owner_sequence = _bridge_required_transitions(phases)
    try:
        handoffs = [EDGE[pair] for pair in zip(owner_sequence, owner_sequence[1:])]
    except KeyError as exc:
        source, target = exc.args[0]
        raise ValueError(f"no authority-safe handoff from {source} to {target}") from None

    return {
        "status": "resolved",
        "authority": "read_only_projection",
        "current_owner": owner_sequence[0],
        "owner_sequence": owner_sequence,
        "handoff_sequence": handoffs,
        "mutation_owner_count": 1,
        "intents": clean,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intent", action="append", required=True, choices=sorted(OWNER))
    parser.add_argument("--current-owner", choices=sorted(ROLES))
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)

    try:
        result, code = route(args.intent, args.current_owner), 0
    except ValueError as exc:
        result, code = {"status": "blocked", "reason": str(exc), "authority": "read_only_projection"}, 2

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(text, encoding="utf-8")
    print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
