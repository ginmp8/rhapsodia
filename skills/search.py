"""Web-search skill.

In production this skill would call a real search API (e.g. Brave, Bing,
SerpAPI).  The default implementation is a *mock* that returns synthetic
results so the skill can be exercised in tests and benchmarks without
network access.

To plug in a real backend, subclass :class:`SearchSkill` and override
:meth:`_fetch`.
"""

from __future__ import annotations

from typing import Any

from skills.base import Skill, SkillResult


class SearchSkill(Skill):
    """Performs a web search and returns a list of result snippets.

    Args:
        max_results: Maximum number of results to return.

    Example::

        skill = SearchSkill(max_results=3)
        result = skill.run("python async generators")
        for snippet in result.output:
            print(snippet["title"], snippet["url"])
    """

    name = "search"
    description = "Searches the web and returns ranked result snippets."
    version = "1.0.0"

    def __init__(self, max_results: int = 5) -> None:
        self.max_results = max_results

    def run(self, input: str, **kwargs: Any) -> SkillResult:
        """Run a web search for *input* and return up to ``max_results`` hits.

        Args:
            input: The search query string.

        Returns:
            A :class:`SkillResult` whose ``output`` is a list of dicts with
            keys ``title``, ``url``, and ``snippet``.
        """
        results = self._fetch(query=input, max_results=self.max_results)
        return SkillResult(
            output=results,
            metadata={"skill": self.name, "query": input, "num_results": len(results)},
        )

    def _fetch(self, query: str, max_results: int) -> list[dict[str, str]]:
        """Return search results for *query*.

        The default implementation returns synthetic mock data.
        Override this method in a subclass to call a real search API.
        """
        return [
            {
                "title": f"Result {i + 1} for '{query}'",
                "url": f"https://example.com/result/{i + 1}",
                "snippet": f"Snippet {i + 1}: information about {query}.",
            }
            for i in range(max_results)
        ]
