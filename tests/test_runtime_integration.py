"""Release-level contract for optional runtime integration and clean packages."""
from __future__ import annotations
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class RuntimeIntegrationTests(unittest.TestCase):
    def test_new_skill_is_complete_and_catalog_has_53_skills(self):
        skills = sorted(ROOT.glob('skills/*/SKILL.md'))
        self.assertEqual(len(skills), 53)
        self.assertTrue((ROOT / 'skills/operational-context/SKILL.md').is_file())
        for rel in ('SKILL.md', 'README.md', 'VERSION', 'agents/openai.yaml', 'contracts/runtime-query-v1.schema.json', 'contracts/runtime-handoff-v1.schema.json', 'scripts/runtime.py'):
            self.assertTrue((ROOT / 'skills/runtime-harness' / rel).is_file(), rel)

    def test_all_seven_agents_have_optional_runtime_guidance(self):
        agents = list(ROOT.glob('agents/*.agent.md'))
        self.assertEqual(len(agents), 7)
        for agent in agents:
            content = agent.read_text(encoding='utf-8')
            self.assertIn('## Optional runtime context', content, agent.name)
            self.assertIn('never replace domain handoffs', content, agent.name)
        for name in ('rhapsodia-supervisor', 'rhapsodia-analyst'):
            front = (ROOT / 'agents' / (name + '.agent.md')).read_text().split('---')[1]
            self.assertNotIn('execute', front)
            self.assertNotIn('edit', front)

    def test_repo_entrypoint_initializes_explicit_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT / 'scripts/runtime.py'), '--workspace', td, 'session-start'], capture_output=True, timeout=15)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)['schema'], 'runtime-session-v1')

    def test_private_state_is_excluded_from_release(self):
        builder = load('build_release_archive')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private = root / '.rhapsodia/runtime/current.json'
            private.parent.mkdir(parents=True)
            private.write_text('private observations')
            example = root / '.env.example'
            example.write_text('SAMPLE=')
            with patch.object(builder, 'ROOT', root):
                self.assertFalse(builder.include(private))
                self.assertTrue(builder.include(example))

    def test_private_packaging_names_are_case_insensitive(self):
        builder = load('build_release_archive')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative in ('.RHAPSODIA/runtime/current.json', '.ENV', '.ENV.production'):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('private')
                with patch.object(builder, 'ROOT', root):
                    self.assertFalse(builder.include(path), relative)

    def test_invalid_release_version_cannot_create_zip_entries(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'bad.zip'
            p = subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT / 'scripts/build_release_archive.py'), '--version', '../../escape', '--output', str(out)], capture_output=True, timeout=15)
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse(out.exists())

    def test_portable_builder_does_not_destroy_existing_output(self):
        builder = load('build_portable_agent_plugin')
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'existing'
            target.mkdir()
            keep = target / 'keep.txt'
            keep.write_text('user data')
            with self.assertRaises(ValueError):
                builder.build(target)
            self.assertEqual(keep.read_text(), 'user data')

    def test_portable_builder_blocks_source_overlap(self):
        builder = load('build_portable_agent_plugin')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'skills/example').mkdir(parents=True)
            with patch.object(builder, 'ROOT', root):
                with self.assertRaises(ValueError):
                    builder.build(root / 'skills/example/output')

    def test_portable_builder_excludes_runtime_state(self):
        builder = load('build_portable_agent_plugin')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'source'
            root.mkdir()
            skill = root / 'skills/example'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('# sample')
            (skill / '.rhapsodia/runtime').mkdir(parents=True)
            (skill / '.rhapsodia/runtime/current.json').write_text('private')
            (skill / '__pycache__').mkdir()
            (skill / '__pycache__/module.pyc').write_bytes(b'residue')
            output = Path(td) / 'output'
            with patch.object(builder, 'ROOT', root):
                builder.build(output)
            self.assertTrue((output / 'skills/example/SKILL.md').is_file())
            self.assertFalse((output / 'skills/example/.rhapsodia').exists())
            self.assertFalse((output / 'skills/example/__pycache__').exists())

    def test_installer_reports_actual_count_without_runtime_prerequisite(self):
        installer = load('install_agents')
        self.assertNotIn('runtime-harness', installer.REQUIRED_SKILLS)
        stream = io.StringIO()
        with patch.object(sys, 'argv', ['installer', '--target', str(ROOT), '--check']), patch.object(installer, 'check_installation', return_value=[]), contextlib.redirect_stdout(stream):
            self.assertEqual(installer.main(), 0)
        self.assertIn('7 agent profiles', stream.getvalue())

    def test_multiplatform_ci_is_present_not_assumed_executed(self):
        text = (ROOT / '.github/workflows/runtime-portability.yml').read_text()
        for os in ('ubuntu-latest', 'windows-latest', 'macos-latest'):
            self.assertIn(os, text)
        self.assertIn('3.10', text)
        self.assertIn('3.14', text)
        self.assertNotIn('continue-on-error: true', text)

if __name__ == '__main__':
    unittest.main()
