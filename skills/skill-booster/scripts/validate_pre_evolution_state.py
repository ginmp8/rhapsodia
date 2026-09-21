#!/usr/bin/env python3
"""Compatibility shim for validate_optimization_state.py.

Canonical callers should use validate_optimization_state.py. This file is retained so
existing local automation does not break solely because the core terminology became
strategy-neutral.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TARGET = Path(__file__).with_name("validate_optimization_state.py")
_SPEC = importlib.util.spec_from_file_location("_skill_booster_validate_optimization_state", _TARGET)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load compatibility target: {_TARGET}")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

for _name in dir(_MOD):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_MOD, _name)


if __name__ == "__main__":
    sys.exit(_MOD.main())
