import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("m",ROOT/"scripts/validate_evolution_handoff.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def data():return json.loads((ROOT/"assets/templates/evolution-handoff.json.template").read_text())
def test_template_valid():assert m.validate(data())==[]
def test_budget_ceiling():
 d=data();d["budget"]["max_total_candidates"]=21;assert "budget:max_total_candidates_exceeds_20" in m.validate(d)
