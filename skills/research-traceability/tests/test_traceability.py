from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'scripts' / 'validate_traceability.py'


def valid_workspace() -> dict:
    return {
        'schema_version': '1.0',
        'mode': 'improve',
        'scope': {
            'research_question': 'How should evidence be transferred into a skill?',
            'target': 'example-target',
            'completeness_boundary': 'corpus-bounded'
        },
        'identities': {
            'research': {'kind': 'manifest', 'value': 'research-manifest.json'},
            'target_baseline': {'kind': 'sha256', 'value': 'abc123'},
            'evaluators': {'kind': 'manifest', 'value': 'evaluator-manifest.json'}
        },
        'sources': [
            {
                'id': 'S-001',
                'title': 'Primary source',
                'locator': 'source.txt',
                'authority': 'primary',
                'evidence_state': 'snapshotted',
                'identity': 'sha256:111',
                'notes': ''
            }
        ],
        'findings': [
            {
                'id': 'F-001',
                'statement': 'Traceability should be bidirectional.',
                'source_ids': ['S-001'],
                'confidence': 'high',
                'relevance': 'required',
                'disposition': 'implement',
                'rationale': 'The target lacks reverse justification.',
                'requirement_ids': ['R-001'],
                'conflict_ids': []
            }
        ],
        'requirements': [
            {
                'id': 'R-001',
                'statement': 'Every substantive change must trace back to an accepted finding.',
                'priority': 'must',
                'derived_from': ['F-001'],
                'change_ids': ['C-001'],
                'evaluation_ids': ['E-001']
            }
        ],
        'changes': [
            {
                'id': 'C-001',
                'kind': 'modify',
                'target': 'SKILL.md#Acceptance-gates',
                'summary': 'Add reverse-justification gate.',
                'status': 'applied',
                'satisfies': ['R-001']
            }
        ],
        'evaluations': [
            {
                'id': 'E-001',
                'kind': 'deterministic',
                'description': 'Reject applied changes with no satisfying requirement.',
                'verifies': ['R-001'],
                'status': 'pass',
                'frozen': True,
                'evidence': 'validator-report.json',
                'limitation': ''
            }
        ],
        'conflicts': []
    }


class TraceabilityValidatorTests(unittest.TestCase):
    def run_validator(self, data: dict, phase: str = 'final') -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / 'traceability.json'
            path.write_text(json.dumps(data), encoding='utf-8')
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path), '--phase', phase],
                capture_output=True,
                text=True,
                check=False
            )

    def test_valid_final_workspace_passes(self):
        result = self.run_validator(valid_workspace())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['metrics']['accepted_finding_requirement_coverage_percent'], 100.0)
        self.assertEqual(report['metrics']['reverse_justification_percent'], 100.0)

    def test_asymmetric_link_fails(self):
        data = valid_workspace()
        data['changes'][0]['satisfies'] = []
        result = self.run_validator(data)
        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {row['code'] for row in report['diagnostics']}
        self.assertIn('record/list-empty', codes)
        self.assertIn('trace/asymmetric-requirement-change', codes)

    def test_planned_evaluation_blocks_final(self):
        data = valid_workspace()
        data['evaluations'][0]['status'] = 'planned'
        data['evaluations'][0]['evidence'] = ''
        result = self.run_validator(data)
        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {row['code'] for row in report['diagnostics']}
        self.assertIn('evaluation/planned-at-final', codes)

    def test_not_run_requires_limitation(self):
        data = valid_workspace()
        data['evaluations'][0]['status'] = 'not-run'
        data['evaluations'][0]['evidence'] = ''
        data['evaluations'][0]['limitation'] = ''
        result = self.run_validator(data)
        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        codes = {row['code'] for row in report['diagnostics']}
        self.assertIn('evaluation/not-run-without-limitation', codes)


if __name__ == '__main__':
    unittest.main()
