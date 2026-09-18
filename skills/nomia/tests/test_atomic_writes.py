import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from nomia_utils import atomic_write_text
from write_ops_scaffold import main as write_ops_main


class AtomicWriteTests(unittest.TestCase):
    def test_atomic_write_replaces_complete_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact.md"
            path.write_text("old", encoding="utf-8")
            atomic_write_text(path, "new")
            self.assertEqual(path.read_text(encoding="utf-8"), "new")
            self.assertEqual(list(Path(tmp).glob(".*.tmp")), [])

    def test_scaffold_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            with contextlib.redirect_stdout(io.StringIO()):
                rc = write_ops_main([
                    str(path), "--spec-id", "spec-2026-07-20-demo",
                    "--spec-id-provenance", "registry/spec-2026-07-20-demo.yaml", "--dry-run"
                ])
            self.assertEqual(rc, 0)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
