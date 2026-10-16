#!/usr/bin/env python3
"""Repository convenience launcher; Local Graph Engine owns workspace memory."""
import runpy
from pathlib import Path
import sys
sys.dont_write_bytecode = True
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'skills/local-graph-engine/scripts/workspace_memory.py'), run_name='__main__')
