#!/usr/bin/env python3
"""Validate Nomia-owned governance closure prerequisites from attributed evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from governance_contract import validate_release_state, validate_technical_state
from nomia_utils import atomic_write_text


def validate_closure(data: Any) -> list[str]:
    if not isinstance(data, dict): return ["closure input must be a mapping"]
    errors: list[str] = []
    if data.get("governance_status") != "closed": errors.append("governance_status must be closed")
    if data.get("governance_lifecycle") != "close": errors.append("governance_lifecycle must be close")
    decision = data.get("decision")
    if not isinstance(decision, dict): errors.append("decision must be a mapping")
    else:
        if decision.get("state") != "accepted": errors.append("decision.state must be accepted")
        if decision.get("authority") != "nomia": errors.append("decision.authority must be nomia")
        if not isinstance(decision.get("evidence"), list) or not decision.get("evidence"): errors.append("decision.evidence is required")
    technical = data.get("technical_state")
    if not isinstance(technical, dict): errors.append("technical_state must be a mapping"); technical = {}
    expected = {"planning":"complete","execution":"complete","validation":"passed"}
    for dimension, state in expected.items():
        item = technical.get(dimension)
        errors.extend(validate_technical_state(dimension, item))
        if isinstance(item, dict) and item.get("state") != state: errors.append(f"technical_state.{dimension}.state must be {state}")
    release = data.get("release")
    errors.extend(validate_release_state(release))
    if isinstance(release, dict) and release.get("state") != "closed": errors.append("release.state must be closed")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True)
    parser.add_argument('--json-output')
    args=parser.parse_args(argv)
    data=json.loads(Path(args.input).read_text(encoding='utf-8'))
    errors=validate_closure(data)
    result={'status':'pass' if not errors else 'fail','errors':errors,'authority':'nomia'}
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.json_output: atomic_write_text(Path(args.json_output),text)
    print(text,end='')
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
