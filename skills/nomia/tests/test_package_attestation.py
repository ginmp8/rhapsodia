from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from package_skill import (
    PackageResult,
    build_release_attestation,
    sha256_file,
    validate_reproducible_archive,
    zip_skill,
)


class PackageAttestationTests(unittest.TestCase):
    @property
    def skill_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def test_two_package_builds_are_byte_identical_and_attested(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            first = Path(raw) / "first.zip"
            second = Path(raw) / "second.zip"
            count = zip_skill(self.skill_root, first)
            self.assertEqual(zip_skill(self.skill_root, second), count)
            self.assertEqual(sha256_file(first), sha256_file(second))
            self.assertEqual(validate_reproducible_archive(first), [])
            result = PackageResult(str(self.skill_root), str(first), "pass", [], count)
            attestation = build_release_attestation(result)
            self.assertEqual(attestation["version"], "1.9.1")
            self.assertEqual(attestation["archive_sha256"], sha256_file(first))
            self.assertFalse(attestation["behavioral_activation_measured"])
            self.assertIn("agents/openai.yaml", attestation["protected_files"])
            self.assertNotIn("assets/icon.svg", attestation["protected_files"])

    def test_reproducibility_gate_rejects_noncanonical_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bad.zip"
            with zipfile.ZipFile(path, "w") as archive:
                info = zipfile.ZipInfo("nomia/SKILL.md", date_time=(2025, 1, 1, 0, 0, 0))
                info.external_attr = 0o644 << 16
                archive.writestr(info, "# test\n")
            errors = validate_reproducible_archive(path)
            self.assertTrue(any("timestamp is not deterministic" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
