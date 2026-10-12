"""Exclusive, side-effect-bounded JSON/text output for RE skill CLIs."""
from __future__ import annotations
import os
from pathlib import Path


def write_exclusive(destination:Path,content:str,protected=()):
    if any(destination.resolve()==Path(src).resolve() for src in protected):
        raise ValueError('output aliases an input')
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive create does not follow an existing symlink or clobber previous evidence.
    with destination.open('x',encoding='utf-8') as fp:
        fp.write(content)
        fp.flush()
        os.fsync(fp.fileno())
