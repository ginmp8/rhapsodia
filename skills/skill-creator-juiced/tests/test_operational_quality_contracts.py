from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_control_plane_is_eval_first_and_trust_aware() -> None:
    skill = text("SKILL.md")
    first_100 = "\n".join(skill.splitlines()[:100])
    assert "seed evaluation and baseline/proof-of-need" in first_100
    assert "catalog coexistence" in first_100
    assert "cannot silently expand skill authority" in first_100


def test_evaluation_contract_covers_judge_trace_catalog_and_field_evidence() -> None:
    contract = text("references/evaluation-and-generalization.md")
    for phrase in (
        "### LLM-judge calibration",
        "skill/resource selection",
        "increasing catalog pressure",
        "Maintain a field-evidence loop",
    ):
        assert phrase in contract


def test_design_and_portability_contracts_cover_proof_authority_and_freshness() -> None:
    design = text("references/design-principles.md")
    portability = text("references/host-portability.md")
    assert "proof-of-need" in design
    assert "authority budget" in design
    assert "freshness-sensitive" in design
    assert "open Agent Skills specification can change" in portability
    assert "permitted authority" in portability
    assert "forbidden authority" in portability

if __name__ == "__main__":
    test_control_plane_is_eval_first_and_trust_aware()
    test_evaluation_contract_covers_judge_trace_catalog_and_field_evidence()
    test_design_and_portability_contracts_cover_proof_authority_and_freshness()
    print("ok")
