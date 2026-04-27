"""Tests for agent skills."""

import pytest

from skills.base import Skill, SkillResult
from skills.echo import EchoSkill
from skills.search import SearchSkill
from skills.summarize import SummarizeSkill


# ---------------------------------------------------------------------------
# EchoSkill
# ---------------------------------------------------------------------------


class TestEchoSkill:
    def test_returns_string_unchanged(self):
        skill = EchoSkill()
        result = skill.run("hello world")
        assert result.output == "hello world"

    def test_returns_non_string_unchanged(self):
        skill = EchoSkill()
        payload = {"key": "value", "num": 42}
        result = skill.run(payload)
        assert result.output == payload

    def test_result_has_skill_metadata(self):
        skill = EchoSkill()
        result = skill.run("test")
        assert result.metadata["skill"] == "echo"

    def test_skill_attributes(self):
        skill = EchoSkill()
        assert skill.name == "echo"
        assert skill.version == "1.0.0"
        assert isinstance(skill.description, str)

    def test_returns_skill_result_instance(self):
        skill = EchoSkill()
        result = skill.run("x")
        assert isinstance(result, SkillResult)


# ---------------------------------------------------------------------------
# SearchSkill
# ---------------------------------------------------------------------------


class TestSearchSkill:
    def test_default_max_results(self):
        skill = SearchSkill()
        result = skill.run("python testing")
        assert len(result.output) == 5

    def test_custom_max_results(self):
        skill = SearchSkill(max_results=3)
        result = skill.run("pytest fixtures")
        assert len(result.output) == 3

    def test_result_items_have_required_keys(self):
        skill = SearchSkill(max_results=2)
        result = skill.run("asyncio")
        for item in result.output:
            assert "title" in item
            assert "url" in item
            assert "snippet" in item

    def test_metadata_contains_query(self):
        skill = SearchSkill(max_results=1)
        query = "type hints python"
        result = skill.run(query)
        assert result.metadata["query"] == query

    def test_metadata_num_results(self):
        skill = SearchSkill(max_results=4)
        result = skill.run("generators")
        assert result.metadata["num_results"] == 4


# ---------------------------------------------------------------------------
# SummarizeSkill
# ---------------------------------------------------------------------------


class TestSummarizeSkill:
    _SAMPLE = (
        "The quick brown fox jumps over the lazy dog. "
        "It was a bright and sunny morning. "
        "The fox had been running for hours. "
        "Finally, it reached the meadow."
    )

    def test_respects_max_sentences(self):
        skill = SummarizeSkill(max_sentences=2)
        result = skill.run(self._SAMPLE)
        sentences = [s for s in result.output.split(". ") if s]
        assert len(sentences) <= 2

    def test_full_text_within_sentence_limit(self):
        skill = SummarizeSkill(max_sentences=100)
        result = skill.run(self._SAMPLE)
        # All content should be preserved when limit > actual sentences
        assert "quick brown fox" in result.output

    def test_metadata_tracks_char_counts(self):
        skill = SummarizeSkill(max_sentences=2)
        result = skill.run(self._SAMPLE)
        assert result.metadata["input_chars"] == len(self._SAMPLE)
        assert result.metadata["output_chars"] == len(result.output)

    def test_empty_string(self):
        skill = SummarizeSkill(max_sentences=3)
        result = skill.run("")
        assert result.output == ""

    def test_single_sentence(self):
        skill = SummarizeSkill(max_sentences=3)
        text = "Just one sentence."
        result = skill.run(text)
        assert result.output == text


# ---------------------------------------------------------------------------
# Skill base
# ---------------------------------------------------------------------------


class TestSkillBase:
    def test_abstract_base_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Skill()  # type: ignore[abstract]

    def test_repr(self):
        skill = EchoSkill()
        r = repr(skill)
        assert "EchoSkill" in r
        assert "echo" in r
