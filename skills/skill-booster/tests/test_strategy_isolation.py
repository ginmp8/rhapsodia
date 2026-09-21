from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_canonical_foundation_is_strategy_neutral():
    foundation = read("references/optimization-foundation.md").lower()
    assert "strategy gate" in foundation
    assert "evolutionary readiness is not a quality gate" in foundation
    for term in ("population management", "crossover", "recombination", "pareto", "novelty", "offspring"):
        assert term not in foundation


def test_canonical_workflow_uses_transform_not_mutate_phase():
    workflow = read("references/optimization-workflow.md")
    assert "## Phase 4: Transform" in workflow
    assert "## Phase 4: Mutate" not in workflow
    assert "Evolutionary readiness is not a completion criterion" in workflow


def test_skill_declares_evolution_isolation_invariants():
    skill = read("SKILL.md")
    assert "must remain fully functional without Skill Evolution" in skill
    assert "Evolutionary readiness is never a completion requirement" in skill
    assert "Maintain an experiment registry only when real experiments or multi-candidate comparisons are executed" in skill


def test_legacy_paths_are_compatibility_only_and_not_canonical():
    skill = read("SKILL.md")
    assert "references/pre-evolution-foundation.md" not in skill
    assert "references/mutation-and-safety-policy.md" not in skill
    assert "scripts/validate_pre_evolution_state.py" not in skill
    assert "compatibility alias" in read("references/pre-evolution-foundation.md").lower()
    assert "compatibility alias" in read("references/mutation-and-safety-policy.md").lower()
    assert "compatibility shim" in read("scripts/validate_pre_evolution_state.py").lower()
