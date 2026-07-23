import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location('router',ROOT/'scripts/route_ecosystem_request.py'); router=importlib.util.module_from_spec(s); s.loader.exec_module(router)
class RouterTests(unittest.TestCase):
 def test_required_planning(self): self.assertEqual(router.route(['governance','implementation'])['owner_sequence'],['nomia','mago','magia'])
 def test_repeated_phases(self): self.assertEqual(router.route(['implementation','reconcile','tests'])['owner_sequence'],['magia','mago','magia'])
 def test_full_lifecycle(self): self.assertEqual(router.route(['intake','planning','implementation','reconcile','release'])['owner_sequence'],['nomia','mago','magia','mago','nomia'])
if __name__=='__main__': unittest.main()
