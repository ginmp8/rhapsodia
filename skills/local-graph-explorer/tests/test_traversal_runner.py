"""Optional Node oracle runner; Node is not a viewer runtime dependency."""
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
class TraversalAlgorithmTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'optional Node test runtime unavailable')
    def test_structural_walkthrough_contract(self):
        p=subprocess.run([shutil.which('node'),str(ROOT/'tests/test_traversal.cjs'),str(ROOT/'assets/graph-traversal.js')],capture_output=True,text=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
if __name__=='__main__':unittest.main()
