from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import route_ecosystem_request as router
class RouterTests(unittest.TestCase):
 def test_single_owner(self):
  result=router.route(['planning']); self.assertEqual(result['current_owner'],'mago'); self.assertEqual(result['mutation_owner_count'],1); self.assertEqual(result['handoff_sequence'],[])
 def test_governed_implementation_inserts_planning(self):
  result=router.route(['governance','implementation']); self.assertEqual(result['owner_sequence'],['nomia','mago','magia']); self.assertEqual(result['handoff_sequence'],['nomia_to_mago','mago_to_magia'])
 def test_execution_reporting_uses_allowed_handoff(self):
  result=router.route(['implementation','reporting'],current_owner='magia'); self.assertEqual(result['owner_sequence'],['magia','nomia']); self.assertEqual(result['handoff_sequence'],['magia_to_nomia'])
 def test_unknown_intent_fails(self):
  with self.assertRaises(ValueError): router.route(['unknown'])
if __name__=='__main__': unittest.main()
