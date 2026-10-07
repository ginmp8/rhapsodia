"""Optional Node execution of production live client with a fake transport."""
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]

class LiveClientRunnerTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'optional Node runtime unavailable')
    def test_live_client_contract(self):
        result=subprocess.run([shutil.which('node'),str(ROOT/'tests/test_live_client.cjs'),str(ROOT/'assets/viewer.js')],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
        self.assertIn('"cases":9',result.stdout)

if __name__=='__main__':unittest.main()
