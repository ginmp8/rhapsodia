from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_research_discovery.py"
SPEC = importlib.util.spec_from_file_location("validate_research_discovery", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def artifact() -> dict:
    sources = [
        {
            "id": "S001",
            "locator": "doi:10.0000/example",
            "identity": "doi:10.0000/example",
            "authority": "primary",
            "evidence_state": "pinned",
        },
        {
            "id": "S002",
            "locator": "sha256:local-evaluator-note",
            "identity": "sha256:local-evaluator-note",
            "authority": "user-provided",
            "evidence_state": "snapshotted",
        },
    ]
    findings = [
        {
            "id": "F001",
            "statement": "Negative testing can expose a weak candidate mechanism before mutation.",
            "source_refs": ["S001"],
            "stance": "supporting",
        },
        {
            "id": "F002",
            "statement": "The deciding evaluator is independent from the discovery evidence.",
            "source_refs": ["S002"],
            "stance": "boundary",
        },
    ]
    data = {
        "schema_version": "1.0",
        "target": {"name": "fixture-skill", "identity": "sha256:target"},
        "research_policy": "if-needed",
        "research_status": "complete",
        "evidence_sufficiency": "sufficient",
        "recommendation": "proceed-to-v2-handoff",
        "research_corpus": {"corpus_id": "", "sources": sources, "findings": findings},
        "evidence_roles": [
            {"evidence_id": "E001", "role": "discovery", "finding_refs": ["F001"]},
            {"evidence_id": "EV001", "role": "validation", "finding_refs": ["F002"]},
        ],
        "hypothesis_checks": [
            {
                "hypothesis_id": "H001",
                "discovery_evidence_refs": ["E001"],
                "supporting_finding_refs": ["F001"],
                "counterevidence_finding_refs": [],
                "alternative_explanations": ["The observed failure may instead be caused by evaluator ambiguity."],
                "falsification": {
                    "status": "attempted",
                    "criteria": ["Reject the mechanism if negative-test cases do not change the diagnostic outcome."],
                    "search_summary": "Searched for contradicting evidence and alternative mechanisms before handoff.",
                },
                "evaluator": {"identity": "sha256:frozen-evaluator", "exposure": "held-out"},
            }
        ],
        "evidence_gaps": [
            {"id": "G001", "question": "Would a second source change the mechanism?", "status": "open", "information_value": 5, "collection_cost": 3},
            {"id": "G002", "question": "Would a formatting example reduce ambiguity?", "status": "open", "information_value": 3, "collection_cost": 1},
        ],
        "ranked_gap_ids": ["G001", "G002"],
    }
    data["research_corpus"]["corpus_id"] = validator.canonical_corpus_id(sources, findings)
    return data


def codes(result: dict) -> set[str]:
    return {item["code"] for item in result["diagnostics"]}


class ResearchDiscoveryValidatorTests(unittest.TestCase):
    def test_same_input_is_deterministic(self) -> None:
        data = artifact()
        self.assertEqual(validator.validate(copy.deepcopy(data)), validator.validate(copy.deepcopy(data)))

    def test_corpus_id_mismatch_is_rejected(self) -> None:
        data = artifact()
        data["research_corpus"]["corpus_id"] = "sha256:wrong"
        result = validator.validate(data)
        self.assertEqual("fail", result["status"])
        self.assertIn("CORPUS_ID_MISMATCH", codes(result))

    def test_validation_evidence_cannot_support_discovery(self) -> None:
        data = artifact()
        data["hypothesis_checks"][0]["discovery_evidence_refs"] = ["EV001"]
        result = validator.validate(data)
        self.assertIn("VALIDATION_LEAKAGE", codes(result))

    def test_falsification_must_be_attempted_before_handoff(self) -> None:
        data = artifact()
        data["hypothesis_checks"][0]["falsification"]["status"] = "blocked"
        result = validator.validate(data)
        self.assertIn("FALSIFICATION_NOT_ATTEMPTED", codes(result))

    def test_shared_evaluator_cannot_decide_research_backed_handoff(self) -> None:
        data = artifact()
        data["hypothesis_checks"][0]["evaluator"]["exposure"] = "shared"
        result = validator.validate(data)
        self.assertIn("EVALUATOR_NOT_INDEPENDENT", codes(result))

    def test_required_research_must_complete_before_handoff(self) -> None:
        data = artifact()
        data["research_policy"] = "required"
        data["research_status"] = "blocked"
        result = validator.validate(data)
        self.assertIn("REQUIRED_RESEARCH_INCOMPLETE", codes(result))
        self.assertIn("RESEARCH_BLOCKED_HANDOFF", codes(result))

    def test_insufficient_evidence_cannot_proceed(self) -> None:
        data = artifact()
        data["evidence_sufficiency"] = "insufficient"
        result = validator.validate(data)
        self.assertIn("INSUFFICIENT_FOR_HANDOFF", codes(result))

    def test_gap_ranking_uses_information_value_then_cost(self) -> None:
        data = artifact()
        # G003 ties G001 on score (3) and information value (5), but costs less and should rank first.
        data["evidence_gaps"].append(
            {"id": "G003", "question": "Would a cheap high-value check falsify the mechanism?", "status": "open", "information_value": 5, "collection_cost": 2}
        )
        data["ranked_gap_ids"] = ["G003", "G001", "G002"]
        result = validator.validate(data)
        self.assertIn(result["status"], {"pass", "pass-with-warnings"})
        self.assertEqual(["G003", "G001", "G002"], result["ranked_gap_ids"])

    def test_wrong_gap_order_is_rejected(self) -> None:
        data = artifact()
        data["ranked_gap_ids"] = ["G002", "G001"]
        result = validator.validate(data)
        self.assertIn("NONDETERMINISTIC_GAP_RANKING", codes(result))


if __name__ == "__main__":
    unittest.main()
