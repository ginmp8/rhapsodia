from pathlib import Path
import importlib.util, unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("journeys",ROOT/"scripts/validate_reference_journeys.py"); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
class ReferenceJourneyTests(unittest.TestCase):
    def test_all_profiles_and_gates(self):
        self.assertEqual(mod.validate(ROOT/"examples/reference-journeys.json"),[])
if __name__=="__main__": unittest.main()
