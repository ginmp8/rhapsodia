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


    def test_long_skill_requires_activation_and_non_activation_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            root.mkdir()
            top = '# Demo\n\n## At a Glance\n\nPurpose.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`'
            write_long_skill(root, top)
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_TOP100_ACTIVATION_BOUNDARY', codes)

    def test_long_reference_requires_semantic_preview_signals(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            refs = root / 'references'
            refs.mkdir(parents=True)
            top = '# Demo\n\n## At a Glance\n\n**Use when:** reproducibility is the goal.\n**Do not use when:** another skill owns the task.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`\n\n[Guide](references/guide.md)'
            write_long_skill(root, top)
            (refs / 'guide.md').write_text(
                '# Guide\n\n## At a Glance\n\nUseful summary without routing signals.\n\n## Contents\n\n- Alpha\n\n## Alpha\n\n' + '\n'.join(f'detail {i}' for i in range(120)),
                encoding='utf-8',
            )
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_LONG_MARKDOWN_PREVIEW_SIGNALS', codes)

    def test_generated_long_reference_may_declare_preview_exception(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            refs = root / 'references'
            refs.mkdir(parents=True)
            top = '# Demo\n\n## At a Glance\n\n**Use when:** reproducibility is the goal.\n**Do not use when:** another skill owns the task.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`\n\n[Generated](references/generated.md)'
            write_long_skill(root, top)
            (refs / 'generated.md').write_text(
                '# Generated\n\n<!-- context-preview-exception: generated -->\n\n'
                + '\n'.join(f'detail {i}' for i in range(130)),
                encoding='utf-8',
            )
            code, report = run(root)
            self.assertEqual(0, code, report)
            warning_codes = {row['code'] for row in report['warnings']}
            self.assertIn('CONTEXT_LONG_MARKDOWN_PREVIEW_EXCEPTION', warning_codes)

    def test_long_reference_rejects_obvious_placeholder_preview(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            refs = root / 'references'
            refs.mkdir(parents=True)
            top = '# Demo\n\n## At a Glance\n\n**Use when:** reproducibility is the goal.\n**Do not use when:** another skill owns the task.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`\n\n[Guide](references/guide.md)'
            write_long_skill(root, top)
            (refs / 'guide.md').write_text(
                '# Guide\n\n## At a Glance\n\n'
                '- **Purpose:** Explain the topic in this file.\n'
                '- **Load when:** Read this file when the active workflow needs Guide.\n'
                '- **Decision impact:** See contents below for the details.\n\n'
                '## Contents\n\n- Alpha\n\n## Alpha\n\n' + '\n'.join(f'detail {i}' for i in range(120)),
                encoding='utf-8',
            )
            code, report = run(root)
            self.assertNotEqual(0, code)
            row = next(item for item in report['diagnostics'] if item['code'] == 'CONTEXT_LONG_MARKDOWN_PREVIEW_SIGNALS')
            self.assertTrue(row['evidence']['failures'][0]['vague'])

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

    def test_long_skill_with_deep_acceptance_gates_requires_top100_gate_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            root.mkdir()
            top = '# Demo\n\n## At a Glance\n\nPurpose.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`'
            tail = '\n## Acceptance Gates\n\nA candidate is acceptable only when validation passes.'
            write_long_skill(root, top, tail)
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_TOP100_ACCEPTANCE_GATES', codes)

    def test_long_skill_with_deep_stop_conditions_requires_top100_stop_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            root.mkdir()
            top = '# Demo\n\n## At a Glance\n\nPurpose.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`'
            tail = '\n## Stop Conditions\n\nStop when evidence identity drifts.'
            write_long_skill(root, top, tail)
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_TOP100_STOP_CONDITIONS', codes)

    def test_long_reference_contents_must_match_material_h2_headings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'demo-skill'
            refs = root / 'references'
            refs.mkdir(parents=True)
            top = '# Demo\n\n## At a Glance\n\nPurpose.\n\n## Modes\n\napply\n\n## Workflow at a Glance\n\nDo work.\n\n## Core Invariants\n\nKeep evidence.\n\n`runtime/script > schema/type > validator/gate`\n\n[Guide](references/guide.md)'
            write_long_skill(root, top)
            (refs / 'guide.md').write_text(
                '# Guide\n\n## At a Glance\n\nSummary.\n\n## Contents\n\n- Alpha\n\n## Alpha\n\nA.\n\n## Beta\n\n' + '\n'.join(f'detail {i}' for i in range(110)),
                encoding='utf-8',
            )
            code, report = run(root)
            self.assertNotEqual(0, code)
            codes = {row['code'] for row in report['diagnostics']}
            self.assertIn('CONTEXT_LONG_MARKDOWN_CONTENTS', codes)

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
