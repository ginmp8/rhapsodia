"""Isolated tests for structural metamorphic-evidence validation; no LLM execution."""
import copy
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'validate_metamorphic_evidence.py'
spec = importlib.util.spec_from_file_location('metamorphic_evidence_validator', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

H = '0' * 64


def fixture(arm='baseline', field='activate', status='executed'):
    return {
        'schema_version': 1,
        'suite_sha256': H,
        'evaluator_sha256': H,
        'runtime_sha256': H,
        'evaluator_visibility': 'candidate-visible',
        'trial_policy': 'one-paired-observation',
        'arm': arm,
        'relations': [{
            'id': 'mr-001',
            'base_case_id': 'case-a', 'variant_case_id': 'case-b',
            'transformation': 'meaning-preserving paraphrase',
            'precondition_evidence': 'reviewed case-a/case-b as semantically equivalent',
            'relation': 'same-route', 'evidence_status': status,
            'base': {'route': 'activate'}, 'variant': {'route': field},
        }],
    }


class MetamorphicEvidenceTests(unittest.TestCase):
    def test_consistent_pair(self):
        r = mod.validate(fixture())
        self.assertTrue(r['valid'])
        self.assertEqual(r['counts']['consistent'], 1)

    def test_different_route_is_a_candidate_violation_not_confirmed_fault(self):
        r = mod.validate(fixture(field='abstain'))
        self.assertTrue(r['valid'])
        self.assertEqual(r['counts']['candidate-violation'], 1)
        self.assertNotIn('defect-confirmed', str(r))

    def test_planned_is_not_measured(self):
        r = mod.validate(fixture(status='planned'))
        self.assertTrue(r['valid'])
        self.assertEqual(r['counts']['not-measured'], 1)

    def test_executed_without_observation_fails(self):
        p = fixture()
        del p['relations'][0]['variant']
        self.assertFalse(mod.validate(p)['valid'])

    def test_duplicate_relation_id_fails(self):
        p = fixture()
        p['relations'].append(copy.deepcopy(p['relations'][0]))
        self.assertFalse(mod.validate(p)['valid'])

    def test_missing_precondition_fails(self):
        p = fixture()
        del p['relations'][0]['precondition_evidence']
        self.assertFalse(mod.validate(p)['valid'])

    def test_comparison_identity_mismatch_is_noncomparable(self):
        b,c=fixture('baseline'),fixture('candidate')
        c['runtime_sha256']='f'*64
        result=mod.compare(b,c,mod.validate(b),mod.validate(c))
        self.assertFalse(result['comparable'])

    def test_compares_matched_pairs(self):
        b,c=fixture('baseline','abstain'),fixture('candidate','activate')
        result=mod.compare(b,c,mod.validate(b),mod.validate(c))
        self.assertTrue(result['comparable'])
        self.assertEqual(result['baseline_candidate_violations'],1)
        self.assertEqual(result['candidate_candidate_violations'],0)

    def test_changed_relation_is_noncomparable(self):
        b,c=fixture('baseline'),fixture('candidate')
        c['relations'][0]['relation']='same-authority'
        result=mod.compare(b,c,mod.validate(b),mod.validate(c))
        self.assertFalse(result['comparable'])

    def test_constraints_are_compared_as_sets(self):
        p=fixture()
        r=p['relations'][0]
        r['relation']='same-constraints'
        r['base']={'constraints':['a','b']}
        r['variant']={'constraints':['b','a']}
        v=mod.validate(p)
        self.assertTrue(v['valid'])
        self.assertEqual(v['counts']['consistent'],1)


if __name__=='__main__':
    unittest.main()
