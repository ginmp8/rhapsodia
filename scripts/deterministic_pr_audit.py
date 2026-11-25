#!/usr/bin/env python3
"""Convenience entrypoint for the bundled Deterministic PR Audit CLI."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "skills" / "deterministic-pr-audit" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
runpy.run_path(str(SCRIPT_DIR / "pr_audit.py"), run_name="__main__")
