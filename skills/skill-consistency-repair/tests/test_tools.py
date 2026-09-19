from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from consistency_audit import audit  # noqa: E402
from freeze_evaluators import freeze, verify  # noqa: E402
from inventory_skill import scan_target  # noqa: E402
from validate_consistency_report import validate  # noqa: E402


class ConsistencyToolTests(unittest.TestCase):
    def test_inventory_fingerprint_is_stable_for_unchanged_tree(self) -> None:
        first = scan_target(ROOT)
        second = scan_target(ROOT)
        self.assertEqual(first['inventory_fingerprint'], second['inventory_fingerprint'])
        self.assertEqual(
            [(x['path'], x['sha256']) for x in first['files']],
            [(x['path'], x['sha256']) for x in second['files']],
        )

    def test_static_classifier_never_authorizes_deletion(self) -> None:
        report = audit(ROOT)
        self.assertTrue(report['resource_classification'])
        self.assertTrue(all(row['deletion_allowed'] is False for row in report['resource_classification']))

    def test_v2_report_validates(self) -> None:
        report = audit(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.json'
            path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            self.assertEqual([], validate(path))

    def test_evaluator_freeze_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'target'
            (root / 'evals').mkdir(parents=True)
            evaluator = root / 'evals' / 'cases.json'
            evaluator.write_text('{"cases": []}\n', encoding='utf-8')
            manifest = Path(tmp) / 'manifest.json'
            freeze(root, ['evals'], manifest)
            self.assertEqual('pass', verify(root, manifest)['status'])
            evaluator.write_text('{"cases": [1]}\n', encoding='utf-8')
            result = verify(root, manifest)
            self.assertEqual('fail', result['status'])
            self.assertEqual(['evals/cases.json'], result['changed'])


if __name__ == '__main__':
    unittest.main()
