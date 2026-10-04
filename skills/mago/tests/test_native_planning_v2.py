from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from artifact_protocol import ContractError
from native_planning import identity,validate,read_identity
from test_optional_task_phases_v2 import document

class NativePlanningV2Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name);self.work=self.repo/'docs/specs/example'
  identity(self.repo,'example','2026-10-03T12:00:00Z')
  (self.work/'prd.md').write_text('# Requirements\n\n### REQ-001 Result\nBounded requirement.\n### AC-001 Result\n- Requirements: REQ-001\n')
  (self.work/'tasks.md').write_text(document().replace('  - Decisions: DECISION-001','  - Decisions: none'))
  (self.work/'validation.md').write_text('# Validation plan\n\n### VAL-001 Deterministic check\n- Requirements: REQ-001\n- Acceptance: AC-001\n- Tasks: task001, task002, task003\n')
  (self.work/'notes.md').write_text('# Planning notes\n\nPlanning-only sources and assumptions.\n')
 def tearDown(self):self.tmp.cleanup()
 def test_stable_local_identity(self):
  result=identity(self.repo,'example','2026-10-03T12:00:00Z');self.assertEqual(result['status'],'unchanged');self.assertEqual(result['identity']['spec_id'],'spec-2026-10-03-example');self.assertFalse((self.repo/'docs/boards').exists())
 def test_identity_cannot_remint(self):
  with self.assertRaises(ContractError):identity(self.repo,'example','2026-10-04T12:00:00Z')
 def test_standard_plan_passes_without_board(self):
  result=validate(self.repo,'example');self.assertEqual(result['status'],'pass',result);self.assertFalse(result['runtime_validation_performed'])
 def test_missing_traceability_rejected(self):
  (self.work/'validation.md').write_text('# Validation\n\nNo explicit planned references.\n');self.assertEqual(validate(self.repo,'example')['status'],'fail')
 def test_omitted_required_file_rejected(self):
  (self.work/'tasks.md').unlink();self.assertEqual(validate(self.repo,'example')['status'],'fail')
 def test_governed_requires_explicit_decisions(self):
  result=validate(self.repo,'example','governed');self.assertEqual(result['status'],'fail');self.assertTrue(any('artifact-decisions' in x for x in result['errors']))
 def test_identity_date_mismatch(self):
  p=self.work/'planning-identity.json';value=json.loads(p.read_text());value['created_at']='2026-10-04T12:00:00Z';p.write_text(json.dumps(value))
  with self.assertRaises(ContractError):validate(self.repo,'example')
if __name__=='__main__':unittest.main()
