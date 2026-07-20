from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from package_skill import python_env, trusted_skill_root, validate_target


class PackagingSecurityTests(unittest.TestCase):
    def test_target_must_be_owned_by_the_running_package_script(self) -> None:
        self.assertEqual(validate_target(ROOT), trusted_skill_root())
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "refusing external target"):
                validate_target(Path(tmp))

    def test_validator_environment_does_not_inherit_credentials(self) -> None:
        with patch.dict(
            os.environ,
            {
                "NOMIA_TEST_SECRET": "do-not-forward",
                "AWS_SECRET_ACCESS_KEY": "do-not-forward",
                "GITHUB_TOKEN": "do-not-forward",
            },
            clear=False,
        ):
            env = python_env(ROOT)
        self.assertNotIn("NOMIA_TEST_SECRET", env)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", env)
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(env["PYTHONHASHSEED"], "0")
        self.assertIn(str(ROOT / "scripts"), env["PYTHONPATH"])


if __name__ == "__main__":
    unittest.main()
