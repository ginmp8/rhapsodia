from __future__ import annotations
import json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import package_evidence as pe

class PackagingIsolationV2Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.target=self.base/'target';(self.target/'scripts').mkdir(parents=True)
  (self.target/'SKILL.md').write_text('---\nname: synthetic-target\ndescription: synthetic package fixture\n---\n# Test\n')
  self.marker=self.base/'executed.txt';(self.target/'scripts/validate_skill_package.py').write_text('from pathlib import Path\nPath('+repr(str(self.marker))+').write_text("executed")\n')
  self.out=self.base/'skill.zip';self.evidence=self.base/'validation.json';self.receipt()
 def tearDown(self):self.tmp.cleanup()
 def receipt(self):
  # Contract-only synthetic fixture: never release evidence.
  value={'schema_version':'1.0.0','evidence_kind':'executed','target_tree_sha256':pe.tree_digest(self.target),'runner_sha256':'0'*64,'gates':[{'name':n,'status':'pass','returncode':0,'command':['synthetic-fixture'],'output_sha256':'0'*64} for n in ['structure','tests','contracts']]}
  self.evidence.write_text(json.dumps(value));return value
 def test_no_target_execution(self):
  with patch('subprocess.run',side_effect=AssertionError('target code executed')):result=pe.deterministic_zip(self.target,self.out,evidence=self.evidence)
  self.assertFalse(self.marker.exists());self.assertFalse(result['target_code_executed'])
 def test_external_evidence_required(self):
  with self.assertRaisesRegex(ValueError,'evidence'):pe.deterministic_zip(self.target,self.out)
  self.assertFalse(self.out.exists())
 def test_stale_evidence_rejected(self):
  (self.target/'new.md').write_text('new')
  with self.assertRaisesRegex(ValueError,'stale'):pe.deterministic_zip(self.target,self.out,evidence=self.evidence)
 def test_missing_gate(self):
  value=self.receipt();value['gates'].pop();self.evidence.write_text(json.dumps(value))
  with self.assertRaises(ValueError):pe.deterministic_zip(self.target,self.out,evidence=self.evidence)
 def test_boolean_exit_code_rejected(self):
  value=self.receipt();value['gates'][0]['returncode']=False;self.evidence.write_text(json.dumps(value))
  with self.assertRaises(ValueError):pe.deterministic_zip(self.target,self.out,evidence=self.evidence)
 def test_deterministic_bytes(self):
  pe.deterministic_zip(self.target,self.out,evidence=self.evidence);first=self.out.read_bytes()
  pe.deterministic_zip(self.target,self.out,evidence=self.evidence);self.assertEqual(first,self.out.read_bytes())
 def test_output_alias_rejected(self):
  with self.assertRaises(ValueError):pe.deterministic_zip(self.target,self.evidence,evidence=self.evidence)
 def test_symlink_rejected(self):
  (self.target/'linked').symlink_to(self.marker)
  with self.assertRaises(ValueError):pe.snapshot(self.target)
 def test_target_mutation_preserves_last_good(self):
  self.out.write_bytes(b'last-good')
  def mutate(_): (self.target/'drift.md').write_text('drift');return []
  with self.assertRaises(ValueError):pe.deterministic_zip(self.target,self.out,evidence=self.evidence,archive_validator=mutate)
  self.assertEqual(self.out.read_bytes(),b'last-good')
 def test_failed_commit_preserves_last_good(self):
  self.out.write_bytes(b'last-good')
  with patch.object(pe.os,'replace',side_effect=OSError('injected failure')),self.assertRaises(OSError):pe.deterministic_zip(self.target,self.out,evidence=self.evidence)
  self.assertEqual(self.out.read_bytes(),b'last-good');self.assertEqual(list(self.base.glob('.*.tmp')),[])
 def test_duplicate_json_key_rejected(self):
  value=self.evidence.read_text().replace('"schema_version": "1.0.0"','"schema_version":"1.0.0", "schema_version":"1.0.0"');self.evidence.write_text(value)
  with self.assertRaises(ValueError):pe.verify_evidence(self.target,self.evidence)
 def test_evidence_inside_target_rejected(self):
  path=self.target/'evidence.json';path.write_bytes(self.evidence.read_bytes())
  with self.assertRaises(ValueError):pe.verify_evidence(self.target,path)
if __name__=='__main__':unittest.main()
