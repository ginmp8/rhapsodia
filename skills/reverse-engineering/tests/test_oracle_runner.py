import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import oracle_runner as runner
import behavior_lab as lab

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.code=self.root/'oracle.py'
        self.code.write_text('''import sys,json\ntry:\n v=json.loads(sys.stdin.readline())\n print(json.dumps({"output": {"n":v["n"]*2}}))\nexcept Exception:\n print(json.dumps({"error":{"kind":"bad"}}))\n''',encoding='utf8')
        self.argv=self.root/'cmd.json'
        self.argv.write_text(json.dumps([sys.executable, str(self.code)]))
        self.cases=self.root/'inputs.jsonl'
        self.cases.write_text(json.dumps({'id':'simple','input':{'n':2}})+'\n')
        self.output=self.root/'captured.jsonl'

    def test_deny_by_default(self):
        self.assertEqual(runner.main(['--cases',str(self.cases),'--argv-file',str(self.argv),
                                      '--cwd',str(self.root),'--output',str(self.output)]),2)
        self.assertFalse(self.output.exists())

    def test_execute_explicitly_approved_local_test_fixture(self):
        exit=runner.main(['--cases',str(self.cases),'--argv-file',str(self.argv),
                          '--cwd',str(self.root),'--output',str(self.output),'--execute-authorized'])
        self.assertEqual(exit,0)
        observations=lab.load_corpus(self.output)
        self.assertEqual(observations['simple']['observation']['output']['n'],4)
        self.assertEqual(observations['simple']['runner_status'],'ok')

    def test_absolute_executable_required(self):
        self.argv.write_text('["python3","oracle.py"]')
        self.assertRaises(lab.DataError, runner.check_command, self.argv)

    def test_duplicate_ids_rejected(self):
        case=json.dumps({'id':'a','input':{}})+'\n'
        self.cases.write_text(case*2)
        self.assertRaises(lab.DataError,runner.json_lines,self.cases,100)

    def test_broken_json_output_becomes_unverified(self):
        self.code.write_text('print("not json")')
        self.assertEqual(runner.main(['--cases',str(self.cases),'--argv-file',str(self.argv),
                                      '--cwd',str(self.root),'--output',str(self.output),'--execute-authorized']),1)
        self.assertEqual(lab.load_corpus(self.output)['simple']['runner_status'],'invalid-output')

    def test_timeout_becomes_unverified(self):
        self.code.write_text('import time\ntime.sleep(2)')
        self.assertEqual(runner.main(['--cases',str(self.cases),'--argv-file',str(self.argv),
                                      '--cwd',str(self.root),'--output',str(self.output),
                                      '--timeout','0.1','--execute-authorized']),1)
        self.assertEqual(lab.load_corpus(self.output)['simple']['runner_status'],'timeout')

    def test_prevent_input_overwrite(self):
        self.assertEqual(runner.main(['--cases',str(self.cases),'--argv-file',str(self.argv),
                                      '--cwd',str(self.root),'--output',str(self.cases),
                                      '--execute-authorized']),2)

if __name__=='__main__':
    unittest.main()
