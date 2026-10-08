#!/usr/bin/env python3
"""Repository launcher; the operational-context skill is independently portable."""
import runpy
import sys
from pathlib import Path
sys.dont_write_bytecode=True
runpy.run_path(str(Path(__file__).resolve().parents[1]/'skills/operational-context/scripts/operational.py'),run_name='__main__')
