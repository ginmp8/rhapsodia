from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_hypothesis_backlog.py"
SPEC = importlib.util.spec_from_file_location("validate_hypothesis_backlog", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def source(source_id: str = "E001", status: str = "observed") -> dict:
    return {
        "id": source_id,
        "status": status,
        "identity": f"sha256:{source_id.lower()}-fixture",
        "summary": "Observed evidence fixture for deterministic validator tests.",
    }


def metric(metric_id: str = "M001", role: str = "primary", status: str = "active") -> dict:
    return {"id": metric_id, "role": role, "status": status, "name": f"Metric {metric_id}"}


def hypothesis(
    hid: str = "H001",
    *,
    subject_key: str = "selection",
    mechanism_key: str = "require-evaluator",
    effect_key: str = "unsupported-tests",
    evaluator_status: str = "available",
    evidence_refs: list[str] | None = None,
    metric_ids: list[str] | None = None,
    observable: str = "Unsupported selected experiments decrease to zero.",
    recommendation: str = "test-now",
    conflicts_with: list[str] | None = None,
    depends_on: list[str] | None = None,
    impact: int = 4,
    confidence: int = 4,
    testability: int = 5,
    risk: int = 1,
    cost: int = 2,
    gate_effect: str = "non-blocking",
) -> dict:
    area = "validation"
    return {
        "id": hid,
        "kind": "testable-hypothesis",
        "title": f"Hypothesis {hid}",
        "statement": "If the bounded change is tested, the named observable should improve because the mechanism is evidenced.",
        "target_area": area,
        "subject_key": subject_key,
        "mechanism_key": mechanism_key,
        "effect_key": effect_key,
        "dedupe_key": f"{area}:{subject_key}:{mechanism_key}:{effect_key}",
        "evidence_refs": evidence_refs or ["E001"],
        "mechanism": "The current evidence shows this bounded mechanism is connected to the observed failure mode.",
        "expected_effect": {
            "observable": observable,
            "direction": "reduce",
            "metric_ids": metric_ids or ["M001"],
        },
        "evaluator": {"id": f"EV-{hid}", "status": evaluator_status, "method": "deterministic validator regression"},
        "acceptance_criteria": ["The observable satisfies the predeclared deterministic gate."],
        "impact": impact,
        "confidence": confidence,
        "testability": testability,
        "risk": risk,
        "cost": cost,
        "gate_effect": gate_effect,
        "recommendation": recommendation,
        "conflicts_with": conflicts_with or [],
        "depends_on": depends_on or [],
    }


def backlog(items: list[dict] | None = None, sources: list[dict] | None = None, metrics: list[dict] | None = None) -> dict:
    sources = [source()] if sources is None else sources
    items = [hypothesis()] if items is None else items
    ranked_guess = [item["id"] for item in items if item.get("kind") == "testable-hypothesis" and item.get("recommendation") == "test-now"]
    data = {
        "schema_version": "2.0",
        "target": {"name": "fixture-skill", "identity": "sha256:fixture-target"},
        "mode": "backlog-discovery",
        "evidence_status": "observed",
        "recommendation": "test-hypotheses",
        "evidence_snapshot": {"snapshot_id": "", "sources": sources},
        "metrics": [metric()] if metrics is None else metrics,
        "items": items,
        "selected_for_testing": ranked_guess[:1],
        "next_hypothesis_id": ranked_guess[0] if ranked_guess else None,
    }
    data["evidence_snapshot"]["snapshot_id"] = validator.canonical_snapshot_id(sources)
    return data


def codes(result: dict) -> set[str]:
    return {d["code"] for d in result.get("diagnostics", [])}


class ValidatorRegressionTests(unittest.TestCase):
    def test_evidence_gap_is_not_promoted_to_hypothesis(self) -> None:
        sources = [source(status="gap")]
        item = {
            "id": "G001",
            "kind": "evidence-gap",
            "title": "Missing holdout evidence",
            "statement": "Holdout behavior has not been measured, so mutation is not justified yet.",
            "target_area": "evidence",
            "evidence_refs": ["E001"],
            "recommendation": "gather-evidence",
            "conflicts_with": [],
            "depends_on": [],
        }
        data = backlog([item], sources=sources, metrics=[])
        data["recommendation"] = "gather-evidence"
        data["selected_for_testing"] = []
        data["next_hypothesis_id"] = None
        result = validator.validate(data)
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["eligible_ids"])

    def test_duplicate_hypothesis_is_rejected(self) -> None:
        h1 = hypothesis("H001")
        h2 = hypothesis("H002")
        data = backlog([h1, h2])
        result = validator.validate(data)
        self.assertIn("DUPLICATE_HYPOTHESIS", codes(result))
        self.assertEqual("fail", result["status"])

    def test_conflicting_hypotheses_cannot_be_selected_together(self) -> None:
        h1 = hypothesis("H001", conflicts_with=["H002"], impact=5, testability=5)
        h2 = hypothesis(
            "H002",
            subject_key="selection-2",
            mechanism_key="alternate-mechanism",
            effect_key="alternate-effect",
            conflicts_with=["H001"],
            impact=4,
            testability=4,
        )
        data = backlog([h1, h2])
        data["selected_for_testing"] = ["H001", "H002"]
        data["next_hypothesis_id"] = "H001"
        result = validator.validate(data)
        self.assertIn("SELECTED_CONFLICT", codes(result))

    def test_missing_evaluator_cannot_be_test_now(self) -> None:
        data = backlog([hypothesis(evaluator_status="missing")])
        result = validator.validate(data)
        self.assertIn("MISSING_EVALUATOR", codes(result))
        self.assertNotIn("H001", result["eligible_ids"])

    def test_saturated_metric_requires_active_auxiliary(self) -> None:
        data = backlog(metrics=[metric(status="saturated")])
        result = validator.validate(data)
        self.assertIn("SATURATED_OR_UNKNOWN_METRIC", codes(result))
        self.assertIn("SATURATED_NO_AUXILIARY", codes(result))

    def test_unmeasurable_effect_cannot_be_test_now(self) -> None:
        data = backlog([hypothesis(observable="")])
        result = validator.validate(data)
        self.assertIn("UNMEASURABLE_EFFECT", codes(result))
        self.assertNotIn("H001", result["eligible_ids"])

    def test_ranking_tie_uses_testability_before_confidence(self) -> None:
        h1 = hypothesis("H001", testability=4, confidence=4, impact=4)
        h2 = hypothesis(
            "H002",
            subject_key="selection-2",
            mechanism_key="require-metric",
            effect_key="unsupported-tests-2",
            testability=5,
            confidence=3,
            impact=4,
        )
        # Both score 10; H002 wins the explicit testability tie-break.
        data = backlog([h1, h2])
        data["selected_for_testing"] = ["H002"]
        data["next_hypothesis_id"] = "H002"
        result = validator.validate(data)
        self.assertEqual("pass", result["status"])
        self.assertEqual(["H002", "H001"], result["ranked_ids"])

    def test_same_input_returns_same_ranking_and_diagnostics(self) -> None:
        data = backlog()
        first = validator.validate(copy.deepcopy(data))
        second = validator.validate(copy.deepcopy(data))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
