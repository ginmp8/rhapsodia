#!/usr/bin/env python3
"""Deterministic offline regression, security and compatibility gates.
Run: python -S tests/test_suite.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'


class ResearchSuiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.results = self.base / 'results'
        self.results.mkdir()
        self.outline = self.base / 'outline.yaml'
        self.fields = self.base / 'fields.yaml'
        self.output = self.base / 'report.md'
        self.item = self.results / 'Item_A.json'
        self.outline.write_text(
            'topic: Example\noutput_language: en\nresearch:\n  time_range: since 2024\nitems:\n  - name: Item A\nexecution:\n  batch_size: 2\n  items_per_agent: 1\n  output_dir: ./results\n', encoding='utf-8')
        self.fields.write_text(
            'fields:\n  Basic Info:\n    - name: name\n      description: Canonical name\n      detail_level: brief\n    - name: release_date\n      description: Release date\n      detail_level: moderate\n      required: false\n  Technical Features:\n    - name: architecture\n      description: Architecture\n      detail_level: detailed\n      required: true\nuncertain: []\n', encoding='utf-8')
        self.data = {
            'name': 'Item A', 'release_date': '[uncertain]',
            'technical_features': {'architecture': 'Layered'},
            'notes': 'Extra evidence', 'uncertain': ['release_date'],
            '_sources': [{'id': 'S-1', 'title': 'Primary',
                          'url': 'https://example.com/path', 'accessed': '2026-10-14'}],
            '_claims': [{'id': 'C-1', 'text': 'It is layered', 'status': 'supported',
                         'source_ids': ['S-1'], 'locator': 'Architecture section'}],
        }
        self.save()

    def save(self):
        self.item.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, '-S', str(SCRIPTS / name), *map(str, args)],
                              text=True, capture_output=True)

    def check(self, p, expected=0):
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
        return json.loads(p.stdout)

    def workspace(self):
        return self.run_script('validate_workspace.py', '--outline', self.outline, '--fields', self.fields)

    def result(self, *args):
        return self.run_script('validate_result.py', '--fields', self.fields, '--json', self.item, *args)

    def report(self, *args, output=None):
        return self.run_script('generate_report.py', '--outline', self.outline, '--fields', self.fields,
                               '--results-dir', self.results, '--output', output or self.output, *args)

    def resume(self, *args):
        return self.run_script('check_resume.py', '--outline', self.outline, '--fields', self.fields,
                               '--json', self.item, '--today', '2026-10-14', *args)

    def test_legacy_compatible_schema_and_report(self):
        self.assertTrue(self.check(self.workspace())['valid'])
        result = self.check(self.result())
        self.assertTrue(result['research_ready'])
        self.assertEqual(result['required_fields'], 2)
        result = self.check(self.report())
        self.assertEqual(result['included_items'], 1)
        content = self.output.read_text(encoding='utf-8')
        self.assertIn('Layered', content)
        self.assertIn('Extra evidence', content)
        self.assertNotIn('[uncertain]', content)
        self.assertIn('https://example.com/path', content)
        self.assertIn('Claim evidence', content)

    def test_optional_flag_does_not_make_every_other_field_optional(self):
        self.data['technical_features'] = {}
        self.save()
        result = self.check(self.result(), 1)
        self.assertIn('architecture', result['missing_required'])

    def test_uncertain_required_not_valid_research(self):
        self.data['technical_features']['architecture'] = '[uncertain]'
        self.data['uncertain'].append('architecture')
        self.save()
        self.assertEqual(self.check(self.result(), 1)['status'], 'incomplete')
        self.assertTrue(self.check(self.result('--allow-incomplete'))['structural_valid'])

    def test_empty_required_not_valid(self):
        self.data['technical_features']['architecture'] = ''
        self.save()
        self.assertIn('architecture', self.check(self.result(), 1)['empty_required'])

    def test_missing_sources_not_research_ready(self):
        self.data['_sources'] = []
        self.data.pop('_claims')
        self.save()
        report = self.check(self.result(), 1)
        self.assertFalse(report['research_ready'])
        self.assertTrue(report['structural_valid'])

    def test_invalid_javascript_url_is_rejected(self):
        self.data['_sources'][0]['url'] = 'javascript:alert(1)'
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_credentials_in_url_are_rejected(self):
        self.data['_sources'][0]['url'] = 'https://admin:secret@example.com/'
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_non_http_url_is_rejected(self):
        self.data['_sources'][0]['url'] = 'file:///etc/passwd'
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_invalid_source_access_date_is_rejected(self):
        self.data['_sources'][0]['accessed'] = 'yesterday'
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_dangling_claim_reference_is_rejected(self):
        self.data['_claims'][0]['source_ids'] = ['S-unknown']
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_claim_without_source_is_rejected(self):
        self.data['_claims'][0]['source_ids'] = []
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_duplicate_claim_id_is_rejected(self):
        self.data['_claims'].append(dict(self.data['_claims'][0]))
        self.save()
        self.assertTrue(self.check(self.result(), 1)['errors'])

    def test_disputes_preserved_visible_not_suppressed(self):
        self.data['_claims'].append({'id': 'C-2', 'text': 'A source disputes it',
                                     'status': 'contradicted', 'source_ids': ['S-1']})
        self.save()
        result = self.check(self.result())
        self.assertIn('C-2', result['unsupported_claims'])
        self.check(self.report())
        self.assertIn('contradicted', self.output.read_text(encoding='utf-8'))

    def test_partial_report_excludes_bad_results(self):
        self.outline.write_text(self.outline.read_text().replace('execution:', '  - name: Item B\nexecution:'))
        bad = self.results / 'Item_B.json'
        bad.write_text(json.dumps({'name': 'Item B'}))
        self.check(self.report(), 2)
        r = self.check(self.report('--allow-partial'))
        self.assertTrue(r['partial'])
        self.assertEqual(r['included_items'], 1)
        self.assertIn('Item_B.json', str(r['invalid_results']))
        md = self.output.read_text(encoding='utf-8')
        self.assertIn('PARTIAL REPORT', md)
        self.assertNotIn('## Item B', md)

    def test_unexpected_result_not_silently_included(self):
        (self.results / 'Unknown.json').write_text(json.dumps({**self.data, 'name': 'Unknown'}))
        r = self.check(self.report())
        self.assertEqual(r['included_items'], 1)
        self.assertIn('Unknown.json', r['unexpected_results'])

    def test_duplicate_file_identity_is_rejected(self):
        (self.results / 'duplicate.json').write_text(json.dumps(self.data))
        self.check(self.report(), 2)
        r = self.check(self.report('--allow-partial'), 2)
        self.assertFalse(r['generated'])

    def test_markdown_and_html_are_escaped(self):
        self.data['notes'] = '<script>alert(1)</script> [click](javascript:alert(1))'
        self.data['_sources'][0]['title'] = '[Injected](javascript:evil)'
        self.save()
        self.check(self.report())
        text = self.output.read_text(encoding='utf-8')
        self.assertNotIn('<script>', text)
        self.assertNotIn('](', text.split('#### Notes')[1].split('###')[0])
        self.assertIn('&lt;script', text)

    def test_report_does_not_overwrite_input(self):
        before = self.item.read_bytes()
        self.check(self.report(output=self.item), 2)
        self.assertEqual(self.item.read_bytes(), before)

    def test_report_rejects_external_output_without_explicit_flag(self):
        outside = self.base.parent / ('outside-' + self.base.name + '.md')
        self.check(self.report(output=outside), 2)
        self.assertFalse(outside.exists())

    def test_report_output_is_deterministic(self):
        self.check(self.report())
        before = self.output.read_bytes()
        self.check(self.report())
        self.assertEqual(before, self.output.read_bytes())

    def test_unsupported_yaml_structure_rejected(self):
        self.outline.write_text(self.outline.read_text().replace('topic: Example', 'topic: |'))
        self.check(self.workspace(), 2)

    def test_relative_path_escape_rejected(self):
        self.outline.write_text(self.outline.read_text().replace('./results', '../outside'))
        self.assertIn('escape', str(self.check(self.workspace(), 1)['errors']))

    def test_duplicate_item_id_rejected(self):
        self.outline.write_text(self.outline.read_text().replace('  - name: Item A',
                  '  - name: Item A\n    id: same\n  - name: Item B\n    id: same'))
        result = self.check(self.workspace(), 1)
        self.assertIn('duplicate item file identities', result['errors'])

    def test_quoted_comma_in_inline_schema(self):
        self.fields.write_text('fields:\n  Test:\n    - {name: name, description: "One, two", detail_level: brief}\nuncertain: []\n')
        self.assertTrue(self.check(self.workspace())['valid'])

    def test_resume_requires_explicit_stamped_identity(self):
        r = self.check(self.resume(), 1)
        self.assertIn('missing-run-identity', r['reasons'])
        stamped = self.check(self.resume('--stamp'))
        self.assertTrue(stamped['safe_to_resume_without_scope_research'])
        self.assertFalse(stamped['freshness_verified'])

    def test_schema_drift_invalidates_resume(self):
        self.check(self.resume('--stamp'))
        self.fields.write_text(self.fields.read_text().replace('Architecture\n', 'Architecture and runtime\n'))
        self.assertIn('changed-fields_contract_fingerprint', self.check(self.resume(), 1)['reasons'])

    def test_scope_drift_invalidates_resume(self):
        self.check(self.resume('--stamp'))
        self.outline.write_text(self.outline.read_text().replace('since 2024', 'since 2025'))
        self.assertIn('changed-scope_fingerprint', self.check(self.resume(), 1)['reasons'])

    def test_comment_only_change_does_not_force_research(self):
        self.check(self.resume('--stamp'))
        self.fields.write_text(self.fields.read_text() + '# nonsemantic comment\n')
        r = self.check(self.resume())
        self.assertTrue(r['safe_to_resume_without_scope_research'])
        self.assertTrue(r['warnings'])

    def test_unrelated_new_item_does_not_invalidate(self):
        self.check(self.resume('--stamp'))
        self.outline.write_text(self.outline.read_text().replace('execution:', '  - name: Item B\nexecution:'))
        self.assertTrue(self.check(self.resume())['safe_to_resume_without_scope_research'])

    def test_source_metadata_change_invalidates_resume(self):
        self.check(self.resume('--stamp'))
        self.data = json.loads(self.item.read_text())
        self.data['_sources'][0]['title'] = 'Updated'
        self.save()
        self.assertIn('changed-sources_fingerprint', self.check(self.resume(), 1)['reasons'])

    def test_age_policy_invalidates_resume(self):
        self.check(self.resume('--stamp'))
        later = self.run_script('check_resume.py', '--outline', self.outline,
            '--fields', self.fields, '--json', self.item, '--today', '2026-10-20', '--max-age-days', '2')
        self.assertIn('age-outside-policy', self.check(later, 1)['reasons'])

    def test_stamp_rejects_invalid_result_without_mutation(self):
        self.data['technical_features']['architecture'] = ''
        self.save()
        original = self.item.read_bytes()
        self.check(self.resume('--stamp'), 2)
        self.assertEqual(self.item.read_bytes(), original)

    def test_top_100_self_sufficient_and_local_links(self):
        text = (ROOT / 'SKILL.md').read_text()
        lines = text.splitlines()
        self.assertLessEqual(len(lines), 100)
        for needle in ('Mode router', 'Workflow (sufficient to begin)', 'Non-negotiable rules',
                       'Deterministic CLI', 'Completion contract', 'report-workflow.md'):
            self.assertIn(needle, text)
        # Files added in this release; unchanged original source modules are kept by overlay.
        for stem in ('workspace-contract', 'evidence-contract', 'resume-contract', 'quality-evaluation',
                     'plan-workflow', 'deep-workflow', 'report-workflow'):
            self.assertTrue((ROOT / 'references' / f'{stem}.md').exists())

    def test_skill_version_and_changelog_match(self):
        version = (ROOT / 'VERSION').read_text().strip()
        self.assertRegex(version, r'^\d+\.\d+\.\d+$')
        self.assertIn('## [' + version + ']', (ROOT / 'CHANGELOG.md').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
