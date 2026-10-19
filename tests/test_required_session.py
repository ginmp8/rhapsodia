"""Executable contract for mandatory, opt-out-aware agent sessions and memory."""
from __future__ import annotations
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / 'scripts/session.py'
MEMORY = ROOT / 'scripts/memory.py'


class SessionMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / 'workspace with spaces'
        self.workspace.mkdir()
        self.source = self.workspace / 'example.py'
        self.source.write_text('def answer():\n    return 42\n', encoding='utf-8')

    def call(self, entry, *args, data=None, ok=True, env=None):
        self.assertTrue(entry.is_file(), f'missing required executable: {entry.name}')
        proc = subprocess.run([sys.executable, '-I', '-S', '-B', str(entry), '--workspace', str(self.workspace), *args],
                              input=None if data is None else json.dumps(data).encode(), capture_output=True, timeout=25, env=env)
        try:
            result = json.loads(proc.stdout)
        except ValueError:
            self.fail(f'expected JSON: {proc.stdout!r} {proc.stderr!r}')
        if ok:
            self.assertEqual(proc.returncode, 0, (result, proc.stderr.decode()))
        else:
            self.assertNotEqual(proc.returncode, 0, result)
        return result

    def session(self, *args, **kwargs):
        return self.call(SESSION, '--skills-root', str(ROOT / 'skills'), *args, **kwargs)

    def memory(self, *args, **kwargs):
        return self.call(MEMORY, *args, **kwargs)

    def reference(self, key='answer-location'):
        return {'schema': 'workspace-knowledge-v1', 'key': key, 'kind': 'reference',
                'title': 'Answer function location', 'summary': 'The answer function is defined in example.py.',
                'tags': ['answer', 'function'], 'sources': [{'path': 'example.py', 'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}]}

    def remedy(self, key='shell-method-limit'):
        return {'schema': 'workspace-knowledge-v1', 'key': key, 'kind': 'remedy',
                'title': 'Shell method invocation restriction', 'summary': 'Check the active shell language mode before choosing syntax.',
                'tags': ['powershell', 'language-mode'], 'sources': [],
                'symptom': 'Method invocation is supported only on core types in this language mode.',
                'cause': 'The active session restricts method invocation.',
                'resolution': 'Use approved cmdlets; do not disable policy or switch interpreters to evade it.',
                'verification': 'A permitted read-only cmdlet completed in the observed session.',
                'evidence_status': 'observed-success', 'applicability': {'shell': 'powershell', 'language_mode': 'ConstrainedLanguage'},
                'environment_variables': ['PATH'], 'ttl_seconds': 86400}

    def test_cold_start_creates_real_harness_and_graph(self):
        result = self.session()
        self.assertEqual(result['status'], 'ready')
        self.assertTrue((self.workspace / '.rhapsodia/runtime/current.json').is_file())
        self.assertTrue((self.workspace / '.rhapsodia/graph/workspace.sqlite3').is_file())
        self.assertEqual(result['harness']['status'], 'ready')
        self.assertEqual(result['graph']['status'], 'ready')
        self.assertTrue(result['memory_argv'])

    def test_warm_start_reuses_snapshot_and_graph(self):
        first = self.session()
        second = self.session()
        self.assertEqual(first['harness']['snapshot_id'], second['harness']['snapshot_id'])
        self.assertTrue(second['harness']['cache_hit'])
        self.assertTrue(second['graph']['cache_hit'])

    def test_warm_start_never_rescans_skill_directory(self):
        self.session()
        code = """import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import agent_session
args = agent_session.parser().parse_args(['--workspace', sys.argv[2], '--skills-root', sys.argv[3]])
with patch.object(Path, 'iterdir', side_effect=AssertionError('warm skill rescan')):
    result = agent_session.start(args)
assert result['harness']['cache_hit'] is True
"""
        proc = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', code,
                               str(ROOT / 'skills/runtime-harness/scripts'), str(self.workspace), str(ROOT / 'skills')],
                              capture_output=True, text=True, timeout=25)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_stale_remedy_requires_explicit_revision_and_can_be_reverified(self):
        self.session()
        first = self.memory('learn', data=self.remedy())
        env = dict(os.environ, PATH=os.environ.get('PATH', '') + os.pathsep + str(self.workspace / 'new-tool-root'))
        result = self.memory('learn', data=self.remedy(), env=env, ok=False)
        self.assertEqual(result['error']['code'], 'REVISION_CONFLICT')
        updated = dict(self.remedy(), expected_revision=first['revision'])
        second = self.memory('learn', data=updated, env=env)
        self.assertTrue(second['mutated'])
        hit = self.memory('lookup', 'shell', env=env)['hits'][0]
        self.assertEqual(hit['freshness'], 'fresh')

    def test_narrow_reconcile_scales_past_global_record_limit(self):
        self.session()
        self.memory('learn', data=self.reference())
        (self.workspace / 'unrelated.py').write_text('unrelated = True\n')
        code = """import sys,time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from workspace_memory_core import WorkspaceMemory
from workspace_memory_contract import pin
from graph_store import apply_patches
memory=WorkspaceMemory(Path(sys.argv[2]))
source=pin(memory.workspace, 'unrelated.py')
patches=[]
for index in range(1030):
    note={'schema':'workspace-knowledge-v1','key':'unrelated-'+str(index),'kind':'reference',
          'title':'Unrelated reference','summary':'Synthetic scale fixture','tags':[],
          'sources':[source], '_recorded_at':time.time()}
    patches.append(memory.patch_for(note))
with memory.writer():
    apply_patches(memory.db, patches)
"""
        proc = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', code,
                               str(ROOT / 'skills/local-graph-engine/scripts'), str(self.workspace)],
                              capture_output=True, text=True, timeout=25)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.source.write_text('changed = True\n')
        result = self.memory('reconcile', '--paths', 'example.py')
        self.assertEqual(result['checked'], 1)
        self.assertEqual(result['stale'], 1)

    def test_independent_no_graph(self):
        result = self.session('--no-graph', '--opt-out-reason', 'user-request')
        self.assertEqual(result['graph']['status'], 'disabled-by-user')
        self.assertTrue((self.workspace / '.rhapsodia/runtime/current.json').is_file())
        self.assertFalse((self.workspace / '.rhapsodia/graph').exists())

    def test_independent_no_harness(self):
        result = self.session('--no-harness', '--opt-out-reason', 'user-request')
        self.assertEqual(result['harness']['status'], 'disabled-by-user')
        self.assertFalse((self.workspace / '.rhapsodia/runtime').exists())
        self.assertTrue((self.workspace / '.rhapsodia/graph/workspace.sqlite3').is_file())

    def test_both_disabled_do_not_touch_local_state(self):
        result = self.session('--no-harness', '--no-graph', '--opt-out-reason', 'user-request')
        self.assertEqual(result['status'], 'ready')
        self.assertFalse((self.workspace / '.rhapsodia').exists())

    def test_optout_requires_explicit_reason(self):
        result = self.session('--no-graph', ok=False)
        self.assertEqual(result['error']['code'], 'OPT_OUT_REQUIRED')
        self.assertFalse((self.workspace / '.rhapsodia').exists())

    def test_missing_graph_skill_blocks_not_silent_fallback(self):
        empty = self.workspace / 'empty-skills'
        empty.mkdir()
        result = self.call(SESSION, '--skills-root', str(empty), ok=False)
        self.assertEqual(result['error']['code'], 'GRAPH_UNAVAILABLE')

    def test_corrupt_harness_is_preserved_and_blocks(self):
        self.session()
        pointer = self.workspace / '.rhapsodia/runtime/current.json'
        pointer.write_text('{broken', encoding='utf-8')
        result = self.session(ok=False)
        self.assertEqual(result['error']['code'], 'CORRUPT_STATE')
        self.assertEqual(pointer.read_text(), '{broken')

    def test_lookup_before_start_is_readonly_miss(self):
        result = self.memory('lookup', 'answer')
        self.assertEqual(result['status'], 'not-initialized')
        self.assertFalse((self.workspace / '.rhapsodia').exists())

    def test_pin_does_not_write(self):
        result = self.memory('pin', 'example.py')
        self.assertEqual(result['sources'], self.reference()['sources'])
        self.assertFalse((self.workspace / '.rhapsodia').exists())

    def test_learn_lookup_and_idempotent_publication(self):
        self.session()
        first = self.memory('learn', data=self.reference())
        second = self.memory('learn', data=self.reference())
        self.assertEqual(first['revision'], second['revision'])
        self.assertFalse(second['mutated'])
        hit = self.memory('lookup', 'answer')['hits'][0]
        self.assertEqual(hit['key'], 'answer-location')
        self.assertEqual(hit['freshness'], 'fresh')
        self.assertEqual(hit['sources'], self.reference()['sources'])

    def test_changed_source_is_stale_not_reusable(self):
        self.session()
        self.memory('learn', data=self.reference())
        self.source.write_text('def answer(): return 99\n')
        hit = self.memory('lookup', 'answer')['hits'][0]
        self.assertEqual(hit['freshness'], 'stale')
        self.assertFalse(hit['reusable'])
        self.assertIn('source-changed', hit['reasons'])

    def test_wrong_pin_is_rejected(self):
        self.session()
        note = self.reference()
        note['sources'][0]['sha256'] = '0' * 64
        result = self.memory('learn', data=note, ok=False)
        self.assertEqual(result['error']['code'], 'STALE_SOURCE')
        self.assertFalse(self.memory('lookup', 'answer')['hits'])

    def test_changed_note_requires_revision(self):
        self.session()
        first = self.memory('learn', data=self.reference())
        changed = self.reference()
        changed['summary'] = 'Updated bounded explanation.'
        self.memory('learn', data=changed, ok=False)
        changed['expected_revision'] = first['revision']
        next_result = self.memory('learn', data=changed)
        self.assertNotEqual(first['revision'], next_result['revision'])

    def test_missing_source_is_invalidated_not_silently_deleted(self):
        self.session()
        self.memory('learn', data=self.reference())
        self.source.unlink()
        result = self.memory('reconcile')
        self.assertEqual(result['stale'], 1)
        self.assertEqual(result['pruned'], 0)
        self.assertFalse(self.memory('lookup', 'answer')['hits'][0]['reusable'])

    def test_prune_requires_complete_scope_confirmation(self):
        self.session()
        self.memory('learn', data=self.reference())
        self.source.unlink()
        self.memory('reconcile', '--prune-missing', ok=False)
        result = self.memory('reconcile', '--prune-missing', '--confirm-complete-scope')
        self.assertEqual(result['pruned'], 1)
        self.assertFalse(self.memory('lookup', 'answer')['hits'])
        import sqlite3
        with closing(sqlite3.connect(self.workspace / '.rhapsodia/graph/workspace.sqlite3')) as con:
            self.assertGreater(con.execute('SELECT COUNT(*) FROM source_revisions').fetchone()[0], 1)

    def test_remedy_is_persisted_with_applicability_not_automatic_proof(self):
        self.session()
        self.memory('learn', data=self.remedy())
        hit = self.memory('lookup', 'powershell')['hits'][0]
        self.assertEqual(hit['evidence_status'], 'observed-success')
        self.assertEqual(hit['evidence_basis'], 'agent-reported')
        self.assertTrue(hit['requires_applicability_check'])
        self.assertIn('resolution', hit)

    def test_hypothesis_is_not_a_reusable_resolution(self):
        self.session()
        note = self.remedy()
        note['evidence_status'] = 'hypothesis'
        self.memory('learn', data=note)
        self.assertFalse(self.memory('lookup', 'powershell')['hits'][0]['reusable'])

    def test_secret_assignment_is_rejected_without_echo(self):
        self.session()
        note = self.remedy()
        secret = 'private-credential-value'
        note['resolution'] = 'Set AWS_SECRET_ACCESS_KEY=' + secret
        result = self.memory('learn', data=note, ok=False)
        self.assertEqual(result['error']['code'], 'SENSITIVE_INPUT')
        self.assertNotIn(secret, json.dumps(result))

    def test_environment_values_are_not_an_accepted_field(self):
        self.session()
        note = self.remedy()
        note['environment_values'] = {'PATH': 'some value'}
        self.memory('learn', data=note, ok=False)

    def test_protected_source_path_is_refused(self):
        private = self.workspace / '.env'
        private.write_text('SECRET=value')
        self.memory('pin', '.env', ok=False)
        self.assertFalse((self.workspace / '.rhapsodia').exists())

    def test_path_escape_is_refused(self):
        self.memory('pin', '../outside', ok=False)
        self.assertFalse((self.workspace / '.rhapsodia').exists())

    def test_state_symlink_is_refused(self):
        other = Path(self.temp.name) / 'other'
        other.mkdir()
        try:
            (self.workspace / '.rhapsodia').symlink_to(other, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        self.session(ok=False)
        self.assertEqual(list(other.iterdir()), [])

    def test_lookup_budget_is_bounded_and_explicit(self):
        self.session()
        for number in range(4):
            self.memory('learn', data=self.reference('answer-' + str(number)))
        result = self.memory('lookup', 'answer', '--budget-bytes', '1600')
        self.assertLessEqual(len((json.dumps(result, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()), 1600)
        self.assertTrue(result['truncated'])

    def test_reserved_identity_cannot_replace_workspace_root(self):
        self.session()
        self.memory('learn', data=self.reference('root'), ok=False)
        self.memory('learn', data=self.reference('workspace'), ok=False)

    def test_environment_change_invalidates_recipe(self):
        self.session()
        self.memory('learn', data=self.remedy())
        env = dict(os.environ, PATH=str(self.workspace))
        hit = self.memory('lookup', 'powershell', env=env)['hits'][0]
        self.assertIn('environment-changed', hit['reasons'])
        self.assertFalse(hit['reusable'])

    def test_copied_graph_is_not_rebound_to_another_workspace(self):
        import shutil
        self.session()
        original = self.workspace
        other = Path(self.temp.name) / 'other-workspace'
        other.mkdir()
        shutil.copytree(original / '.rhapsodia/graph', other / '.rhapsodia/graph')
        self.workspace = other
        result = self.memory('start', ok=False)
        self.assertEqual(result['error']['code'], 'SCOPE_MISMATCH')

    def test_concurrent_distinct_records_are_preserved(self):
        from concurrent.futures import ThreadPoolExecutor
        self.session()
        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(lambda number: self.memory('learn', data=self.reference('parallel-' + str(number))), range(4)))
        self.assertEqual(len(self.memory('lookup', 'Answer')['hits']), 4)

    def test_lookup_does_not_modify_database(self):
        self.session()
        self.memory('learn', data=self.reference())
        db = self.workspace / '.rhapsodia/graph/workspace.sqlite3'
        before = db.read_bytes()
        self.memory('lookup', 'answer')
        self.assertEqual(before, db.read_bytes())

    def test_readonly_lookup_rejects_symlinked_database(self):
        self.session()
        db = self.workspace / '.rhapsodia/graph/workspace.sqlite3'
        destination = Path(self.temp.name) / 'external.sqlite3'
        destination.write_bytes(db.read_bytes())
        db.unlink()
        try:
            db.symlink_to(destination)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        self.memory('lookup', 'answer', ok=False)

    def test_hardlinked_database_cannot_be_mutated(self):
        self.session()
        db = self.workspace / '.rhapsodia/graph/workspace.sqlite3'
        try:
            os.link(db, Path(self.temp.name) / 'alias.sqlite3')
        except OSError:
            self.skipTest('hardlinks unavailable')
        self.memory('learn', data=self.reference(), ok=False)

    def test_reconcile_preserves_multi_source_knowledge(self):
        self.session()
        second = self.workspace / 'other.py'
        second.write_text('OTHER = 1')
        note = self.reference()
        note['sources'].append({'path': 'other.py', 'sha256': hashlib.sha256(second.read_bytes()).hexdigest()})
        self.memory('learn', data=note)
        self.source.unlink()
        result = self.memory('reconcile', '--prune-missing', '--confirm-complete-scope')
        self.assertEqual(result['pruned'], 0)
        self.assertEqual(len(self.memory('lookup', 'answer')['hits']), 1)

    def test_all_agents_require_bootstrap_with_explicit_optouts_in_top100(self):
        agents = list((ROOT / 'agents').glob('*.agent.md'))
        self.assertEqual(len(agents), 8)
        for path in agents:
            text = '\n'.join(path.read_text(encoding='utf-8').splitlines()[:100])
            for marker in ('## Mandatory session and memory', 'agent_session.py', '--no-harness', '--no-graph', 'graph-first', 'reconcile', 'blocked'):
                self.assertIn(marker, text, (path.name, marker))
        adhoc = (ROOT / 'agents/rhapsodia-adhoc.agent.md').read_text()
        self.assertIn('no subagent orchestration', adhoc)


if __name__ == '__main__':
    unittest.main()
