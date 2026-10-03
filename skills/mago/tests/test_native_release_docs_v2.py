from pathlib import Path
import json
import unittest
ROOT=Path(__file__).resolve().parents[1]
class NativeReleaseDocumentation(unittest.TestCase):
    def test_active_release_prose_matches_actual_version(self):
        version=(ROOT/'VERSION').read_text().strip()
        self.assertEqual(version,json.loads((ROOT/'release.json').read_text())['version'])
        self.assertIn('ecosystem release `'+version+'`',(ROOT/'SKILL.md').read_text())
        self.assertIn('Release `'+version+'`',(ROOT/'references/ecosystem-handoff-contract.md').read_text())
        self.assertIn('Package versions must all equal `'+version+'`',(ROOT/'references/ecosystem-compatibility.md').read_text())
        self.assertEqual(version,json.loads((ROOT/'references/ecosystem-handoff-contract.json').read_text())['compatibility']['required_ecosystem_release'])

if __name__ == "__main__":
    unittest.main()
