"""Pre-built question-answering benchmark tasks.

These tasks are used by the QA benchmark suite.  Each task is an
:class:`~evals.harness.EvalCase` where ``input`` is a question string and
``expected`` is the canonical answer string.
"""

from __future__ import annotations

from evals.harness import EvalCase

#: A small set of factual QA pairs for smoke-testing skills.
QA_TASKS: list[EvalCase] = [
    EvalCase(
        id="qa-001",
        input="What is the capital of France?",
        expected="Paris",
    ),
    EvalCase(
        id="qa-002",
        input="What is 2 + 2?",
        expected="4",
    ),
    EvalCase(
        id="qa-003",
        input="Who wrote Hamlet?",
        expected="William Shakespeare",
    ),
    EvalCase(
        id="qa-004",
        input="What is the boiling point of water in Celsius?",
        expected="100",
    ),
    EvalCase(
        id="qa-005",
        input="What programming language is known for its use in data science?",
        expected="Python",
    ),
]
