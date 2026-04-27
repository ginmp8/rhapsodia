"""Tests for the skill pipeline delivery workflow."""

import pytest

from skills.echo import EchoSkill
from skills.summarize import SummarizeSkill
from workflows.pipeline import SkillPipeline


class TestSkillPipeline:
    def test_single_skill_passthrough(self):
        pipeline = SkillPipeline(skills=[EchoSkill()])
        result = pipeline.run("hello")
        assert result.output == "hello"

    def test_two_skills_chained(self):
        # Both EchoSkills are string-compatible; verify the chain completes.
        pipeline = SkillPipeline(skills=[EchoSkill(), SummarizeSkill(max_sentences=1)])
        result = pipeline.run("One sentence. Two sentence.")
        assert result.output is not None

    def test_metadata_contains_pipeline_steps(self):
        pipeline = SkillPipeline(skills=[EchoSkill(), EchoSkill()])
        result = pipeline.run("test")
        assert "pipeline" in result.metadata
        assert "steps" in result.metadata
        assert len(result.metadata["steps"]) == 2

    def test_metadata_pipeline_skill_names(self):
        pipeline = SkillPipeline(skills=[EchoSkill()])
        result = pipeline.run("x")
        assert result.metadata["pipeline"] == ["echo"]

    def test_empty_skills_raises_value_error(self):
        with pytest.raises(ValueError, match="at least one skill"):
            SkillPipeline(skills=[])

    def test_output_threads_through(self):
        """Each skill receives the previous skill's output."""
        calls = []

        class RecordingEcho(EchoSkill):
            def run(self, input, **kwargs):
                calls.append(input)
                return super().run(input, **kwargs)

        pipeline = SkillPipeline(skills=[RecordingEcho(), RecordingEcho()])
        pipeline.run("seed")
        assert calls[0] == "seed"
        assert calls[1] == "seed"  # echo returns input unchanged

    def test_repr(self):
        pipeline = SkillPipeline(skills=[EchoSkill(), EchoSkill()])
        r = repr(pipeline)
        assert "SkillPipeline" in r
        assert "echo" in r
