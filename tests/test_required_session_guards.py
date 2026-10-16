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


if __name__ == '__main__':
    unittest.main()
