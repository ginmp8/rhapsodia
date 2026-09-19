from __future__ import annotations
import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ecosystem_repro_validator',ROOT/'scripts/validate_ecosystem_reproducibility.py')
validator=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(validator)
class EcosystemReproducibilityTests(unittest.TestCase):
    def test_frozen_cross_skill_suite(self):
        result=validator.run()
        self.assertEqual(result['status'],'pass',result)
        self.assertEqual(result['scenario_count'],22)
if __name__=='__main__': unittest.main()
