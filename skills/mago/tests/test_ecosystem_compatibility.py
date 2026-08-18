import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_ecosystem_compatibility import collect_errors

class EcosystemCompatibilityTests(unittest.TestCase):
 def test_local_compatibility_manifest(self): self.assertEqual(collect_errors(ROOT),[])

if __name__=='__main__': unittest.main()
