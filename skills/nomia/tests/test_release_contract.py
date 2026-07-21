from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_contract_preservation import validate as validate_preservation
from validate_release_contract import validate_release_contract


class ReleaseContractTests(unittest.TestCase):
    @property
    def skill_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def copy_contract_fixture(self, destination: Path) -> Path:
        root = destination / "nomia"
        for rel in (
            "VERSION",
            "assets/icon.svg",
            "agents/openai.yaml",
            "tests/original-contract.json",
            "tests/current-release-contract.json",
            "tests/protected-file-migrations.json",
        ):
            source = self.skill_root / rel
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        return root

    def test_current_release_contract_passes(self) -> None:
        self.assertEqual(validate_release_contract(self.skill_root), [])
        self.assertEqual(
            validate_preservation(self.skill_root, self.skill_root / "tests" / "original-contract.json"),
            [],
        )

    def test_missing_migration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            (root / "tests" / "protected-file-migrations.json").write_text(
                json.dumps({"schema_version": 1, "skill": "nomia", "migrations": []}) + "\n",
                encoding="utf-8",
            )
            errors = validate_release_contract(root)
            self.assertTrue(any("migration is required" in error for error in errors))

    def test_tampered_icon_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            (root / "assets" / "icon.svg").write_text("<svg/>\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("current protected file hash changed" in error for error in errors))

    def test_migration_source_hash_must_match_historical_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            path = root / "tests" / "protected-file-migrations.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["migrations"][0]["from_sha256"] = "0" * 64
            path.write_text(json.dumps(data) + "\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("from_sha256" in error for error in errors))

    def test_historical_protected_file_migration_remains_valid_in_later_release(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            migration = json.loads((root / "tests" / "protected-file-migrations.json").read_text(encoding="utf-8"))
            self.assertEqual(migration["migrations"][0]["version"], "2.2.0")
            self.assertEqual((root / "VERSION").read_text(encoding="utf-8").strip(), "2.3.0")
            self.assertEqual(validate_release_contract(root), [])

    def test_future_protected_file_migration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            path = root / "tests" / "protected-file-migrations.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["migrations"][0]["version"] = "9.9.9"
            path.write_text(json.dumps(data) + "\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("newer than VERSION" in error for error in errors))

    def test_release_version_must_match_version_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            (root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("does not match VERSION" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
