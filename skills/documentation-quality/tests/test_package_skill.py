from __future__ import annotations

import hashlib
import importlib.util
import json
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


def canonical_tree_hash(root: Path) -> str:
    rows = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"} for part in rel.parts):
            continue
        if not path.is_file():
            continue
        rows.append({
            "path": rel.as_posix(),
            "type": "file",
            "size": path.stat().st_size,
            "sha256": digest(path),
        })
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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

    def test_package_writes_receipt_bound_to_archive_and_candidate(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "candidate" / "documentation-quality"
            candidate.parent.mkdir(parents=True)
            shutil.copytree(source, candidate)
            out = root / "out"

            zip_path = MODULE.package_skill(candidate, out)
            receipt_path = out / "skill.zip.receipt.json"

            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(1, receipt["receipt_version"])
            self.assertEqual("committed", receipt["stage"])
            self.assertEqual("pass", receipt["status"])
            self.assertEqual(digest(zip_path), receipt["archive_sha256"])
            self.assertEqual(zip_path.stat().st_size, receipt["archive_size_bytes"])
            self.assertRegex(receipt["candidate_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(canonical_tree_hash(candidate), receipt["source_tree_sha256"])
            self.assertEqual([], receipt["recovery_paths"])

    def test_output_directory_inside_target_is_rejected_before_write(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "documentation-quality"
            shutil.copytree(source, candidate)
            out = candidate / "dist"

            with self.assertRaisesRegex(ValueError, "outside the skill folder"):
                MODULE.package_skill(candidate, out)

            self.assertFalse(out.exists())

    def test_validation_failure_preserves_existing_last_good_outputs(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "candidate" / "documentation-quality"
            candidate.parent.mkdir(parents=True)
            shutil.copytree(source, candidate)
            out = root / "out"
            out.mkdir()
            prior_zip = out / "skill.zip"
            prior_receipt = out / "skill.zip.receipt.json"
            prior_zip.write_bytes(b"last-good-zip")
            prior_receipt.write_text('{"stage":"committed"}\n', encoding="utf-8")

            skill_md = candidate / "SKILL.md"
            skill_md.write_text("# invalid\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                MODULE.package_skill(candidate, out)

            self.assertEqual(b"last-good-zip", prior_zip.read_bytes())
            self.assertEqual('{"stage":"committed"}\n', prior_receipt.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
