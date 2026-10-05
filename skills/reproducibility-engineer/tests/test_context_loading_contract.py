from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'scripts' / 'validate_context_loading.py'


def run(target: Path):
    cp = subprocess.run([sys.executable, str(VALIDATOR), '--target', str(target)], text=True, capture_output=True)
    return cp.returncode, json.loads(cp.stdout)


def write_long_skill(root: Path, top: str, tail: str = '') -> None:
    filler = '\n'.join(f'line {i}' for i in range(1, 115))
    (root / 'SKILL.md').write_text(
        '---\nname: demo-skill\ndescription: Demo skill for context-loading validation.\n---\n\n'
        + top + '\n' + filler + '\n' + tail + '\n',
        encoding='utf-8',
    )


class ContextLoadingContractTests(unittest.TestCase):
    def test_reproducibility_engineer_self_contract_passes(self) -> None:
        code, report = run(ROOT)
        self.assertEqual(0, code, report)
        self.assertEqual('pass', report['status'])
        self.assertTrue(report['control_surface']['long_skill_contract_applies'])

    def test_long_skill_hiding_workflow_and_invariants_below_100_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            root.mkdir()
            write_long_skill(root, '# Demo\n\n## At a Glance\n\nPurpose only.', '\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`')
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_TOP100_ROUTING', codes)
            self.assertIn('CONTEXT_TOP100_WORKFLOW', codes)
            self.assertIn('CONTEXT_TOP100_INVARIANTS', codes)
            self.assertIn('CONTEXT_TOP100_CONTROL_MODEL', codes)

    def test_long_reference_requires_preview_and_direct_root_link(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            refs = root / 'references'
            refs.mkdir(parents=True)
            top = '# Demo\n\n## At a Glance\n\nPurpose.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`'
            write_long_skill(root, top)
            (refs / 'hidden.md').write_text('# Hidden\n\n' + '\n'.join(f'detail {i}' for i in range(120)), encoding='utf-8')
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_DIRECT_REFERENCE_TOPOLOGY', codes)
            self.assertIn('CONTEXT_LONG_MARKDOWN_PREVIEW', codes)


if __name__ == '__main__':
    unittest.main()
