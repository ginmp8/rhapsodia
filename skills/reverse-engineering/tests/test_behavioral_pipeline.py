import json
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from behavioral_pipeline import run_pair,shrink_one,candidates
from behavior_lab import DataError

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.refdir=self.root/'reference';self.refdir.mkdir()
        self.canddir=self.root/'candidate';self.canddir.mkdir()
        for root,offset in [(self.refdir,0),(self.canddir,1)]:
            file=root/'main.py'
            file.write_text('import json,sys\nv=json.loads(sys.stdin.readline())\nprint(json.dumps({"output":v.get("n",0)*2+'+str(offset)+'}))\n')
            (root/'argv.json').write_text(json.dumps([sys.executable,str(file)]))
        self.cases=self.root/'cases.jsonl'
        self.cases.write_text(json.dumps({'id':'a','input':{'n':5,'unrelated':1}})+'\n')

    def runit(self,**kwargs):
        return run_pair(self.cases,self.refdir/'argv.json',self.canddir/'argv.json',
                        self.refdir,self.canddir,self.root/'evidence',**kwargs)
    def test_deny_default(self):
        with self.assertRaises(DataError):self.runit()
        self.assertFalse((self.root/'evidence').exists())
    def test_pair_replays_and_detects_mismatch(self):
        out=self.runit(execute_authorized=True,shrink_trials=8)
        self.assertEqual(out['counts']['mismatched'],1)
        self.assertEqual(len(out['counterexamples']),1)
        self.assertTrue(out['counterexamples'][0]['reduced'])
        self.assertEqual(out['verdict'],'DIVERGENCE_OR_INCOMPLETE')
        self.assertTrue((self.root/'evidence'/'reference.jsonl').exists())
        with self.assertRaises(DataError):self.runit(execute_authorized=True)
    def test_input_candidates(self):
        self.assertIn({'x':2},list(candidates({'x':2,'y':'q'})))
        self.assertIn(0,list(candidates(35)))

if __name__=='__main__':unittest.main()
