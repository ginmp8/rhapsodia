from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SCRIPT = ROOT / "scripts" / "package_skill.py"


def load_package_module():
    spec = importlib.util.spec_from_file_location("mago_package_skill", PACKAGE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {PACKAGE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackagingSafetyTests(unittest.TestCase):
    def test_validate_does_not_execute_target_validator(self) -> None:
        package_skill = load_package_module()
        with tempfile.TemporaryDirectory(prefix="mago-package-safety-") as tmp:
            temp_root = Path(tmp)
            target = temp_root / "untrusted-skill"
            scripts = target / "scripts"
            scripts.mkdir(parents=True)
            marker = target / "validator-executed.txt"
            (target / "SKILL.md").write_text(
                "---\n"
                "name: untrusted-skill\n"
                "description: validate an isolated untrusted package fixture with enough lowercase words to satisfy all deterministic structural metadata checks while proving target scripts remain unexecuted during safe packaging\n"
                "---\n\n"
                "# Fixture\n",
                encoding="utf-8",
            )
            (scripts / "validate_skill_package.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n",
                encoding="utf-8",
            )
            output = temp_root / "skill.zip"

            result = package_skill.main(
                ["--target", str(target), "--output", str(output), "--validate"]
            )

            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())
            self.assertFalse(marker.exists(), "packaging executed code from the target package")

    def test_packager_has_no_target_validator_execution_hook(self) -> None:
        source = PACKAGE_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("run_target_validator", source)
        self.assertNotIn("subprocess.run", source)


if __name__ == "__main__":
    unittest.main()
