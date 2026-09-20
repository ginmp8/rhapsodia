from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from consistency_audit import audit  # noqa: E402
from freeze_evaluators import freeze, verify  # noqa: E402
from inventory_skill import scan_target  # noqa: E402
from package_target_skill import ZIP_TIMESTAMP, files_to_zip, sha256_file, validate_archive, write_normalized_archive  # noqa: E402
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

    def test_package_bytes_ignore_source_mtime_and_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / 'first' / 'sample-skill'
            second = root / 'second' / 'sample-skill'
            first.mkdir(parents=True)
            (first / 'scripts').mkdir()
            (first / 'SKILL.md').write_text('---\nname: sample-skill\ndescription: package determinism fixture\n---\n', encoding='utf-8')
            (first / 'scripts' / 'tool.py').write_text('print("ok")\n', encoding='utf-8')
            shutil.copytree(first, second)

            os.utime(first / 'SKILL.md', (946684800, 946684800))
            os.utime(second / 'SKILL.md', (1789948800, 1789948800))
            (first / 'scripts' / 'tool.py').chmod(0o600)
            (second / 'scripts' / 'tool.py').chmod(0o755)

            first_zip = root / 'first.zip'
            second_zip = root / 'second.zip'
            write_normalized_archive(first_zip, first, 'sample-skill', files_to_zip(first))
            write_normalized_archive(second_zip, second, 'sample-skill', files_to_zip(second))

            self.assertEqual(sha256_file(first_zip), sha256_file(second_zip))
            self.assertEqual([], validate_archive(first_zip, 'sample-skill', require_normalized=True))
            self.assertEqual([], validate_archive(second_zip, 'sample-skill', require_normalized=True))
            with zipfile.ZipFile(first_zip) as zf:
                self.assertTrue(all(info.date_time == ZIP_TIMESTAMP for info in zf.infolist()))


if __name__ == '__main__':
    unittest.main()
