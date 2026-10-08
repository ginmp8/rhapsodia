"""Final contract, recovery and platform adapter acceptance tests."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from runtime_core.common import RuntimeFault, atomic_batch, canonical, sha
from runtime_core.store import Store
from runtime_core.graph import export_graph


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='runtime delivery ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'skills/example').mkdir(parents=True)
        (self.root / 'skills/example/SKILL.md').write_text('# example\n', encoding='utf-8')
        self.store = Store(self.root)
        self.store.initialize()

    def call(self, *args):
        p = subprocess.run([sys.executable, '-I', '-S', '-B', str(SKILL / 'scripts/runtime.py'), '--workspace', str(self.root), *args], capture_output=True, timeout=20)
        return p, json.loads(p.stdout)

    def test_graph_source_is_stable_within_environment(self):
        first = export_graph(self.store)
        self.store.initialize(refresh=True)
        second = export_graph(self.store)
        self.assertEqual(first['source']['uri'], second['source']['uri'])
        self.assertNotEqual(first['source']['content_hash'], second['source']['content_hash'])

    def test_added_agent_invalidates_catalog(self):
        (self.root / 'agents').mkdir()
        (self.root / 'agents/example.agent.md').write_text('# example\n', encoding='utf-8')
        with self.assertRaises(RuntimeFault) as ctx:
            self.store.current()
        self.assertEqual(ctx.exception.code, 'STALE_CATALOG')
        self.assertFalse(self.store.initialize()['cache_hit'])

    def test_self_consistent_but_malformed_snapshot_is_rejected(self):
        _, snapshot = self.store.current()
        snapshot['tools'] = ['not a mapping']
        key = sha(snapshot)
        (self.store.root / 'snapshots' / (key + '.json')).write_bytes(canonical(snapshot))
        pointer = json.loads((self.store.root / 'current.json').read_bytes())
        pointer['snapshot_id'] = key
        pointer['snapshot_file'] = 'snapshots/' + key + '.json'
        (self.store.root / 'current.json').write_bytes(canonical(pointer))
        with self.assertRaises(RuntimeFault) as ctx:
            self.store.current()
        self.assertEqual(ctx.exception.code, 'CORRUPT_STATE')

    def test_configuration_batch_rolls_back_own_changes(self):
        import runtime_core.common as common
        (self.root / 'a.txt').write_bytes(b'old-a')
        (self.root / 'b.txt').write_bytes(b'old-b')
        original = common.atomic_write
        def fail_second(root, relative, data, **kwargs):
            if relative == 'b.txt' and data == b'new-b':
                raise OSError('injected failure')
            return original(root, relative, data, **kwargs)
        with patch.object(common, 'atomic_write', side_effect=fail_second):
            with self.assertRaises((OSError, RuntimeFault)):
                atomic_batch([(self.root, 'a.txt', b'old-a', b'new-a'), (self.root, 'b.txt', b'old-b', b'new-b')])
        self.assertEqual((self.root / 'a.txt').read_bytes(), b'old-a')
        self.assertEqual((self.root / 'b.txt').read_bytes(), b'old-b')

    def test_bootstrap_argv_tampering_is_not_reused(self):
        pointer = self.store.root / 'current.json'
        body = json.loads(pointer.read_bytes())
        body['runtime_argv'][0] = '/unrelated/executable'
        pointer.write_bytes(canonical(body))
        with self.assertRaises(RuntimeFault) as ctx:
            self.store.current()
        self.assertEqual(ctx.exception.code, 'CORRUPT_STATE')

    def test_python_record_must_match_running_interpreter(self):
        _, snapshot = self.store.current()
        snapshot['tools']['python']['argv'] = ['/unrelated/python']
        key = sha(snapshot)
        (self.store.root / 'snapshots' / (key + '.json')).write_bytes(canonical(snapshot))
        path = self.store.root / 'current.json'
        pointer = json.loads(path.read_bytes())
        pointer['snapshot_id'] = key
        pointer['snapshot_file'] = 'snapshots/' + key + '.json'
        pointer['python_argv'] = ['/unrelated/python']
        pointer['runtime_argv'][0] = '/unrelated/python'
        path.write_bytes(canonical(pointer))
        with self.assertRaises(RuntimeFault):
            self.store.current()

    def test_session_start_preserves_selected_expiry_policy(self):
        self.store.initialize(max_age=60)
        proc, body = self.call('session-start')
        self.assertEqual(proc.returncode, 0, body)
        self.assertTrue(body['cache_hit'])
        _, snapshot = self.store.current()
        self.assertEqual(snapshot['max_age_seconds'], 60)

    def test_session_start_returns_small_reusable_card(self):
        proc, body = self.call('session-start')
        self.assertEqual(proc.returncode, 0, body)
        self.assertTrue(body['cache_hit'])
        self.assertIn('runtime_argv', body)
        self.assertLess(len(proc.stdout), 4096)
        self.assertNotIn('skills', body)

    def test_vscode_session_start_output_is_host_adapter_only(self):
        proc, body = self.call('session-start', '--format', 'vscode-local')
        self.assertEqual(proc.returncode, 0, body)
        self.assertEqual(body['hookSpecificOutput']['hookEventName'], 'SessionStart')
        self.assertIn('observations', body['hookSpecificOutput']['additionalContext'])
        self.assertNotIn('continue', body)

    def test_mcp_config_is_argv_not_shell(self):
        proc, body = self.call('mcp-config')
        self.assertEqual(proc.returncode, 0, body)
        self.assertEqual(body['command'], os.path.abspath(sys.executable))
        self.assertEqual(body['args'][-1], 'mcp')
        self.assertIn('-S', body['args'])
        self.assertNotIn('env', body)
        self.assertFalse((self.root / '.vscode/mcp.json').exists())

    def test_virtual_environment_identity_survives_isolated_no_site(self):
        env = self.root / 'virtual environment'
        p = subprocess.run([sys.executable, '-I', '-S', '-m', 'venv', '--without-pip', str(env)], capture_output=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        exe = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        p = subprocess.run([str(exe), '-I', '-S', '-B', str(SKILL / 'scripts/runtime.py'), '--workspace', str(self.root), 'init'], capture_output=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        card = json.loads((self.store.root / 'current.json').read_bytes())
        self.assertEqual(os.path.normcase(card['python_argv'][0]), os.path.normcase(str(exe)))

    @unittest.skipUnless(shutil.which('pwsh') or shutil.which('powershell'), 'PowerShell unavailable on this host')
    def test_powershell_bootstrap(self):
        shell = shutil.which('pwsh') or shutil.which('powershell')
        proc = subprocess.run([shell, '-NoLogo', '-NoProfile', '-File', str(SKILL / 'scripts/bootstrap.ps1'), '--workspace', str(self.root), 'init'], env=dict(os.environ, RHAPSODIA_PYTHON=sys.executable), capture_output=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['status'], 'ready')


if __name__ == '__main__':
    unittest.main()
