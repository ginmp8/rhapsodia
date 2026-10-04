from __future__ import annotations
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/'assets/templates/prompt-contract.json.template'
ENV_TEMPLATE=ROOT/'assets/templates/execution-environment.json.template'

class ValidatorTests(unittest.TestCase):
    def run_ok(self,*args):
        p=subprocess.run([sys.executable,*map(str,args)],text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
    def run_fail_contract(self,data):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'contract.json'; p.write_text(json.dumps(data),encoding='utf-8')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_prompt_contract.py'),str(p)],text=True,capture_output=True)
            self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)
            return r.stdout+r.stderr
    def template(self): return json.loads(TEMPLATE.read_text(encoding='utf-8'))
    def test_prompt_contract_template(self): self.run_ok(ROOT/'scripts/validate_prompt_contract.py',TEMPLATE)
    def test_canonical_scenarios(self): self.run_ok(ROOT/'scripts/validate_scenario_suite.py',ROOT/'evals/activation-scenarios.json')
    def test_package_validator(self): self.run_ok(ROOT/'scripts/validate_skill.py','--target',ROOT)
    def test_obsolete_v1_scenario_format_is_rejected(self):
        obsolete={'suite_name':'obsolete-v1','status':'planned','scenarios':[{'id':'x','type':'should_activate','prompt':'x','expected_behavior':'x','acceptance_criteria':['x']}]}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'obsolete-v1.json'; p.write_text(json.dumps(obsolete),encoding='utf-8')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_scenario_suite.py'),str(p)],text=True,capture_output=True)
            self.assertNotEqual(r.returncode,0)
    def test_obsolete_v1_prompt_contract_is_rejected(self):
        d=self.template(); d['contract_version']=1
        self.assertIn('contract_version must be 2',self.run_fail_contract(d))
    def test_prompt_only_security_enforcement_is_rejected(self):
        d=self.template(); d['requirements'][0]['control_class']='security'; d['requirements'][0]['enforcement']='prompt'
        self.assertIn('prompt-only enforcement',self.run_fail_contract(d))
    def test_behavioral_claim_requires_execution_profile_identity(self):
        d=self.template(); d['validation']['claim_level']='behavioral'; d['validation']['freeze_state']='frozen'; d['validation']['suite_id']='suite-1'
        self.assertIn('execution_profile_identity',self.run_fail_contract(d))
    def test_llm_judge_behavioral_comparison_requires_bias_controls(self):
        d=self.template(); d['execution_profile']['profile_identity']='p1'; d['validation'].update({'claim_level':'behavioral','freeze_state':'frozen','suite_id':'s1','execution_profile_identity':'p1'}); d['validation']['comparison'].update({'enabled':True,'evaluator_kind':'llm-judge','evaluator_identity':'j1','blinded':False,'position_swap':False,'repetitions':1,'ties_allowed':False})
        out=self.run_fail_contract(d); self.assertIn('position_swap',out); self.assertIn('repetitions >= 2',out)

    def run_environment(self,data,compare=None):
        with tempfile.TemporaryDirectory() as d:
            left=Path(d)/'left.json'; left.write_text(json.dumps(data),encoding='utf-8')
            argv=[sys.executable,str(ROOT/'scripts/validate_execution_environment.py'),str(left)]
            if compare is not None:
                right=Path(d)/'right.json'; right.write_text(json.dumps(compare),encoding='utf-8'); argv += ['--compare',str(right)]
            return subprocess.run(argv,text=True,capture_output=True)
    def environment(self): return json.loads(ENV_TEMPLATE.read_text(encoding='utf-8'))
    def test_execution_environment_template(self): self.run_ok(ROOT/'scripts/validate_execution_environment.py',ENV_TEMPLATE)
    def test_execution_environment_missing_model_identity_is_rejected(self):
        d=self.environment(); d['model']['configuration_identity']=''
        r=self.run_environment(d); self.assertNotEqual(r.returncode,0); self.assertIn('model.configuration_identity',r.stdout+r.stderr)
    def test_execution_environment_drift_is_detected(self):
        left=self.environment(); right=copy.deepcopy(left); right['model']['configuration_identity']='different-config'
        r=self.run_environment(left,right); self.assertNotEqual(r.returncode,0); self.assertIn('ENVIRONMENT_DRIFT',r.stdout+r.stderr)
if __name__=='__main__': unittest.main()
