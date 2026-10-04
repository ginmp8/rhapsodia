import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_catalog_release_is_030(self):
  d=json.loads((ROOT/"marketplace/catalog.json").read_text());self.assertEqual(d["plugin"]["version"],"0.4.0");self.assertEqual(d["marketplace"]["version"],"0.4.0")
 def test_release_validator(self):
  r=subprocess.run([sys.executable,str(ROOT/"scripts"/"validate_release_versions.py")],cwd=ROOT);self.assertEqual(r.returncode,0)
if __name__=="__main__":unittest.main()
