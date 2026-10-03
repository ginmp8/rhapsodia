"""Resolve this standalone package's script imports before pytest collection.

Do not depend on another test module running first or on caller PYTHONPATH.
"""
from pathlib import Path
import sys

SCRIPTS = str(Path(__file__).resolve().parents[1] / 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
