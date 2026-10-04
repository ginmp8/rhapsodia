from __future__ import annotations

import json
import os
import shutil
import subprocess
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
from inventory_skill import portable_path_collisions, scan_target  # noqa: E402
from package_target_skill import ZIP_TIMESTAMP, files_to_zip, sha256_file, validate_archive, write_normalized_archive  # noqa: E402
from impact_analysis import analyze as analyze_impact  # noqa: E402
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

    def test_v3_report_validates_and_v2_remains_compatible(self) -> None:
        report = audit(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.json'
            path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            self.assertEqual(3, report['report_version'])
            self.assertEqual([], validate(path))

            legacy = json.loads(json.dumps(report))
            legacy['report_version'] = 2
            for key in ('relation_contract', 'conformance', 'evidence_classes'):
                legacy.pop(key, None)
            legacy['classification_contract'].pop('trace_coverage_states', None)
            for finding in legacy['findings']:
                finding.pop('evidence_class', None)
            for row in legacy['resource_classification']:
                row.pop('trace_coverage', None)
            legacy_path = Path(tmp) / 'report-v2.json'
            legacy_path.write_text(json.dumps(legacy, indent=2) + '\n', encoding='utf-8')
            self.assertEqual([], validate(legacy_path))

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

    def test_trace_coverage_distinguishes_absence_from_uninspected(self) -> None:
        inv = scan_target(ROOT)
        coverage = inv['trace_coverage']['SKILL.md']
        self.assertEqual('inspected-none', coverage['imports']['state'])
        self.assertEqual('not-inspected', coverage['external_runtime']['state'])
        self.assertTrue(all(row['evidence_class'] == 'mechanically-proven' for row in inv['relation_graph']))

    def test_portable_path_collisions_detect_case_and_unicode(self) -> None:
        case = portable_path_collisions(['references/Foo.md', 'references/foo.md'])
        self.assertTrue(case)
        composed = 'references/caf\u00e9.md'
        decomposed = 'references/cafe\u0301.md'
        unicode_collision = portable_path_collisions([composed, decomposed])
        self.assertTrue(unicode_collision)

    def test_progressive_disclosure_reports_depth_from_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'sample-skill'
            (root / 'references').mkdir(parents=True)
            (root / 'SKILL.md').write_text('---\nname: sample-skill\ndescription: deterministic progressive disclosure fixture with explicit negative boundary; do not use outside tests.\n---\n' + '[one]' + '(references/one.md)\n', encoding='utf-8')
            (root / 'references' / 'one.md').write_text('[two]' + '(two.md)\n', encoding='utf-8')
            (root / 'references' / 'two.md').write_text('# Two\n', encoding='utf-8')
            inv = scan_target(root)
            self.assertEqual(2, inv['progressive_disclosure']['max_depth'])
            self.assertIn('references/two.md', inv['progressive_disclosure']['deep_references'])

    def test_impact_analysis_finds_direct_and_transitive_dependents(self) -> None:
        before = {
            'inventory_fingerprint': 'before',
            'files': [
                {'path': 'references/a.md', 'sha256': 'old'},
                {'path': 'scripts/b.py', 'sha256': 'b'},
                {'path': 'SKILL.md', 'sha256': 's'},
            ],
        }
        after = {
            'inventory_fingerprint': 'after',
            'files': [
                {'path': 'references/a.md', 'sha256': 'new'},
                {'path': 'scripts/b.py', 'sha256': 'b'},
                {'path': 'SKILL.md', 'sha256': 's'},
            ],
            'relation_graph': [
                {'source': 'scripts/b.py', 'target': 'references/a.md', 'relation': 'REFERENCES', 'detector': 'fixture'},
                {'source': 'SKILL.md', 'target': 'scripts/b.py', 'relation': 'REFERENCES', 'detector': 'fixture'},
            ],
        }
        result = analyze_impact(before, after)
        self.assertEqual(['scripts/b.py'], result['direct_dependents'])
        self.assertEqual(['SKILL.md', 'scripts/b.py'], result['transitive_dependents'])
        self.assertEqual('final-full-validation', result['suggested_gates'][-1])

    def test_consistency_receipt_binds_subject_verifier_and_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            baseline = scan_target(ROOT)
            baseline_path = tmp_path / 'baseline.json'
            baseline_path.write_text(json.dumps(baseline, indent=2) + '\n', encoding='utf-8')
            report = audit(ROOT)
            report_path = tmp_path / 'report.json'
            report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            manifest = tmp_path / 'evaluators.json'
            freeze(ROOT, ['evals'], manifest)
            receipt_path = tmp_path / 'receipt.json'
            proc = subprocess.run([
                sys.executable, str(SCRIPTS / 'create_consistency_receipt.py'),
                '--target', str(ROOT), '--baseline-inventory', str(baseline_path),
                '--final-report', str(report_path), '--evaluator-manifest', str(manifest),
                '--mode', 'validation-only', '--status', 'pass', '--out', str(receipt_path),
            ], capture_output=True, text=True, check=False)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            self.assertEqual(2, receipt['receipt_version'])
            self.assertEqual(baseline['inventory_fingerprint'], receipt['subject']['digest']['sha256'])
            self.assertEqual(64, len(receipt['verifier']['identity_sha256']))
            self.assertEqual(64, len(receipt['policies']['identity_sha256']))
            self.assertIn('not a cryptographic signature', receipt['claim_boundary'])

    def test_archive_validation_rejects_portable_path_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'sample-skill'
            root.mkdir(parents=True)
            (root / 'SKILL.md').write_text('---\nname: sample-skill\ndescription: portable path collision fixture with explicit boundary; do not use outside tests.\n---\n', encoding='utf-8')
            (root / 'Foo.md').write_text('A\n', encoding='utf-8')
            (root / 'foo.md').write_text('B\n', encoding='utf-8')
            archive = Path(tmp) / 'collision.zip'
            write_normalized_archive(archive, root, 'sample-skill', files_to_zip(root))
            errors = validate_archive(archive, 'sample-skill', require_normalized=True)
            self.assertTrue(any('portable path collisions' in error for error in errors))

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
