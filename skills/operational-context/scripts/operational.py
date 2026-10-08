#!/usr/bin/env python3
"""Portable explicit CLI. It never executes target commands or makes network calls."""
from __future__ import annotations
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from oc_core.cli import main
if __name__=='__main__':raise SystemExit(main())
