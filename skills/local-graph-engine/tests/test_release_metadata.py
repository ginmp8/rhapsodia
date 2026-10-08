#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
GRAPH_ENGINE = ROOT / "scripts" / "graph_engine.py"
GRAPH = ROOT / "scripts" / "graph.py"


def load_graph_engine():
    spec = importlib.util.spec_from_file_location("graph_engine_release_test", GRAPH_ENGINE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseMetadataTests(unittest.TestCase):
    def test_package_version_matches_version_file(self) -> None:
        module = load_graph_engine()
        self.assertEqual(module.PACKAGE_VERSION, VERSION)

    def test_doctor_reports_package_version(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "graph.db"
            proc = subprocess.run(
                [sys.executable, str(GRAPH), "--db", str(db), "doctor"],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["version"], VERSION)


if __name__ == "__main__":
    unittest.main()
