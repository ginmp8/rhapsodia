"""Regression tests: an audit must produce an installable evidence bundle without fabricated numbers."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_bundle import build_bundle
from audit_core import AuditError, digest, extract_requirements, init_checks, normalize_source


class AlwaysArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.source = {
            "repository": "example/audit", "pull_request": {
                "number": 55, "head_sha": "a" * 40, "base_sha": "b" * 40,
                "files": ["src/service.py"]},
            "issue": {"number": 88, "body": "## Acceptance criteria\n- **AC-01** Verify a real result.\n- **AC-02** Reject an invalid result.",
                      "comments": []},
        }

    def test_without_checkout_still_writes_all_files_and_zip(self):
        report = build_bundle(source_input=self.source, output=self.dir / 'audit')
        self.assertEqual(report['overall']['assessment_state'], 'NOT_ASSESSED')
        self.assertIsNone(report['overall']['completion_verified_pct'])
        self.assertEqual(report['overall']['acceptance_criteria']['eligible_count'], 2)
        zip_path = self.dir / 'audit' / 'audit-bundle.zip'
        self.assertTrue(zip_path.is_file())
        with zipfile.ZipFile(zip_path) as z:
            self.assertIn('report.md', z.namelist())
            self.assertIn('source.json', z.namelist())
            self.assertEqual(json.loads(z.read('source.json'))['capture']['issue_completeness'], 'not_verified')
            self.assertIn('NOT ASSESSED', z.read('report.md').decode())
        manifest = json.loads((self.dir / 'audit' / 'manifest.json').read_text())
        for path, expected in manifest['files_sha256'].items():
            self.assertEqual(hashlib.sha256((self.dir / 'audit' / path).read_bytes()).hexdigest(), expected)

    def test_numeric_lower_bound_and_explicit_final_review_gate(self):
        build_bundle(source_input=self.source, output=self.dir / "numeric")
        result = json.loads((self.dir / "numeric" / "implementation-grade.json").read_text())
        self.assertEqual(result["summary"]["numeric_delivery_grade_pct"], "0.00")
        self.assertEqual(result["summary"]["assessed"], 0)
        with self.assertRaisesRegex(AuditError, "NO_SUBSTANTIVE_REVIEW"):
            build_bundle(source_input=self.source, output=self.dir / "no-empty-final",
                         require_review=True)
        self.assertFalse((self.dir / "no-empty-final" / "audit-bundle.zip").exists())

    def test_replay_is_byte_exact_in_separate_directories(self):
        build_bundle(source_input=self.source, output=self.dir / 'a')
        build_bundle(source_input=self.source, output=self.dir / 'b')
        self.assertEqual((self.dir / 'a' / 'audit-bundle.zip').read_bytes(),
                         (self.dir / 'b' / 'audit-bundle.zip').read_bytes())
        build_bundle(source_input=self.source, output=self.dir / 'a')

    def test_unavailable_checks_are_not_scored(self):
        normalized = normalize_source(self.source)
        req = extract_requirements(normalized)
        checks = init_checks(req)
        checks['requirements']['AC-01']['checks'] = [
            {'id':'static','kind':'contains','path':'src/service.py','text':'run'}]
        report = build_bundle(source_input=self.source, output=self.dir / 'partial',checks=checks)
        self.assertEqual(report['overall']['assessment_state'], 'NOT_ASSESSED')
        self.assertIsNone(report['overall']['completion_verified_pct'])
        self.assertEqual(report['criteria'][0]['checks'][0]['status'], 'NOT_RUN')

    def test_rejects_invalid_sha_without_creating_report(self):
        self.source['pull_request']['head_sha'] = 'short'
        with self.assertRaises(ValueError):
            build_bundle(source_input=self.source, output=self.dir / 'bad')
        self.assertFalse((self.dir / 'bad' / 'report.json').exists())

    def test_cli_offline_runs_without_gh(self):
        inp = self.dir / 'input.json'
        inp.write_text(json.dumps(self.source))
        out = self.dir / 'cli'
        result = subprocess.run([sys.executable, str(ROOT/'scripts'/'audit_bundle.py'),
                                 '--from-json', str(inp), '--out', str(out)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('NOT_ASSESSED', result.stdout)
        self.assertTrue((out/'audit-bundle.zip').exists())

if __name__ == '__main__':
    unittest.main()
