"""Focused regression tests for opt-in behavior contract v2 and failure-preserving shrink.

Only test trusted, locally defined fixtures and synthetic observations.
"""
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import behavior_lab as lab
import behavioral_pipeline as pipeline


class ContractV2Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def corpus(self, name, records):
        p = self.root / name
        p.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n'
                             for r in records), encoding='utf-8')
        return p

    def row(self, name='x', *, data=None, observation=None, version='2.0'):
        return {'id': name, 'input': {} if data is None else data,
                'observation': {'output': 1} if observation is None else observation,
                'schema_version': version}

    def must_reject(self, row):
        with self.assertRaises(lab.DataError):
            lab.load_corpus(self.corpus('bad.jsonl', [row]))

    def test_v1_does_not_get_v2_step_constraints(self):
        record = self.row(data={'actions': [{'x': 1}]},
                          observation={'output': 1, 'steps': [{'action_index': 99}]}, version='1.0')
        self.assertEqual(lab.load_corpus(self.corpus('old.jsonl', [record]))['x'], record)

    def test_v2_valid_steps(self):
        record = self.row(data={'actions': [{'op': 'push'}, {'op': 'read'}]},
                          observation={'steps': [{'action_index': 0, 'state': {'n': 1}},
                                                  {'action_index': 1, 'output': 1}],
                                       'effects': [{'kind': 'event', 'operation': 'published'}]})
        self.assertEqual(lab.load_corpus(self.corpus('ok.jsonl', [record]))['x'], record)

    def test_v2_rejects_out_of_order_or_boolean_action_index(self):
        for bad in (True, 1, -1, None):
            with self.subTest(bad=bad):
                record = self.row(data={'actions': [{'op': 'read'}]},
                                  observation={'steps': [{'action_index': bad, 'output': 1}],
                                               'output': 1})
                self.must_reject(record)

    def test_v2_rejects_partial_step_count(self):
        self.must_reject(self.row(data={'actions': [{'op': 'a'}, {'op': 'b'}]},
                                  observation={'steps': [{'action_index': 0, 'output': 1}],
                                               'output': 1}))

    def test_v2_rejects_invalid_effect(self):
        for effects in ({}, [{'kind': 'unknown', 'operation': 'commit'}],
                        [{'kind': 'database', 'operation': ''}], [{'kind': 'file'}]):
            with self.subTest(effects=effects):
                self.must_reject(self.row(observation={'output': 1, 'effects': effects}))

    def test_v2_requires_action_objects_if_present(self):
        self.must_reject(self.row(data={'actions': ['not-object']}))

    def test_v2_unknown_schema_is_error_not_silent(self):
        self.must_reject(self.row(version='3.0'))

    def test_v2_binary_envelope_accepts_canonical_base64(self):
        values = (b'', b'\x00\x01\x02', bytes(range(256)))
        for value in values:
            with self.subTest(size=len(value)):
                tag = {'$type': 'bytes', 'base64': base64.b64encode(value).decode()}
                record = self.row(observation={'output': {'nested': [tag]}})
                self.assertEqual(lab.load_corpus(self.corpus('bytes.jsonl', [record]))['x'], record)

    def test_v2_binary_envelope_rejects_noncanonical(self):
        for payload in ('AAE', 'AAE==', '$#', 'AA E=', 'aGVsbG8', '////\n'):
            with self.subTest(payload=payload):
                self.must_reject(self.row(observation={'output': {'$type': 'bytes', 'base64': payload}}))
        self.must_reject(self.row(observation={'output': {'$type': 'bytes', 'base64': 'AAE=', 'extra': 3}}))

    def test_v2_numeric_tolerance_never_normalizes_inputs(self):
        ref = [self.row(data={'n': 10}, observation={'output': 1.0})]
        cand = [self.row(data={'n': 10.001}, observation={'output': 1.001})]
        comparison = lab.compare(self.corpus('ref.jsonl', ref), self.corpus('cand.jsonl', cand), tolerance=0.1)
        self.assertEqual(comparison['counts']['mismatched'], 1)
        self.assertEqual(comparison['findings'][0]['diffs'][0]['pointer'], '/input/n')
        self.assertTrue(comparison['comparisons']['inputs_exact'])

    def test_v2_state_trace_order_matters(self):
        base = self.row(data={'actions': [{'op': 'a'}, {'op': 'b'}]},
                        observation={'output': 1, 'steps': [
                            {'action_index': 0, 'events': ['a']},
                            {'action_index': 1, 'events': ['b']}]})
        different = json.loads(json.dumps(base))
        different['observation']['steps'][0]['events'] = ['b']
        diff = lab.compare(self.corpus('ref.jsonl', [base]), self.corpus('cand.jsonl', [different]))
        self.assertEqual(diff['counts']['mismatched'], 1)
        self.assertIn('/observation/steps/0/events/0',
                      [x['pointer'] for x in diff['findings'][0]['diffs']])

    def test_characterization_manual_provenance(self):
        rows = [self.row('manual'), self.row('claimed')]
        rows[1]['runner_status'] = 'ok'
        result = lab.study(self.corpus('rows.jsonl', rows))
        statuses = {x['id']: x['status'] for x in result['obligations']}
        self.assertEqual(statuses, {'manual': 'supplied', 'claimed': 'claimed_runtime'})

    def test_sequence_probes_deterministic_and_hypothetical(self):
        initial = self.row(data={'actions': [{'op': 'add', 'n': 1}, {'op': 'read'}]})
        case = self.corpus('seq.jsonl', [initial])
        first = lab.proposals(case)
        self.assertEqual(first, lab.proposals(case))
        self.assertTrue(any('sequence' in x['hypothesis'] for x in first['proposals']))
        self.assertTrue(all(x['status'] == 'not_observed' for x in first['proposals']))
        self.assertTrue(all(x['input'] != initial['input'] for x in first['proposals']))


class SignatureTests(unittest.TestCase):
    def source(self, cmd, value, *_):
        n = value.get('n', 1)
        if cmd[0] == 'reference':
            return 'ok', {'output': {'value': n}}
        return ('ok', {'error': {'kind': 'alt'}}) if n == 0 else ('ok', {'output': {'value': n + 1}})

    def test_retains_first_failure_signature_default(self):
        with mock.patch.object(pipeline, 'run_one', side_effect=self.source):
            result = pipeline.shrink_one({'n': 4, 'unused': 'long'}, ['reference'], ['candidate'],
                                         Path('.'), Path('.'), 1, 10000, 0, max_trials=30)
        self.assertEqual(result['failure_signature']['kind'], 'value_mismatch')
        self.assertEqual(result['failure_signature']['pointer'], '/observation/output/value')
        self.assertTrue(result['preserved_signature'])
        self.assertNotEqual(result['input'].get('n', 1), 0)
        self.assertTrue(result['reduced'])

    def test_unverified_oracle_cannot_be_reduced(self):
        with mock.patch.object(pipeline, 'run_one', return_value=('timeout', {'error': 'timeout'})):
            result = pipeline.shrink_one({'n': 3}, ['reference'], ['candidate'],
                                         Path('.'), Path('.'), 1, 100, 0, max_trials=10)
        self.assertEqual(result['attempted_trials'], 0)
        self.assertFalse(result['reduced'])
        self.assertIsNone(result['failure_signature'])


if __name__ == '__main__':
    unittest.main()
