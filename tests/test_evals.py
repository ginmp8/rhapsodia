"""Tests for evaluation harnesses and metrics."""

import pytest

from evals.harness import EvalCase, EvalHarness, EvalReport
from evals.metrics import accuracy, f1_score, rouge_l
from skills.echo import EchoSkill
from skills.summarize import SummarizeSkill


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class TestAccuracy:
    def test_exact_match_strings(self):
        assert accuracy("hello", "hello") == 1.0

    def test_mismatch_strings(self):
        assert accuracy("hello", "world") == 0.0

    def test_exact_match_numbers(self):
        assert accuracy(42, 42) == 1.0

    def test_mismatch_numbers(self):
        assert accuracy(1, 2) == 0.0

    def test_exact_match_lists(self):
        assert accuracy([1, 2], [1, 2]) == 1.0


class TestF1Score:
    def test_identical_strings(self):
        assert f1_score("the cat sat", "the cat sat") == pytest.approx(1.0)

    def test_completely_different(self):
        assert f1_score("foo bar", "baz qux") == pytest.approx(0.0)

    def test_partial_overlap(self):
        score = f1_score("the cat sat on the mat", "the dog sat on the floor")
        assert 0.0 < score < 1.0

    def test_empty_expected(self):
        assert f1_score("", "") == pytest.approx(1.0)

    def test_empty_actual_nonempty_expected(self):
        assert f1_score("", "something") == pytest.approx(0.0)


class TestRougeL:
    def test_identical_strings(self):
        assert rouge_l("the quick brown fox", "the quick brown fox") == pytest.approx(1.0)

    def test_completely_different(self):
        assert rouge_l("abc def", "xyz uvw") == pytest.approx(0.0)

    def test_partial_match(self):
        score = rouge_l("the quick brown fox", "the slow brown dog")
        assert 0.0 < score < 1.0

    def test_empty_strings(self):
        assert rouge_l("", "") == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# EvalHarness
# ---------------------------------------------------------------------------


class TestEvalHarness:
    def _echo_cases(self):
        return [
            EvalCase(id="c1", input="hello", expected="hello"),
            EvalCase(id="c2", input="world", expected="world"),
        ]

    def test_perfect_score_echo(self):
        harness = EvalHarness(
            skill=EchoSkill(),
            cases=self._echo_cases(),
            metric=accuracy,
        )
        report = harness.run()
        assert report.score == pytest.approx(1.0)

    def test_zero_score_mismatch(self):
        cases = [EvalCase(input="hello", expected="WRONG")]
        harness = EvalHarness(skill=EchoSkill(), cases=cases, metric=accuracy)
        report = harness.run()
        assert report.score == pytest.approx(0.0)

    def test_report_num_cases(self):
        harness = EvalHarness(
            skill=EchoSkill(),
            cases=self._echo_cases(),
            metric=accuracy,
        )
        report = harness.run()
        assert report.num_cases == 2

    def test_report_details_length(self):
        harness = EvalHarness(
            skill=EchoSkill(),
            cases=self._echo_cases(),
            metric=accuracy,
        )
        report = harness.run()
        assert len(report.details) == 2

    def test_report_details_keys(self):
        harness = EvalHarness(
            skill=EchoSkill(),
            cases=self._echo_cases(),
            metric=accuracy,
        )
        report = harness.run()
        for detail in report.details:
            assert "input" in detail
            assert "expected" in detail
            assert "actual" in detail
            assert "score" in detail

    def test_empty_cases(self):
        harness = EvalHarness(skill=EchoSkill(), cases=[], metric=accuracy)
        report = harness.run()
        assert report.score == pytest.approx(0.0)
        assert report.num_cases == 0

    def test_report_str(self):
        harness = EvalHarness(
            skill=EchoSkill(), cases=self._echo_cases(), metric=accuracy
        )
        report = harness.run()
        assert "EvalReport" in str(report)
        assert "echo" in str(report)

    def test_returns_eval_report_instance(self):
        harness = EvalHarness(
            skill=EchoSkill(), cases=self._echo_cases(), metric=accuracy
        )
        assert isinstance(harness.run(), EvalReport)
