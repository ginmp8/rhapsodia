import tempfile,unittest
from pathlib import Path
from guide_intake import build_guidance
from write_ops_scaffold import render_native, main
from validate_ops import validate

class NativeIntakeV2Tests(unittest.TestCase):
 def test_native_guidance_does_not_require_board_or_spec(self):
  result=build_guidance({'work_item_id':'example','repository_write':True,'problem':'Delay','outcome':'Reduce delay','evidence':'issue-1'})
  self.assertTrue(result['repository_write']['ready'],result);self.assertEqual(result['storage_profile'],'artifact-native');self.assertEqual(result['identity_issues'],[])
 def test_native_canonical_ops_without_spec(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'ops.yaml';path.write_text(render_native('example'))
   errors,_=validate(path,require_canonical=True);self.assertEqual(errors,[])
 def test_native_writer_confines_owner(self):
  with tempfile.TemporaryDirectory() as td:
   self.assertEqual(main(['docs/product/example/ops.yaml','--repo-root',td,'--work-item','example']),0)
   self.assertTrue((Path(td)/'docs/product/example/ops.yaml').exists())
   self.assertEqual(main(['docs/specs/example/ops.yaml','--repo-root',td,'--work-item','example']),1)
 def test_legacy_profile_remains_explicit(self):
  result=build_guidance({'storage_profile':'legacy-board','repository_write':True,'problem':'Delay','outcome':'Reduce delay','evidence':'issue-1'})
  self.assertFalse(result['repository_write']['ready']);self.assertIn('BOARD_ROOT',result['repository_write']['missing_fields'])
