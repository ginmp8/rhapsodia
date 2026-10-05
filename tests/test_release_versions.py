import json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RELEASE="0.5.0"
class Tests(unittest.TestCase):
 def test_catalog_release_is_050(self):
  d=json.loads((ROOT/"marketplace/catalog.json").read_text());self.assertEqual(d["plugin"]["version"],RELEASE);self.assertEqual(d["marketplace"]["version"],RELEASE)
 def test_release_validator(self):
  r=subprocess.run([sys.executable,str(ROOT/"scripts"/"validate_release_versions.py"),"--expected-version",RELEASE],cwd=ROOT);self.assertEqual(r.returncode,0)
 def test_release_archive_keeps_env_template(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/"release.zip"
   r=subprocess.run([sys.executable,str(ROOT/"scripts"/"build_release_archive.py"),"--version",RELEASE,"--output",str(out)],cwd=ROOT,capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stdout+r.stderr)
   with zipfile.ZipFile(out) as z:
    names=set(z.namelist())
   self.assertIn(f"rhapsodia-{RELEASE}/.env.example",names)
   self.assertNotIn(f"rhapsodia-{RELEASE}/.env",names)
if __name__=="__main__":unittest.main()
