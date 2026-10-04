import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v",ROOT/"scripts"/"validate_dynamic_workflow.py"); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
def plan(): return json.loads((ROOT/"assets"/"templates"/"dynamic-workflow-plan.json.template").read_text())
class Tests(unittest.TestCase):
 def test_template_passes(self): self.assertEqual(v.validate(plan())["status"],"pass")
 def test_same_model_independence_rejected(self):
  p=plan(); p["verification"]["same_model_independence_claim"]=True; self.assertIn("E_FALSE_INDEPENDENCE",{x["code"] for x in v.validate(p)["errors"]})
 def test_durable_requires_capability(self):
  p=plan(); p["runtime"]["resumption_semantics"]="durable-external"; self.assertIn("E_DURABLE_CAPABILITY",{x["code"] for x in v.validate(p)["errors"]})
 def test_budget_order(self):
  p=plan(); p["budgets"]["max_parallel"]=9; self.assertIn("E_BUDGET_ORDER",{x["code"] for x in v.validate(p)["errors"]})
 def test_cycle(self):
  p=plan(); p["stages"][0]["depends_on"]=["synthesize"]; self.assertIn("E_CYCLE",{x["code"] for x in v.validate(p)["errors"]})
if __name__=="__main__": unittest.main()
