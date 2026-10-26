"""Negative tests for the release's non-optional agent control plane."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('required_session_validator', ROOT / 'scripts/validate_agents.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class RequiredSessionGuardTests(unittest.TestCase):
    def agent_findings(self, name, mutate):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / name
            path.write_text(mutate((ROOT / 'agents' / name).read_text()))
            findings = []
            validator.validate_agent_file(path, validator.EXPECTED[name], findings)
            return {f['code'] for f in findings}

    def contract_findings(self, mutate):
        value = json.loads((ROOT / 'docs/agents/contracts/rhapsodia-agent-system.json').read_text())
        mutate(value)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'contract.json'
            path.write_text(json.dumps(value))
            findings = []
            validator.validate_contract(path, findings)
            return {f['code'] for f in findings}

    def test_removed_graph_first_rule_is_rejected(self):
        codes = self.agent_findings('mago.agent.md', lambda s: s.replace('graph-first', 'optional-memory'))
        self.assertIn('MANDATORY_SESSION', codes)

    def test_missing_independent_optout_is_rejected(self):
        codes = self.agent_findings('nomia.agent.md', lambda s: s.replace('--no-graph', '--old-switch'))
        self.assertIn('MANDATORY_SESSION', codes)

    def test_memory_scope_cannot_expand_to_product_files(self):
        def mutate(d):
            next(c for c in d['capabilities'] if c['id'] == 'local-memory-maintenance')['scope'].append('src')
        self.assertIn('MEMORY_AUTHORITY', self.contract_findings(mutate))

    def test_one_agent_cannot_silently_omit_memory(self):
        def mutate(d):
            d['agents'][0]['capabilities'].remove('local-memory-maintenance')
        self.assertIn('MANDATORY_SESSION', self.contract_findings(mutate))

    def test_graph_cannot_become_optional_by_default(self):
        self.assertIn('MANDATORY_SESSION', self.contract_findings(lambda d: d['session_memory']['default'].update(graph='optional')))

    def test_adhoc_cannot_gain_subagent_orchestration(self):
        self.assertIn('ADHOC_AUTHORITY', self.contract_findings(lambda d: d['routing']['direct_adhoc'].update(subagent_delegation=True)))


class MemoryPurposeGuardTests(RequiredSessionGuardTests):
    """Additive static regression checks, not model-comprehension measurements."""

    def test_all_profiles_explain_reuse_learning_and_success(self):
        required = (
            "prevent repeated environment discovery", "across agents and sessions",
            "not a ritual", "repository and live environment remain authoritative",
            "same question and unchanged evidence", "no-new-reusable-knowledge",
            "not graph size or invocation counts",
            "do not skip necessary source reads or verification",
        )
        for name in validator.EXPECTED:
            text = "\n".join((ROOT / 'agents' / name).read_text().splitlines()[:100]).lower()
            for marker in required:
                with self.subTest(agent=name, marker=marker):
                    self.assertIn(marker, text)

    def test_removed_purpose_is_rejected_for_each_profile(self):
        for name in validator.EXPECTED:
            with self.subTest(agent=name):
                codes = self.agent_findings(name, lambda s: s.replace(
                    'prevent repeated environment discovery', 'perform initialization'))
                self.assertIn('MEMORY_PURPOSE', codes)

    def test_purpose_only_after_top100_is_rejected(self):
        def mutate(text):
            lines = text.splitlines()
            purpose = [line for line in lines if 'prevent repeated environment discovery' in line]
            remaining = [line for line in lines if line not in purpose]
            return '\n'.join(remaining + [''] * 101 + purpose) + '\n'
        self.assertIn('MEMORY_PURPOSE', self.agent_findings('mago.agent.md', mutate))

    def test_removed_nonritual_learning_rule_is_rejected(self):
        self.assertIn('MEMORY_PURPOSE', self.agent_findings('magia.agent.md', lambda s: s.replace(
            'no-new-reusable-knowledge', 'always-add-a-note')))

    def test_removed_source_authority_rule_is_rejected(self):
        self.assertIn('MEMORY_PURPOSE', self.agent_findings('nomia.agent.md', lambda s: s.replace(
            'repository and live environment remain authoritative', 'graph is authoritative')))

    def test_missing_structured_purpose_is_rejected(self):
        self.assertIn('MEMORY_PURPOSE_CONTRACT', self.contract_findings(
            lambda d: d['session_memory'].pop('purpose', None)))

    def test_quantity_as_success_is_rejected(self):
        def mutate(doc):
            doc['session_memory'].setdefault('purpose', {})['success_measure'] = 'graph-record-count'
        self.assertIn('MEMORY_PURPOSE_CONTRACT', self.contract_findings(mutate))

    def test_unconditional_duplicate_learning_is_rejected(self):
        def mutate(doc):
            doc['session_memory'].setdefault('purpose', {})['no_new_knowledge'] = 'write-anyway'
        self.assertIn('MEMORY_PURPOSE_CONTRACT', self.contract_findings(mutate))

    def test_managed_guidance_explains_why_and_source_authority(self):
        import ast
        module = ast.parse((ROOT / 'skills/runtime-harness/scripts/runtime_core/integration.py').read_text())
        text = next(ast.literal_eval(n.value) for n in module.body
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CONTENT' for t in n.targets)).lower()
        for marker in ('prevent repeated environment discovery', 'across agents and sessions',
                       'not a ritual', 'repository and live environment remain authoritative',
                       'no-new-reusable-knowledge', 'not graph size or invocation counts'):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_cli_contract_versions_and_legacy_memory_compatibility(self):
        # Local Graph Engine 3.2.0 adds a separate v2 lesson contract; do not
        # change the existing v1 reference/remedy schema or independent skill IDs.
        expected = {'runtime-harness': '1.3.0', 'local-graph-engine': '3.2.0',
                    'rhapsodia-workspace': '1.0.2', 'operational-context': '1.1.0'}
        for skill, version in expected.items():
            with self.subTest(skill=skill):
                self.assertEqual((ROOT / 'skills' / skill / 'VERSION').read_text().strip(), version)
        contracts = ROOT / 'skills' / 'local-graph-engine' / 'contracts'
        v1 = json.loads((contracts / 'workspace-knowledge-v1.schema.json').read_text())
        v2 = json.loads((contracts / 'workspace-knowledge-v2.schema.json').read_text())
        self.assertEqual(v1['properties']['kind']['enum'], ['reference', 'remedy'])
        self.assertEqual(v1['properties']['schema']['const'], 'workspace-knowledge-v1')
        self.assertEqual(v2['properties']['kind']['const'], 'lesson')
        self.assertEqual(v2['properties']['schema']['const'], 'workspace-knowledge-v2')
        catalog = json.loads((ROOT / 'marketplace/catalog.json').read_text())
        self.assertEqual(catalog['plugin']['version'], '0.14.1')


if __name__ == '__main__':
    unittest.main()
