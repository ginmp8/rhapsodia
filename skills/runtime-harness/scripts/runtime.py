#!/usr/bin/env python3
"""Portable RhapsodIA runtime entrypoint. Python standard library only."""
import sys
if sys.version_info < (3, 10):
    print('{"status":"error","error":{"code":"PYTHON_VERSION","message":"Python 3.10 or newer is required; no installation was attempted."}}')
    raise SystemExit(2)
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_core.cli import main
if __name__ == "__main__":
    raise SystemExit(main())
