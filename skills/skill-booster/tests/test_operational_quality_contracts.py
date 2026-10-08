from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_control_plane_exposes_trace_and_runtime_trust() -> None:
    skill = text("SKILL.md")
    first_100 = "\n".join(skill.splitlines()[:100])
    assert "catalog-pressure/coexistence" in first_100
    assert "runtime trust boundaries" in first_100
    assert "must not silently expand authority" in first_100


def test_evaluation_contract_covers_catalog_trace_judge_and_field_evidence() -> None:
    contract = text("references/evaluation-contract.md")
    for phrase in (
        "### Catalog pressure and coexistence",
        "### Agentic trace evaluation",
        "### LLM-judge calibration",
        "### Continuous field-evidence loop",
    ):
        assert phrase in contract


def test_safety_contract_separates_runtime_trust_and_authority() -> None:
    policy = text("references/transformation-and-safety-policy.md")
    assert "Skill-package trust and runtime-input trust are separate" in policy
    assert "required capabilities" in policy
    assert "permitted authority" in policy
    assert "forbidden authority" in policy
    assert "time/version-bound guidance" in policy

if __name__ == "__main__":
    test_control_plane_exposes_trace_and_runtime_trust()
    test_evaluation_contract_covers_catalog_trace_judge_and_field_evidence()
    test_safety_contract_separates_runtime_trust_and_authority()
    print("ok")
