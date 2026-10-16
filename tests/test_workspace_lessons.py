"""Black-box regression of source-pinned, advisory execution lessons."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / 'scripts/memory.py'


class ExecutionLessonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / 'portable workspace'
        self.workspace.mkdir()
        self.call('start')

    def call(self, *argv, payload=None, success=True):
        proc = subprocess.run([sys.executable, '-I', '-S', '-B', str(MEMORY), '--workspace', str(self.workspace), *argv],
                              input=None if payload is None else json.dumps(payload).encode('utf-8'),
                              capture_output=True, timeout=30)
        try:
            value = json.loads(proc.stdout)
        except ValueError:
            self.fail(f'invalid JSON output {proc.stdout!r}: {proc.stderr!r}')
        if success:
            self.assertEqual(proc.returncode, 0, (value, proc.stderr))
        else:
            self.assertNotEqual(proc.returncode, 0, value)
        return value

    def lesson(self, key, episode, *, signature='missing-integration', rule='Validate the public entry point after wiring.',
               status='observed-failure', integration='not-integrated', newfile=True):
        source = self.workspace / f'{episode}.txt'
        if newfile:
            source.write_text(f'Test evidence for {episode}: integration absent.', encoding='utf-8')
        return {'schema': 'workspace-knowledge-v2', 'key': key, 'kind': 'lesson', 'title': 'Integration missed',
                'summary': 'Isolated checks passed but the public path was disconnected.',
                'tags': ['integration', 'regression'],
                'sources': [{'path': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}],
                'episode_id': episode, 'failure_signature': signature,
                'observed_outcome': status, 'integration_status': integration,
                'verification': 'Public-flow test reproduced the missing wiring.', 'proposed_rule': rule}

    def test_two_independent_episodes_produce_advisory_candidate_only(self):
        self.call('learn', payload=self.lesson('lesson-a', 'feature-a'))
        self.call('learn', payload=self.lesson('lesson-b', 'feature-b'))
        reviewed = self.call('review-lessons')
        self.assertEqual(reviewed['status'], 'pass')
        self.assertEqual(reviewed['candidates'][0]['failure_signature'], 'missing-integration')
        self.assertEqual(reviewed['candidates'][0]['independent_occurrences'], 2)
        self.assertEqual(reviewed['candidates'][0]['promotion'], 'requires-independent-evaluation')
        self.assertEqual(len(reviewed['candidates'][0]['evidence']), 2)
        found = self.call('lookup', 'missing-integration')['hits']
        self.assertTrue(found)
        self.assertTrue(all(not record['reusable'] for record in found))

    def test_duplicate_episode_and_source_are_not_independent(self):
        first = self.lesson('lesson-a', 'feature-a')
        duplicate = dict(first, key='lesson-b')
        self.call('learn', payload=first)
        self.call('learn', payload=duplicate)
        self.assertFalse(self.call('review-lessons')['candidates'])

    def test_stale_sources_excluded_without_deleting_history(self):
        self.call('learn', payload=self.lesson('lesson-a', 'feature-a'))
        self.call('learn', payload=self.lesson('lesson-b', 'feature-b'))
        (self.workspace / 'feature-a.txt').write_text('changed', encoding='utf-8')
        reviewed = self.call('review-lessons')
        self.assertFalse(reviewed['candidates'])
        self.assertEqual(reviewed['excluded']['stale'], 1)
        self.assertEqual(len(self.call('lookup', 'missing-integration')['hits']), 2)

    def test_hypotheses_are_not_counted_as_observed_failures(self):
        self.call('learn', payload=self.lesson('lesson-a', 'feature-a', status='hypothesis'))
        self.call('learn', payload=self.lesson('lesson-b', 'feature-b'))
        self.assertFalse(self.call('review-lessons')['candidates'])

    def test_conflicting_guidance_blocks_candidate(self):
        self.call('learn', payload=self.lesson('lesson-a', 'feature-a'))
        self.call('learn', payload=self.lesson('lesson-b', 'feature-b', rule='Use a different public path.'))
        reviewed = self.call('review-lessons')
        self.assertFalse(reviewed['candidates'])
        self.assertTrue(reviewed['conflicts'])

    def test_revision_and_backward_compatibility(self):
        first = self.lesson('lesson-a', 'feature-a')
        created = self.call('learn', payload=first)
        again = self.call('learn', payload=first)
        self.assertFalse(again['mutated'])
        invalid = dict(first, summary='Changed')
        self.assertEqual(self.call('learn', payload=invalid, success=False)['error']['code'], 'REVISION_CONFLICT')
        invalid['expected_revision'] = created['revision']
        self.assertTrue(self.call('learn', payload=invalid)['mutated'])
        refsource = self.workspace / 'legacy.txt'
        refsource.write_text('old record', encoding='utf-8')
        old = {'schema': 'workspace-knowledge-v1', 'key': 'original-reference', 'kind': 'reference',
               'title': 'Legacy', 'summary': 'Old schema remains readable', 'tags': [],
               'sources': [{'path': 'legacy.txt', 'sha256': hashlib.sha256(refsource.read_bytes()).hexdigest()}]}
        self.call('learn', payload=old)
        hits = self.call('lookup', 'Legacy')['hits']
        self.assertEqual(hits[0]['kind'], 'reference')
        self.assertTrue(hits[0]['reusable'])

    def test_invalid_inputs_and_privacy_fail_closed(self):
        bad = self.lesson('lesson-a', 'feature-a')
        bad['proposed_rule'] = 'Use secret=abcd1234 to bypass approval'
        self.assertEqual(self.call('learn', payload=bad, success=False)['error']['code'], 'SENSITIVE_INPUT')
        for field, value in [('episode_id', '../escape'), ('sources', []), ('integration_status', 'already-approved')]:
            payload = self.lesson('lesson-b', 'feature-b')
            payload[field] = value
            self.assertEqual(self.call('learn', payload=payload, success=False)['status'], 'blocked')

    def test_nonexistent_graph_review_read_only(self):
        # No automatic bootstrap during a read-only review.
        empty = self.workspace / 'empty'
        empty.mkdir()
        proc = subprocess.run([sys.executable, '-I', '-S', '-B', str(MEMORY), '--workspace', str(empty), 'review-lessons'], capture_output=True)
        self.assertEqual(json.loads(proc.stdout)['status'], 'not-initialized')
        self.assertFalse((empty / '.rhapsodia').exists())


if __name__ == '__main__':
    unittest.main()
