"""Benchmark runner.

A *benchmark* is a named collection of :class:`~evals.harness.EvalCase`s
paired with a metric.  The :class:`BenchmarkRunner` evaluates one or more
skills across a :class:`BenchmarkSuite` and returns structured results.

Usage::

    from skills.echo import EchoSkill
    from evals.metrics import accuracy
    from benchmarks.runner import BenchmarkSuite, BenchmarkRunner
    from evals.harness import EvalCase

    suite = BenchmarkSuite(
        name="echo-bench",
        cases=[EvalCase(input="hi", expected="hi")],
        metric=accuracy,
    )
    runner = BenchmarkRunner(suites=[suite])
    results = runner.run(EchoSkill())
    for r in results:
        print(r)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from evals.harness import EvalCase, EvalHarness, EvalReport
from skills.base import Skill


@dataclass
class BenchmarkSuite:
    """A named collection of evaluation cases and a scoring metric.

    Attributes:
        name: Human-readable name for this suite.
        cases: List of :class:`~evals.harness.EvalCase` instances.
        metric: A callable ``metric(actual, expected) -> float``.
        description: Optional longer description of the suite.
    """

    name: str
    cases: list[EvalCase]
    metric: Callable[[Any, Any], float]
    description: str = ""


@dataclass
class BenchmarkResult:
    """Result of running a single :class:`BenchmarkSuite` against a skill.

    Attributes:
        suite_name: Name of the benchmark suite.
        report: The :class:`~evals.harness.EvalReport` for this run.
    """

    suite_name: str
    report: EvalReport

    def __str__(self) -> str:
        return (
            f"BenchmarkResult(suite={self.suite_name!r}, "
            f"skill={self.report.skill_name!r}, "
            f"score={self.report.score:.4f})"
        )


class BenchmarkRunner:
    """Evaluates skills across one or more :class:`BenchmarkSuite`s.

    Args:
        suites: The benchmark suites to run.
    """

    def __init__(self, suites: list[BenchmarkSuite]) -> None:
        self.suites = suites

    def run(self, skill: Skill) -> list[BenchmarkResult]:
        """Run *skill* against every suite and return results.

        Args:
            skill: The skill to benchmark.

        Returns:
            A list of :class:`BenchmarkResult`, one per suite.
        """
        results: list[BenchmarkResult] = []
        for suite in self.suites:
            harness = EvalHarness(skill=skill, cases=suite.cases, metric=suite.metric)
            report = harness.run()
            results.append(BenchmarkResult(suite_name=suite.name, report=report))
        return results

    def run_all(self, skills: list[Skill]) -> dict[str, list[BenchmarkResult]]:
        """Run multiple skills across every suite.

        Args:
            skills: Skills to benchmark.

        Returns:
            A dict mapping each skill name to its list of
            :class:`BenchmarkResult` objects.
        """
        return {skill.name: self.run(skill) for skill in skills}
