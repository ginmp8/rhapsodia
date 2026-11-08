#!/usr/bin/env python3
"""Backward-compatible entry point for attributed skills; use package_skill.py for all 76."""
from package_skill import build, main

if __name__ == "__main__":
    raise SystemExit(main())
