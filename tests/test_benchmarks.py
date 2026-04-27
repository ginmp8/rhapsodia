"""Tests for benchmark runner and pre-built tasks."""

import pytest

from benchmarks.runner import BenchmarkResult, BenchmarkRunner, BenchmarkSuite
from benchmarks.tasks.qa import QA_TASKS
from evals.harness import EvalCase
from evals.metrics import accuracy
from skills.echo import EchoSkill
from skills.search import SearchSkill


# ---------------------------------------------------------------------------
# BenchmarkSuite / BenchmarkRunner
# ---------------------------------------------------------------------------


class TestBenchmarkRunner:
    def _make_suite(self, name="test-suite"):
        cases = [
            EvalCase(input="a", expected="a"),
            EvalCase(input="b", expected="b"),
        ]
        return BenchmarkSuite(name=name, cases=cases, metric=accuracy)

    def test_single_suite_perfect_score(self):
        suite = self._make_suite()
        runner = BenchmarkRunner(suites=[suite])
        results = runner.run(EchoSkill())
        assert len(results) == 1
        assert results[0].report.score == pytest.approx(1.0)

    def test_returns_benchmark_result_instances(self):
        suite = self._make_suite()
        runner = BenchmarkRunner(suites=[suite])
        results = runner.run(EchoSkill())
        for r in results:
            assert isinstance(r, BenchmarkResult)

    def test_suite_name_preserved(self):
        suite = self._make_suite(name="my-bench")
        runner = BenchmarkRunner(suites=[suite])
        results = runner.run(EchoSkill())
        assert results[0].suite_name == "my-bench"

    def test_multiple_suites(self):
        suites = [self._make_suite(f"suite-{i}") for i in range(3)]
        runner = BenchmarkRunner(suites=suites)
        results = runner.run(EchoSkill())
        assert len(results) == 3

    def test_run_all_multiple_skills(self):
        suite = self._make_suite()
        runner = BenchmarkRunner(suites=[suite])
        skills = [EchoSkill(), SearchSkill(max_results=1)]
        all_results = runner.run_all(skills)
        assert set(all_results.keys()) == {"echo", "search"}

    def test_benchmark_result_str(self):
        suite = self._make_suite()
        runner = BenchmarkRunner(suites=[suite])
        result = runner.run(EchoSkill())[0]
        s = str(result)
        assert "BenchmarkResult" in s
        assert "echo" in s


# ---------------------------------------------------------------------------
# Pre-built QA tasks
# ---------------------------------------------------------------------------


class TestQATasks:
    def test_qa_tasks_is_list(self):
        assert isinstance(QA_TASKS, list)

    def test_qa_tasks_nonempty(self):
        assert len(QA_TASKS) > 0

    def test_qa_task_eval_cases_have_ids(self):
        for task in QA_TASKS:
            assert task.id, f"Task missing id: {task}"

    def test_qa_task_eval_cases_have_inputs(self):
        for task in QA_TASKS:
            assert task.input

    def test_qa_task_eval_cases_have_expected(self):
        for task in QA_TASKS:
            assert task.expected
