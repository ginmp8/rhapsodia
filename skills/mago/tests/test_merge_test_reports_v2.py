from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from merge_test_reports import merge  # noqa: E402
from run_test_suite import suite_manifest  # noqa: E402


class MergeTestReportsV2Tests(unittest.TestCase):
    def test_merge_rejects_incomplete_coverage(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-merge-") as tmp:
            report = Path(tmp) / "shard.json"
            files = sorted((ROOT / "tests").glob("test_*.py"))
            manifest, digest = suite_manifest(files)
            report.write_text(json.dumps({
                "status": "pass", "suite_digest": digest,
                "results": [{"file": f"tests/{files[0].name}", "status": "pass", "test_count": 1}],
            }), encoding="utf-8")
            result = merge(ROOT, [report], minimum_tests=1)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("missing test files" in error for error in result["errors"]), result)


if __name__ == "__main__":
    unittest.main()
