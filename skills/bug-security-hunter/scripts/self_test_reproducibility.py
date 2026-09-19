#!/usr/bin/env python3
"""Run deterministic self-tests for Bug Security Hunter reproducibility helpers."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def load_validator(root: Path):
    path = root / "scripts" / "validate_review_receipt.py"
    spec = importlib.util.spec_from_file_location("bsh_validate_review_receipt", path)
    if spec is None or spec.loader is None:
        raise SystemExit("FAIL: could not load validate_review_receipt.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validator = load_validator(root)
    valid = json.loads((root / "evals" / "fixtures" / "review-receipt-valid.json").read_text(encoding="utf-8"))
    invalid = json.loads((root / "evals" / "fixtures" / "review-receipt-invalid.json").read_text(encoding="utf-8"))

    valid_errors = validator.validate_receipt(valid)
    if valid_errors:
        print(json.dumps(valid_errors, indent=2, sort_keys=True))
        raise SystemExit("FAIL: valid fixture was rejected")

    invalid_errors = validator.validate_receipt(invalid)
    codes = {item.get("code") for item in invalid_errors}
    required = {
        "safety/sensitive-evidence-unredacted",
        "safety/probable-secret-in-evidence",
        "consistency/nit-cannot-block",
        "verdict/inconsistent",
    }
    missing = sorted(required - codes)
    if missing:
        print(json.dumps(invalid_errors, indent=2, sort_keys=True))
        raise SystemExit("FAIL: invalid fixture missed diagnostics: " + ", ".join(missing))

    print("PASS: reproducibility helper self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
