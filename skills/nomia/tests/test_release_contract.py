from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_contract_preservation import validate as validate_preservation
from validate_release_contract import sha256_file, validate_release_contract


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

    def configure_agent_migration(self, root: Path, version: str = "1.2.0") -> None:
        protected_path = root / "agents" / "openai.yaml"
        protected_path.write_text(
            protected_path.read_text(encoding="utf-8") + "\n# migrated test fixture\n",
            encoding="utf-8",
        )
        current_hash = sha256_file(protected_path)

        release_path = root / "tests" / "current-release-contract.json"
        release = json.loads(release_path.read_text(encoding="utf-8"))
        release["protected_files"]["agents/openai.yaml"] = current_hash
        release_path.write_text(json.dumps(release) + "\n", encoding="utf-8")

        original = json.loads((root / "tests" / "original-contract.json").read_text(encoding="utf-8"))
        historical_hash = original["protected_files"]["agents/openai.yaml"]
        migrations = {
            "schema_version": 1,
            "skill": "nomia",
            "migrations": [
                {
                    "authority": "unit-test-authorized-migration",
                    "from_sha256": historical_hash,
                    "path": "agents/openai.yaml",
                    "reason": "Synthetic protected-file migration used to verify fail-closed release validation behavior.",
                    "recorded_at": "2026-07-21",
                    "to_sha256": current_hash,
                    "version": version,
                }
            ],
        }
        (root / "tests" / "protected-file-migrations.json").write_text(
            json.dumps(migrations) + "\n",
            encoding="utf-8",
        )

    def test_current_release_contract_passes(self) -> None:
        self.assertEqual(validate_release_contract(self.skill_root), [])
        self.assertEqual(
            validate_preservation(self.skill_root, self.skill_root / "tests" / "original-contract.json"),
            [],
        )

    def test_current_release_uses_a_continuous_multi_step_migration_chain(self) -> None:
        migrations = json.loads((self.skill_root / "tests" / "protected-file-migrations.json").read_text(encoding="utf-8"))
        chain = [item for item in migrations["migrations"] if item["path"] == "agents/openai.yaml"]
        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[0]["to_sha256"], chain[1]["from_sha256"])
        self.assertEqual(validate_release_contract(self.skill_root), [])

    def test_discontinuous_multi_step_migration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            path = root / "tests" / "protected-file-migrations.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["migrations"][1]["from_sha256"] = "0" * 64
            path.write_text(json.dumps(data) + "\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("does not continue" in error for error in errors))

    def test_missing_migration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            self.configure_agent_migration(root)
            (root / "tests" / "protected-file-migrations.json").write_text(
                json.dumps({"schema_version": 1, "skill": "nomia", "migrations": []}) + "\n",
                encoding="utf-8",
            )
            errors = validate_release_contract(root)
            self.assertTrue(any("migration is required" in error for error in errors))

    def test_tampered_protected_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            (root / "agents" / "openai.yaml").write_text("tampered: true\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("current protected file hash changed" in error for error in errors))

    def test_migration_source_hash_must_match_historical_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            self.configure_agent_migration(root)
            path = root / "tests" / "protected-file-migrations.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["migrations"][0]["from_sha256"] = "0" * 64
            path.write_text(json.dumps(data) + "\n", encoding="utf-8")
            errors = validate_release_contract(root)
            self.assertTrue(any("from_sha256" in error for error in errors))

    def test_historical_protected_file_migration_remains_valid_in_later_release(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            self.configure_agent_migration(root)
            migration = json.loads((root / "tests" / "protected-file-migrations.json").read_text(encoding="utf-8"))
            self.assertEqual(migration["migrations"][0]["version"], "1.2.0")
            self.assertEqual((root / "VERSION").read_text(encoding="utf-8").strip(), "1.9.1")
            self.assertEqual(validate_release_contract(root), [])

    def test_future_protected_file_migration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.copy_contract_fixture(Path(raw))
            self.configure_agent_migration(root, version="9.9.9")
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
