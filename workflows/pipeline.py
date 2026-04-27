"""Skill pipeline – chains multiple skills so the output of one becomes the
input of the next.

Usage::

    from skills.search import SearchSkill
    from skills.summarize import SummarizeSkill
    from workflows.pipeline import SkillPipeline

    pipeline = SkillPipeline(skills=[SearchSkill(), SummarizeSkill()])
    result = pipeline.run("latest advances in quantum computing")
    print(result.output)
"""

from __future__ import annotations

from typing import Any

from skills.base import Skill, SkillResult


class SkillPipeline:
    """Executes a sequence of skills, threading output into the next input.

    The pipeline treats the ``output`` of each :class:`~skills.base.SkillResult`
    as the ``input`` to the subsequent skill.  Metadata from every step is
    collected and available on the final result.

    Args:
        skills: Ordered list of skills to execute.

    Raises:
        ValueError: If *skills* is empty.

    Example::

        pipeline = SkillPipeline(skills=[SearchSkill(), SummarizeSkill()])
        result = pipeline.run("climate change solutions")
    """

    def __init__(self, skills: list[Skill]) -> None:
        if not skills:
            raise ValueError("SkillPipeline requires at least one skill.")
        self.skills = skills

    def run(self, input: Any, **kwargs: Any) -> SkillResult:
        """Run *input* through every skill in order.

        Args:
            input: The initial input to the first skill.
            **kwargs: Forwarded to every skill's :meth:`~skills.base.Skill.run`.

        Returns:
            The :class:`~skills.base.SkillResult` produced by the last skill,
            augmented with a ``steps`` key in ``metadata`` that lists each
            intermediate result.
        """
        current_input: Any = input
        steps: list[dict[str, Any]] = []

        for skill in self.skills:
            result = skill.run(current_input, **kwargs)
            steps.append(
                {
                    "skill": skill.name,
                    "input": current_input,
                    "output": result.output,
                    "metadata": result.metadata,
                }
            )
            current_input = result.output

        final_result = steps[-1]
        return SkillResult(
            output=final_result["output"],
            metadata={"pipeline": [s["skill"] for s in steps], "steps": steps},
        )

    def __repr__(self) -> str:
        names = " -> ".join(s.name for s in self.skills)
        return f"SkillPipeline([{names}])"
