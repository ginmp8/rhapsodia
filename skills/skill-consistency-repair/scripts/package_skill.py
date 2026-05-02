#!/usr/bin/env python3
"""Package this skill folder or another target skill folder as skill.zip after consistency validation."""
from __future__ import annotations

import argparse
from pathlib import Path

from package_target_skill import main as package_main

if __name__ == '__main__':
    raise SystemExit(package_main())
