"""Real executed regression coverage for the metric-only helper."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "compare_metrics.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
import compare_metrics as mod


def example() -> dict:
    return json.loads((SKILL_ROOT / "assets" / "metrics-input.example.json").read_text(encoding="utf-8"))


class EvaluateTests(unittest.TestCase):
    def report(self, data: dict) -> dict:
        return mod.evaluate(data, "0" * 64)

    def test_example_passes_numerically_but_only_with_limited_scope(self):
        r = self.report(example())
        self.assertEqual(r["gate"], "pass")
        self.assertTrue(all(m["metric_status"] == "met" for m in r["metric_results"]))
        self.assertIn("does not prove tests", r["scope_of_proof"])

    def test_target_that_cannot_be_met_fails(self):
        data = example()
        data["metrics"][0]["min_improvement_pct"] = 30
        result = self.report(data)
        self.assertEqual(result["gate"], "fail")
        self.assertEqual(result["metric_results"][0]["metric_status"], "unmet")

    def test_guardrail_regression_blocks_pass(self):
        data = example()
        data["metrics"][1]["candidate_samples"] = [190] * 5
        r = self.report(data)
        self.assertEqual(r["gate"], "fail")
        self.assertEqual(r["metric_results"][1]["metric_status"], "regression")

    def test_small_gain_does_not_count_as_verified_improvement(self):
        data = example()
        data["metrics"][0]["candidate_samples"] = [270] * 5
        data["metrics"][0]["min_improvement_pct"] = 10
        data["metrics"][0]["noise_floor_pct"] = 1
        result = self.report(data)
        self.assertEqual(result["gate"], "inconclusive")
        self.assertEqual(result["metric_results"][0]["metric_status"], "inconclusive")

    def test_higher_is_better_target(self):
        data = example()
        metric = data["metrics"][0]
        metric["direction"] = "higher"
        metric["baseline_samples"] = [100] * 5
        metric["candidate_samples"] = [125] * 5
        self.assertEqual(self.report(data)["metric_results"][0]["metric_status"], "met")

    def test_environment_mismatch_rejected(self):
        data = example()
        data["candidate"]["environment_id"] = "different-machine"
        with self.assertRaisesRegex(mod.InvalidEvidence, "mismatch: environment_id"):
            self.report(data)

    def test_workload_and_harness_mismatch_rejected(self):
        for key in ("workload_id", "harness_id"):
            with self.subTest(key=key):
                data = example()
                data["candidate"][key] = "changed"
                with self.assertRaises(mod.InvalidEvidence):
                    self.report(data)

    def test_identical_candidate_and_baseline_rejected(self):
        data = example()
        data["candidate"]["id"] = data["baseline"]["id"]
        with self.assertRaises(mod.InvalidEvidence):
            self.report(data)

    def test_missing_target_metric_rejected(self):
        data = example()
        data["metrics"].pop(0)
        with self.assertRaises(mod.InvalidEvidence):
            self.report(data)

    def test_metric_duplicate_rejected(self):
        data = example()
        data["metrics"].append(copy.deepcopy(data["metrics"][0]))
        with self.assertRaises(mod.InvalidEvidence):
            self.report(data)

    def test_nonfinite_and_bool_samples_rejected(self):
        for invalid in (float("nan"), float("inf"), True, -1, 0, "1"):
            with self.subTest(value=str(invalid)):
                data = example()
                data["metrics"][0]["candidate_samples"][0] = invalid
                with self.assertRaises(mod.InvalidEvidence):
                    self.report(data)

    def test_insufficient_samples_rejected(self):
        data = example()
        data["metrics"][0]["candidate_samples"] = [230, 240]
        with self.assertRaises(mod.InvalidEvidence):
            self.report(data)

    def test_unexpected_keys_rejected(self):
        data = example()
        data["metrics"][0]["change_acceptance"] = True
        with self.assertRaises(mod.InvalidEvidence):
            self.report(data)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text('{"x": 1, "x": 2}', encoding="utf-8")
            with self.assertRaisesRegex(mod.InvalidEvidence, "duplicate JSON key"):
                mod.read_input(source)

    def test_invalid_json_nans_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text('{"metric": NaN}', encoding="utf-8")
            with self.assertRaises(mod.InvalidEvidence):
                mod.read_input(source)

    def test_equal_output_path_does_not_corrupt_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            original = json.dumps(example())
            source.write_text(original, encoding="utf-8")
            with self.assertRaisesRegex(mod.InvalidEvidence, "may not overwrite input"):
                mod.write_atomic(source, source, self.report(example()))
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_symlink_output_rejected_and_destination_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(example()), encoding="utf-8")
            destination = Path(tmp) / "existing.json"
            destination.write_text("do not overwrite", encoding="utf-8")
            symlink = Path(tmp) / "report.json"
            try:
                symlink.symlink_to(destination)
            except (OSError, NotImplementedError):
                self.skipTest("symlink unsupported by platform")
            with self.assertRaisesRegex(mod.InvalidEvidence, "may not be a symlink"):
                mod.write_atomic(symlink, source, self.report(example()))
            self.assertEqual(destination.read_text(encoding="utf-8"), "do not overwrite")

    def test_cli_writes_report_and_exits_zero_on_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(example()), encoding="utf-8")
            report_path = Path(tmp) / "report.json"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--out", str(report_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["gate"], "pass")
            self.assertEqual(report["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_cli_writes_report_and_exits_two_on_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = example()
            data["metrics"][0]["min_improvement_pct"] = 40
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            report_path = Path(tmp) / "report.json"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--out", str(report_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["gate"], "fail")

    def test_existing_report_is_not_overwritten_even_by_valid_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(example()), encoding="utf-8")
            report = Path(tmp) / "existing.json"
            report.write_text("previous validated result", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--out", str(report)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 3)
            self.assertEqual(report.read_text(encoding="utf-8"), "previous validated result")

    def test_cli_invalid_does_not_replace_existing_good_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "invalid.json"
            source.write_text("{}", encoding="utf-8")
            existing = Path(tmp) / "report.json"
            existing.write_text("last-good-report", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--out", str(existing)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 3)
            self.assertEqual(existing.read_text(encoding="utf-8"), "last-good-report")


if __name__ == "__main__":
    unittest.main()
