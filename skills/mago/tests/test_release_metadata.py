from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_release_metadata import validate


class ReleaseMetadataTests(unittest.TestCase):
    def copy_release_surface(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory(prefix="mago-release-")
        target = Path(temp.name) / "mago"
        (target / "agents").mkdir(parents=True)
        (target / "references").mkdir()
        for rel in ("release.json", "CHANGELOG.md", "agents/openai.yaml", "references/installation-and-release.md"):
            source = ROOT / rel
            destination = target / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temp, target

    def test_current_release_metadata_passes(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def test_version_and_changelog_must_match(self) -> None:
        temp, target = self.copy_release_surface()
        try:
            data = json.loads((target / "release.json").read_text(encoding="utf-8"))
            data["version"] = "2.2.0"
            (target / "release.json").write_text(json.dumps(data), encoding="utf-8")
            errors = validate(target)
            self.assertTrue(any("missing release heading" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_release_product_must_match_agent_policy(self) -> None:
        temp, target = self.copy_release_surface()
        try:
            text = (target / "agents" / "openai.yaml").read_text(encoding="utf-8").replace("  - atlas\n", "")
            (target / "agents" / "openai.yaml").write_text(text, encoding="utf-8")
            errors = validate(target)
            self.assertTrue(any("product `atlas` is not declared" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_unstable_or_implicit_version_is_rejected(self) -> None:
        temp, target = self.copy_release_surface()
        try:
            data = json.loads((target / "release.json").read_text(encoding="utf-8"))
            data["version"] = "latest"
            (target / "release.json").write_text(json.dumps(data), encoding="utf-8")
            errors = validate(target)
            self.assertTrue(any("stable semantic versioning" in error for error in errors), errors)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
