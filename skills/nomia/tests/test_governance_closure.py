import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_governance_closure import validate_closure
NOW=datetime(2026,7,22,12,0,tzinfo=timezone.utc).isoformat()

def valid():
 return {'governance_status':'closed','governance_lifecycle':'close','decision':{'state':'accepted','authority':'nomia','evidence':['decision-1']},'technical_state':{'planning':{'state':'complete','source':'handoff-1','observed_at':NOW},'execution':{'state':'complete','source':'handoff-2','observed_at':NOW},'validation':{'state':'passed','source':'handoff-2','observed_at':NOW}},'release':{'state':'closed','released_at':NOW,'evidence':['external-release-1']}}

class GovernanceClosureTests(unittest.TestCase):
 def test_valid_closure(self): self.assertEqual(validate_closure(valid()),[])
 def test_technical_completion_does_not_close_without_nomia_decision_and_release(self):
  data=valid(); data['decision']['evidence']=[]; data['release']={'state':'unknown','evidence':[],'released_at':None}
  errors=validate_closure(data); self.assertTrue(any('decision.evidence' in e for e in errors)); self.assertTrue(any('release.state must be closed' in e for e in errors))

if __name__=='__main__': unittest.main()
