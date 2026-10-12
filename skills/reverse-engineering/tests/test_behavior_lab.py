import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import behavior_lab as lab


class BehavioralTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def rows(self, name, records):
        path = self.root / name
        path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
        return path

    def record(self, i, input_, observation, **extra):
        return {'id': i, 'input': input_, 'observation': observation, **extra}

    def compare_rows(self, a, b, **kw):
        return lab.compare(self.rows('ref.jsonl', a), self.rows('rep.jsonl', b), **kw)

    def test_identical_observations_pass(self):
        cases=[self.record('a', {'q': 1}, {'output': {'a': [1, 2]}})]
        report=self.compare_rows(cases,cases)
        self.assertEqual(report['verdict'],'PASS_OBSERVED_CASES')
        self.assertEqual(report['counts']['matched'],1)
        self.assertEqual(len(report['reference']['sha256']),64)

    def test_type_difference_is_real(self):
        ref=[self.record('one', {'x': 1}, {'output': 1})]
        for value in (1.0, True, '1'):
            with self.subTest(value=value):
                report=self.compare_rows(ref,[self.record('one',{'x':1},{'output':value})])
                self.assertEqual(report['counts']['mismatched'],1)
                self.assertEqual(report['findings'][0]['diffs'][0]['pointer'],'/observation/output')

    def test_opt_in_numeric_tolerance(self):
        report=self.compare_rows([self.record('x', 0, {'output': 1})],
                                 [self.record('x', 0, {'output': 1.01})],tolerance=0.02)
        self.assertEqual(report['counts']['matched'],1)
        report=self.compare_rows([self.record('x', 0, {'output': True})],
                                 [self.record('x', 0, {'output': 1})],tolerance=1)
        self.assertEqual(report['counts']['mismatched'],1)

    def test_difference_paths_and_array_order(self):
        report=self.compare_rows([self.record('x', {}, {'output': {'a': [1,2]}})],
                                 [self.record('x', {}, {'output': {'a': [2,1]}})])
        self.assertEqual([x['pointer'] for x in report['findings'][0]['diffs']],
                         ['/observation/output/a/0','/observation/output/a/1'])

    def test_missing_cases_fail_not_silent(self):
        a=[self.record('a',0,{'output':0}), self.record('b',2,{'error':{'kind':'bad'}})]
        b=[self.record('c',0,{'output':0})]
        report=self.compare_rows(a,b)
        self.assertEqual(report['counts']['missing_candidate'],2)
        self.assertEqual(report['counts']['missing_reference'],1)
        self.assertEqual(report['verdict'],'DIVERGENCE_OR_INCOMPLETE')

    def test_runner_failure_cannot_pass(self):
        case=[self.record('a',1,{'error':{'kind':'timeout'}},runner_status='timeout')]
        report=self.compare_rows(case,case)
        self.assertEqual(report['counts']['unverified'],1)

    def test_ignore_requires_specific_observation_pointer(self):
        a=[self.record('a',0,{'output':{'timestamp':'t1','ok':True}})]
        b=[self.record('a',0,{'output':{'timestamp':'t2','ok':True}})]
        self.assertEqual(self.compare_rows(a,b,ignore=frozenset({'/observation/output/timestamp'}))['counts']['matched'],1)
        with self.assertRaises(lab.DataError):
            self.compare_rows(a,b,ignore=frozenset({'/input'}))
        with self.assertRaises(lab.DataError):
            self.compare_rows(a,b,ignore=frozenset({'/observation'}))

    def test_input_mismatch_cannot_be_ignored(self):
        report=self.compare_rows([self.record('a',{'q':1},{'output':'same'})],
                                 [self.record('a',{'q':2},{'output':'same'})])
        self.assertEqual(report['findings'][0]['diffs'][0]['pointer'],'/input/q')

    def test_duplicate_case_ids_rejected(self):
        case=self.record('id', 1, {'output':2})
        path=self.rows('rows', [case,case])
        with self.assertRaisesRegex(lab.DataError,'duplicate case id'):
            lab.load_corpus(path)

    def test_duplicate_json_keys_are_rejected(self):
        self.assertRaises(lab.DataError,lab.strict_json,'{"a":1,"a":2}')
        self.assertRaises(lab.DataError,lab.strict_json,'{"a":{"b":1,"b":2}}')

    def test_nan_and_infinity_rejected(self):
        for token in ['NaN','Infinity','-Infinity']:
            with self.subTest(token=token):
                self.assertRaises(lab.DataError,lab.strict_json,token)

    def test_numeric_overflow_and_unpaired_surrogates_rejected(self):
        self.assertRaises(lab.DataError, lab.strict_json, '1e999')
        self.assertRaises(lab.DataError, lab.strict_json, r'"\ud800"')

    def test_output_alias_rejected(self):
        seed = self.rows('in.jsonl', [self.record('k',1,{'output':2})])
        self.assertEqual(lab.main(['characterize',str(seed),'-o',str(seed)]),2)
        self.assertEqual(lab.load_corpus(seed)['k']['observation']['output'],2)

    def test_missing_observation_field_rejected(self):
        path=self.rows('bad',[{'id':'a','input':{},'observation':{}}])
        self.assertRaises(lab.DataError,lab.load_corpus,path)

    def test_characterization_records_state_and_errors(self):
        path=self.rows('state',[self.record('1',{}, {'output':1,'state':{'count':1}}),
                                self.record('2',{}, {'error':{'kind':'bad'},'events':['fail']})])
        spec=lab.study(path)
        self.assertEqual(spec['features']['has_error'],1)
        self.assertEqual(spec['features']['has_state'],1)
        self.assertEqual(spec['count'],2)

    def test_suggest_probes_are_not_claimed_observed(self):
        path=self.rows('seed',[self.record('edge',{'n':8,'txt':'a','flag':False},{'output':5})])
        proposed=lab.proposals(path)
        self.assertTrue(proposed['proposals'])
        self.assertTrue(all(row['status']=='not_observed' for row in proposed['proposals']))
        self.assertTrue(any(p['hypothesis']=='missing property' for p in proposed['proposals']))

    def test_numeric_tolerance_fail_closed(self):
        a=[self.record('x', 1, {'output':1})]
        for tol in [-1,float('nan'),float('inf')]:
            self.assertRaises(lab.DataError,self.compare_rows,a,a,tolerance=tol)

    def test_invalid_utf8_rejected(self):
        p=self.root/'bad.jsonl';p.write_bytes(b'\xff\n')
        self.assertRaises(lab.DataError,lab.load_corpus,p)

    def test_pointer_escaping(self):
        self.assertEqual(lab.pointer(('observation','a/b','x~y')),'/observation/a~1b/x~0y')

    def test_main_has_nonzero_exit_on_divergence(self):
        a=self.rows('a', [self.record('x',2,{'output':1})])
        b=self.rows('b', [self.record('x',2,{'output':2})])
        out=self.root/'diff.json'
        self.assertEqual(lab.main(['compare',str(a),str(b),'-o',str(out)]),1)
        self.assertEqual(json.loads(out.read_text())['counts']['mismatched'],1)

if __name__=='__main__':
    unittest.main()
