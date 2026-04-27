"""Abstract base class for all agent skills."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillResult:
    """Encapsulates the output of a skill invocation."""

    output: Any
    metadata: dict[str, Any] = field(default_factory=dict)


class Skill(abc.ABC):
    """Base class for all skills in the rhapsody-of-skills collection.

    Subclasses must implement :meth:`run` which accepts an arbitrary input
    and returns a :class:`SkillResult`.

    Attributes:
        name: Human-readable skill name.
        description: Short description of what the skill does.
        version: Semantic version string (e.g. ``"1.0.0"``).
    """

    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    @abc.abstractmethod
    def run(self, input: Any, **kwargs: Any) -> SkillResult:
        """Execute the skill.

        Args:
            input: Skill-specific input payload.
            **kwargs: Additional keyword arguments passed to the skill.

        Returns:
            A :class:`SkillResult` containing the output and optional metadata.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, version={self.version!r})"
