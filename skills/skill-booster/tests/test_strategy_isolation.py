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


def test_retired_legacy_paths_are_absent():
    skill = read("SKILL.md")
    retired = [
        "references/pre-evolution-foundation.md",
        "references/mutation-and-safety-policy.md",
        "scripts/validate_pre_evolution_state.py",
    ]
    for path in retired:
        assert path not in skill
        assert not (ROOT / path).exists()


def test_prove_requires_fresh_canonical_validation_receipt_before_final_gate():
    skill = read("SKILL.md")
    workflow = read("references/optimization-workflow.md")
    passbook = read("references/specialist-passbook.md")
    phrase = "fresh passing `skill-opt.validation-gate-receipt` v1"
    assert phrase in skill
    assert phrase in workflow
    assert phrase in passbook
    assert "do not replace this requirement with a Booster-local parser" in skill
    assert "final `skill-change-gate`" in workflow
