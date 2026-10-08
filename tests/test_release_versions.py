import json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RELEASE="0.8.0"
NEW_SKILLS=("local-graph-engine","local-graph-explorer","pdf-workbench","runtime-harness","operational-context")
class Tests(unittest.TestCase):
 def test_catalog_release_is_080(self):
  d=json.loads((ROOT/"marketplace/catalog.json").read_text());self.assertEqual(d["plugin"]["version"],RELEASE);self.assertEqual(d["marketplace"]["version"],RELEASE)
 def test_readme_declares_current_release(self):
  first=(ROOT/"README.md").read_text(encoding="utf-8").splitlines()[:20];self.assertTrue(any(line.startswith(f"## {RELEASE}") for line in first),first)
 def test_github_release_workflows_use_current_version(self):
  for name in ("helix-release.yml", "runtime-portability.yml"):
   body=(ROOT/".github/workflows"/name).read_text(encoding="utf-8")
   self.assertIn(f"--version {RELEASE}",body,name)
   self.assertIn(f"rhapsodia-{RELEASE}.zip",body,name)
   self.assertNotIn("0.7.0",body,name)
 def test_graph_view_contract_is_shared_exactly(self):
  engine=(ROOT/"skills/local-graph-engine/contracts/graph-view-v1.schema.json").read_bytes();viewer=(ROOT/"skills/local-graph-explorer/contracts/graph-view-v1.schema.json").read_bytes();self.assertEqual(engine,viewer)
 def test_release_validator(self):
  r=subprocess.run([sys.executable,str(ROOT/"scripts"/"validate_release_versions.py"),"--expected-version",RELEASE],cwd=ROOT);self.assertEqual(r.returncode,0)
 def test_release_archive_contains_expected_files(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/"release.zip"
   r=subprocess.run([sys.executable,str(ROOT/"scripts"/"build_release_archive.py"),"--version",RELEASE,"--output",str(out)],cwd=ROOT,capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stdout+r.stderr)
   with zipfile.ZipFile(out) as z:
    names=set(z.namelist())
   self.assertIn(f"rhapsodia-{RELEASE}/.env.example",names)
   self.assertNotIn(f"rhapsodia-{RELEASE}/.env",names)
   for skill in NEW_SKILLS:self.assertIn(f"rhapsodia-{RELEASE}/skills/{skill}/SKILL.md",names)
if __name__=="__main__":unittest.main()
