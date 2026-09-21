#!/usr/bin/env python3
"""Regression checks for deterministic and recovery-aware skill packaging."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import sys
sys.dont_write_bytecode = True
import tempfile
from pathlib import Path
from unittest import mock


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_packager(root: Path):
    script = root / "scripts" / "package_skill.py"
    spec = importlib.util.spec_from_file_location("karpathy_package_skill", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load package_skill.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_with_mtime(source: Path, destination: Path, timestamp: int) -> Path:
    target = destination / source.name
    shutil.copytree(source, target)
    for path in target.rglob("*"):
        if path.is_file():
            os.utime(path, (timestamp, timestamp))
    return target


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    module = load_packager(root)
    with tempfile.TemporaryDirectory(prefix="karpathy-package-test-") as tmp:
        work = Path(tmp)
        left = copy_with_mtime(root, work / "left", 946684800)
        right = copy_with_mtime(root, work / "right", 1893456000)
        left_zip = work / "left.zip"
        right_zip = work / "right.zip"
        left_info, left_validation = module.build_package(left, left_zip, validate=True)
        right_info, right_validation = module.build_package(right, right_zip, validate=True)
        if left_validation.get("status") != "pass" or right_validation.get("status") != "pass":
            print("FAIL: deterministic package candidates did not validate")
            return 1
        if sha256(left_zip) != sha256(right_zip):
            print("FAIL: identical bytes with different mtimes produced different archives")
            return 1
        if not left_info.get("deterministic_metadata") or not left_info.get("atomic_replace"):
            print("FAIL: package receipt omitted deterministic/atomic guarantees")
            return 1

        last_good = work / "last-good.zip"
        last_good.write_bytes(b"last-good")
        before = last_good.read_bytes()
        with mock.patch.object(module, "write_deterministic_zip", side_effect=RuntimeError("injected failure")):
            try:
                module.build_package(left, last_good, validate=True)
            except RuntimeError:
                pass
            else:
                print("FAIL: injected packaging failure unexpectedly succeeded")
                return 1
        if last_good.read_bytes() != before:
            print("FAIL: failed packaging replaced the last-good archive")
            return 1

    print("PASS: package output is deterministic across mtimes and preserves last-good on failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
