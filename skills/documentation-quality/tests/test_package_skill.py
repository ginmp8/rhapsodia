from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_skill.py"
SPEC = importlib.util.spec_from_file_location("package_skill", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PackageSkillTests(unittest.TestCase):
    def test_identical_bytes_produce_same_zip_across_mtime_changes(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hashes = []
            for idx, timestamp in enumerate((946684800, 1893456000), start=1):
                candidate = root / f"candidate-{idx}" / "documentation-quality"
                candidate.parent.mkdir(parents=True)
                shutil.copytree(source, candidate)
                for path in candidate.rglob("*"):
                    if path.is_file():
                        os.utime(path, (timestamp, timestamp))
                out = root / f"out-{idx}"
                zip_path = MODULE.package_skill(candidate, out)
                hashes.append(digest(zip_path))
            self.assertEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()
