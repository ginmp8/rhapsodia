from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import native_planning as planning
from artifact_protocol import ContractError
from test_optional_task_phases_v2 import document

class PlanningConsistencyGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name);self.work=self.repo/'docs/specs/example'
        planning.identity(self.repo,'example','2026-10-03T12:00:00Z')
        (self.work/'prd.md').write_text('# Requirements\n\n### REQ-001 Result\nBounded requirement.\n### AC-001 Result\n- Requirements: REQ-001\n')
        (self.work/'tasks.md').write_text(document().replace('  - Decisions: DECISION-001','  - Decisions: none'))
        (self.work/'validation.md').write_text('# Validation plan\n\n### VAL-001 Check\n- Requirements: REQ-001\n- Acceptance: AC-001\n- Tasks: task001, task002, task003\n')
        (self.work/'notes.md').write_text('# Planning notes\n\nEvidence-backed planning assumptions.\n')
    def tearDown(self):self.tmp.cleanup()
    def test_identity_is_part_of_validation_evidence(self):
        result=planning.validate(self.repo,'example');self.assertEqual(result['status'],'pass',result)
        self.assertIn('docs/specs/example/planning-identity.json',result['source_hashes'])
    def test_declared_clarification_contract_is_not_silently_skipped(self):
        (self.work/'notes.md').write_text('---\nclarification_contract: 2\n---\n# Notes\n\n### BLOCKER-001 - Missing decision\n- Status: open\n')
        result=planning.validate(self.repo,'example');self.assertEqual(result['status'],'fail',result)
    def test_conditional_artifacts_are_bound_to_validation(self):
        (self.work/'contract-spec.md').write_text('# Contract\n\nStable input for the source-binding test.\n')
        with patch('native_planning.validate_conditional_artifacts',return_value=[]):
            result=planning.validate(self.repo,'example')
        self.assertEqual(result['status'],'pass',result);self.assertIn('docs/specs/example/contract-spec.md',result['source_hashes'])
    def test_conditional_source_mutation_during_validation_is_rejected(self):
        source=self.work/'contract-spec.md';source.write_text('# Original contract\n')
        def change(_):source.write_text('# Changed contract\n');return []
        with patch('native_planning.validate_conditional_artifacts',side_effect=change):
            with self.assertRaises(ContractError):planning.validate(self.repo,'example')
    def test_handoff_rejects_open_blockers(self):
        (self.work/'notes.md').write_text('---\nclarification_contract: 2\n---\n# Notes\n\n### BLOCKER-001 - Approval needed\n- Status: open\n- Severity: high\n- Evidence: source-001\n- Owner: planner\n- Resolution condition: recorded approval\n')
        result=planning.validate(self.repo,'example',handoff=True);self.assertEqual(result['status'],'fail',result)
if __name__=='__main__':unittest.main()
