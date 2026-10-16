#!/usr/bin/env python3
"""Repository convenience launcher for the installed mandatory-session adapter."""
import runpy
from pathlib import Path
import sys
sys.dont_write_bytecode = True
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'skills/runtime-harness/scripts/agent_session.py'), run_name='__main__')
