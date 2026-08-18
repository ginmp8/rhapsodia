from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from package_skill import validate_archive, zip_skill
from validate_skill_package import validate_package_hygiene


class PackageSecurityTests(unittest.TestCase):
    def hygiene_errors(self, root: Path) -> list[str]:
        errors: list[str] = []
        validate_package_hygiene(root, errors)
        return errors

    def test_rejects_environment_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".env").write_text("TOKEN=example\n", encoding="utf-8")
            self.assertTrue(any("unsafe package path .env" in item for item in self.hygiene_errors(root)))

    def test_rejects_private_key_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "test-key.pem").write_text("not a real key\n", encoding="utf-8")
            self.assertTrue(any("test-key.pem" in item for item in self.hygiene_errors(root)))

    def test_rejects_private_key_content_with_neutral_name(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            marker = "".join(["-----BEGIN ", "PRIVATE KEY", "-----"])
            (root / "notes.txt").write_text(marker + "\nmasked\n", encoding="utf-8")
            self.assertTrue(any("private key material" in item for item in self.hygiene_errors(root)))

    def test_rejects_symlink_even_when_target_is_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as external_raw:
            root = Path(raw)
            external = Path(external_raw) / "outside.txt"
            external.write_text("outside\n", encoding="utf-8")
            (root / "linked.txt").symlink_to(external)
            self.assertTrue(any("symlink" in item for item in self.hygiene_errors(root)))

    def test_zip_builder_fails_closed_on_sensitive_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as output_raw:
            root = Path(raw)
            (root / "SKILL.md").write_text("# test\n", encoding="utf-8")
            (root / ".env.local").write_text("TOKEN=example\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe package path"):
                zip_skill(root, Path(output_raw) / "skill.zip")

    def test_clean_archive_has_single_root_and_passes_validation(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as output_raw:
            root = Path(raw)
            (root / "SKILL.md").write_text("# test\n", encoding="utf-8")
            (root / "references").mkdir()
            (root / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
            output = Path(output_raw) / "skill.zip"
            self.assertEqual(zip_skill(root, output), 2)
            self.assertEqual(validate_archive(output), [])
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(sorted(archive.namelist()), ["nomia/SKILL.md", "nomia/references/guide.md"])

    def test_archive_validator_rejects_traversal_and_secret_entries(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "skill.zip"
            with zipfile.ZipFile(output, "w") as archive:
                archive.writestr("../escape.txt", "x")
                archive.writestr("nomia/.env", "TOKEN=example")
            errors = validate_archive(output)
            self.assertTrue(any("unsafe archive entry" in item for item in errors))
            self.assertTrue(any(".env" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
