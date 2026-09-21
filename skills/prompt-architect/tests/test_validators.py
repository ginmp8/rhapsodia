from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class ValidatorTests(unittest.TestCase):
    def run_ok(self,*args):
        p=subprocess.run([sys.executable,*map(str,args)],text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
    def test_prompt_contract_template(self):
        self.run_ok(ROOT/'scripts/validate_prompt_contract.py',ROOT/'assets/templates/prompt-contract.json.template')
    def test_canonical_scenarios(self):
        self.run_ok(ROOT/'scripts/validate_scenario_suite.py',ROOT/'evals/activation-scenarios.json')
    def test_package_validator(self):
        self.run_ok(ROOT/'scripts/validate_skill.py','--target',ROOT)
    def test_obsolete_v1_scenario_format_is_rejected(self):
        obsolete={'suite_name':'obsolete-v1','status':'planned','scenarios':[{'id':'x','type':'should_activate','prompt':'x','expected_behavior':'x','acceptance_criteria':['x']}]}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'obsolete-v1.json'; p.write_text(json.dumps(obsolete),encoding='utf-8')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_scenario_suite.py'),str(p)],text=True,capture_output=True)
            self.assertNotEqual(r.returncode,0)
if __name__=='__main__': unittest.main()
