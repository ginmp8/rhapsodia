from __future__ import annotations
import copy,importlib.util,json,os,tempfile,unittest
from pathlib import Path
ROOT=Path(os.environ.get('REVIEW_TARGET',Path(__file__).resolve().parents[1]))
spec=importlib.util.spec_from_file_location('review_agents_validator',ROOT/'scripts/validate_agents.py')
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
class WorkspaceCapabilityTests(unittest.TestCase):
    def setUp(self):self.value=json.loads((ROOT/'docs/agents/contracts/rhapsodia-agent-system.json').read_text())
    def findings(self,value):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'contract.json';path.write_text(json.dumps(value));result=[];validator.validate_contract(path,result);return result
    def test_derived_capability_is_fully_typed(self):
        capability=next(c for c in self.value['capabilities'] if c['id']=='derived-output-write')
        self.assertTrue({'required','effect','scope','approval','idempotency'}<=set(capability))
    def test_missing_authority_field_rejected(self):
        capability=next(c for c in self.value['capabilities'] if c['id']=='derived-output-write');capability.pop('effect',None)
        self.assertTrue(self.findings(self.value))
    def test_widened_derived_scope_rejected(self):
        capability=next(c for c in self.value['capabilities'] if c['id']=='derived-output-write');capability['scope']=['docs/specs']
        self.assertTrue(self.findings(self.value))
    def test_missing_host_mapping_rejected(self):
        next(h for h in self.value['hosts'] if h['host']=='vscode')['capability_mapping'].pop('derived-output-write',None)
        self.assertTrue(self.findings(self.value))
    def test_undeclared_capability_rejected(self):
        self.value['agents'][-1]['capabilities'].append('undeclared-write');self.assertTrue(self.findings(self.value))
if __name__=='__main__':unittest.main()
