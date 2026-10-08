#!/usr/bin/env python3
"""Repository convenience entrypoint; the installed skill remains standalone."""
import runpy
from pathlib import Path
import sys
sys.dont_write_bytecode = True
entrypoint = Path(__file__).resolve().parents[1] / 'skills/runtime-harness/scripts/runtime.py'
runpy.run_path(str(entrypoint), run_name='__main__')
