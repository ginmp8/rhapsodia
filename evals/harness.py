"""Evaluation harness for agent skills.

Usage::

    from skills.echo import EchoSkill
    from evals.harness import EvalCase, EvalHarness
    from evals.metrics import accuracy

    cases = [
        EvalCase(input="hello", expected="hello"),
        EvalCase(input="world", expected="world"),
    ]

    harness = EvalHarness(skill=EchoSkill(), cases=cases, metric=accuracy)
    report = harness.run()
    print(report)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from skills.base import Skill


@dataclass
class EvalCase:
    """A single evaluation example.

    Attributes:
        input: The input passed to :meth:`Skill.run`.
        expected: The expected output used to compute the metric.
        id: Optional identifier for the case (useful for debugging).
    """

    input: Any
    expected: Any
    id: str = ""


@dataclass
class EvalReport:
    """Aggregated result of an evaluation run.

    Attributes:
        skill_name: Name of the evaluated skill.
        score: Aggregate metric score in the range ``[0, 1]``.
        num_cases: Total number of evaluation cases.
        details: Per-case breakdown (input, expected, actual, score).
    """

    skill_name: str
    score: float
    num_cases: int
    details: list[dict[str, Any]] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"EvalReport(skill={self.skill_name!r}, score={self.score:.4f}, "
            f"cases={self.num_cases})"
        )


class EvalHarness:
    """Runs a :class:`~skills.base.Skill` against a set of :class:`EvalCase`s.

    Args:
        skill: The skill under evaluation.
        cases: List of evaluation cases.
        metric: A callable ``metric(actual, expected) -> float`` in ``[0, 1]``.
    """

    def __init__(
        self,
        skill: Skill,
        cases: list[EvalCase],
        metric: Callable[[Any, Any], float],
    ) -> None:
        self.skill = skill
        self.cases = cases
        self.metric = metric

    def run(self) -> EvalReport:
        """Execute all cases and return an aggregated :class:`EvalReport`.

        Returns:
            An :class:`EvalReport` with per-case details and the mean score.
        """
        details: list[dict[str, Any]] = []
        total_score = 0.0

        for case in self.cases:
            result = self.skill.run(case.input)
            case_score = self.metric(result.output, case.expected)
            total_score += case_score
            details.append(
                {
                    "id": case.id,
                    "input": case.input,
                    "expected": case.expected,
                    "actual": result.output,
                    "score": case_score,
                }
            )

        aggregate = total_score / len(self.cases) if self.cases else 0.0
        return EvalReport(
            skill_name=self.skill.name,
            score=aggregate,
            num_cases=len(self.cases),
            details=details,
        )
