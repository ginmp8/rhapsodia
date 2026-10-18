"""Structural regression tests. These are NOT behavioral agent evaluations."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import validate_analysis, validate_skill  # noqa: E402


class AnalysisContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'assets/analysis.schema.json').read_text())
        cls.sample = json.loads((ROOT / 'examples/sample-analysis.json').read_text())

    def test_valid_example(self):
        self.assertEqual([], validate_analysis.validate(self.sample, self.schema))

    def test_reject_dangling_source(self):
        bad = copy.deepcopy(self.sample)
        bad['claims'][0]['source_ids'] = ['SRC-999']
        self.assertTrue(any('source SRC-999 is absent' in x for x in validate_analysis.validate(bad, self.schema)))

    def test_reject_observed_runtime_without_runtime_evidence(self):
        bad = copy.deepcopy(self.sample)
        bad['claims'][0]['status'] = 'runtime-observed'
        self.assertTrue(any('requires an appropriate evidence source kind' in x for x in validate_analysis.validate(bad, self.schema)))

    def test_reject_bounded_universal_without_closed_world(self):
        bad = copy.deepcopy(self.sample)
        bad['claims'][0]['universality'] = 'bounded'
        self.assertTrue(any('closed-world' in x for x in validate_analysis.validate(bad, self.schema)))

    def test_reject_unknown_without_next_check(self):
        bad = copy.deepcopy(self.sample)
        bad['claims'][2]['countercheck'] = ''
        self.assertTrue(any('next verification check' in x for x in validate_analysis.validate(bad, self.schema)))

    def test_reject_unlinked_transition_claim(self):
        bad = copy.deepcopy(self.sample)
        bad['transitions'][0]['claim_ids'] = ['CL-999']
        self.assertTrue(any('unknown claim ID' in x for x in validate_analysis.validate(bad, self.schema)))

    def test_duplicate_json_keys_blocked(self):
        with self.assertRaises(validate_analysis.DuplicateKeyError):
            json.loads('{"question":"A","question":"B"}', object_pairs_hook=validate_analysis.no_duplicate_keys)

    def test_reject_unexpected_field(self):
        bad = copy.deepcopy(self.sample)
        bad['unchecked_extra'] = 'silent drift'
        self.assertTrue(any('unexpected field' in x for x in validate_analysis.validate(bad, self.schema)))


class SkillPackageTests(unittest.TestCase):
    def test_package_valid(self):
        # A staged distribution excludes Python's runtime-generated caches.
        with tempfile.TemporaryDirectory() as temp:
            staged = Path(temp) / ROOT.name
            shutil.copytree(ROOT, staged, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache', '.DS_Store'))
            self.assertEqual([], validate_skill.validate(staged))

    def test_trace_bidirectional_link_failure(self):
        trace = json.loads((ROOT / 'research/traceability.json').read_text())
        trace['sources'][0]['finding_ids'] = []
        self.assertTrue(any('reverse source link' in x for x in validate_skill.validate_trace(ROOT, trace)))

    def test_invalid_version_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp) / ROOT.name
            shutil.copytree(ROOT, temp_root, ignore=shutil.ignore_patterns('__pycache__'))
            (temp_root / 'VERSION').write_text('not-semver\n')
            self.assertTrue(any('VERSION' in x for x in validate_skill.validate(temp_root)))

    def test_missing_reference_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp) / ROOT.name
            shutil.copytree(ROOT, temp_root, ignore=shutil.ignore_patterns('__pycache__'))
            (temp_root / 'references/investigation-playbook.md').unlink()
            self.assertTrue(any('missing reference' in x for x in validate_skill.validate(temp_root)))


if __name__ == '__main__':
    unittest.main()
