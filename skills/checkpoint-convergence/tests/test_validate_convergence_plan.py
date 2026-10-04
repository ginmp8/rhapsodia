import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v",ROOT/"scripts"/"validate_convergence_plan.py");v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def plan():return json.loads((ROOT/"assets"/"templates"/"convergence-plan.json.template").read_text())
class Tests(unittest.TestCase):
 def test_template_passes(self):self.assertEqual(v.validate(plan())["status"],"pass")
 def test_oracle_required(self):
  p=plan();del p["checkpoints"][0]["oracle_identity"];self.assertIn("E_ORACLE",{x["code"] for x in v.validate(p)["errors"]})
 def test_gate_order_non_overridable(self):
  p=plan();p["promotion"]["gate_order_is_binding"]=False;self.assertIn("E_PROMOTION",{x["code"] for x in v.validate(p)["errors"]})
 def test_human_required(self):
  p=plan();p["promotion"]["autonomy_policy"]="human-required";self.assertIn("E_HUMAN_REQUIRED",{x["code"] for x in v.validate(p)["errors"]})
 def test_distinct_adversarial_reviewers(self):
  p=plan();p["promotion"]["min_independent_adversarial_reviewers"]=2;self.assertIn("E_ADVERSARIAL_INDEPENDENCE",{x["code"] for x in v.validate(p)["errors"]})
if __name__=="__main__":unittest.main()
