"""Summarization skill.

Condenses a piece of text to the first *max_sentences* sentences.  In
production this would call an LLM; the default implementation uses a simple
sentence-splitting heuristic so it works offline.

To use a real summarizer, subclass :class:`SummarizeSkill` and override
:meth:`_summarize`.
"""

from __future__ import annotations

import re
from typing import Any

from skills.base import Skill, SkillResult

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


class SummarizeSkill(Skill):
    """Summarizes a block of text.

    Args:
        max_sentences: Maximum number of sentences to keep.

    Example::

        skill = SummarizeSkill(max_sentences=2)
        result = skill.run("Long article text goes here. ...")
        print(result.output)
    """

    name = "summarize"
    description = "Summarizes a text document to a configurable number of sentences."
    version = "1.0.0"

    def __init__(self, max_sentences: int = 3) -> None:
        self.max_sentences = max_sentences

    def run(self, input: str, **kwargs: Any) -> SkillResult:
        """Summarize *input*.

        Args:
            input: Text to summarize.

        Returns:
            A :class:`SkillResult` whose ``output`` is the summarized string.
        """
        summary = self._summarize(input, self.max_sentences)
        return SkillResult(
            output=summary,
            metadata={
                "skill": self.name,
                "input_chars": len(input),
                "output_chars": len(summary),
            },
        )

    def _summarize(self, text: str, max_sentences: int) -> str:
        """Return a summary of *text*.

        The default implementation keeps the first *max_sentences* sentences.
        Override this method in a subclass to call an LLM or extraction model.
        """
        sentences = _SENTENCE_SPLIT_RE.split(text.strip())
        return " ".join(sentences[:max_sentences])
