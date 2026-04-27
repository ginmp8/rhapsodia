"""Echo skill – mirrors its input back as output.

Useful as a smoke-test and as a trivial baseline for evaluation harnesses.
"""

from __future__ import annotations

from typing import Any

from skills.base import Skill, SkillResult


class EchoSkill(Skill):
    """Returns its input unchanged.

    Example::

        skill = EchoSkill()
        result = skill.run("hello")
        assert result.output == "hello"
    """

    name = "echo"
    description = "Returns the input unchanged."
    version = "1.0.0"

    def run(self, input: Any, **kwargs: Any) -> SkillResult:
        return SkillResult(output=input, metadata={"skill": self.name})
