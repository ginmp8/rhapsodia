from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_package import validate_task_contract  # noqa: E402


def task(task_id: str, task_type: str, dependency: str) -> str:
    return "\n".join([
        f"- [ ] {task_id}: Bounded work",
        "  - Objective: Produce one bounded result.",
        "  - Affected boundary: src/service",
        f"  - Task type: {task_type}",
        "  - Reasoning: medium",
        "  - Why this reasoning is sufficient: Scope and proof are explicit.",
        "  - Specialist Support: not_required",
        "  - Required LOAD: none",
        "  - Optional LOAD: none",
        "  - Selection Hint: No specialist is required.",
        f"  - Dependencies: {dependency}",
        "  - Requirements: REQ-001",
        "  - Acceptance: AC-001",
        "  - Decisions: DECISION-001",
        "  - Validations: VAL-001",
        "  - Validation: Run the declared package validator.",
        "  - Expected result: The bounded result is verifiable.",
    ])


def document(*, evidence: bool = True, omit_core: bool = False) -> str:
    n_a = ["Not applicable: Repository evidence shows no separate integration boundary."]
    if evidence:
        n_a.append("Evidence: REQ-001 and src/service contract inspection.")
    core = (
        "Not applicable: No core work exists.\nEvidence: REQ-001."
        if omit_core else task("task002", "implementation", "task001")
    )
    return "\n\n".join([
        "# Tasks - Example\n\n## Execution Rules\n\n- Follow dependencies.",
        "## Phase 1 - Foundation\n\n" + task("task001", "analysis", "none"),
        "## Phase 2 - Core Implementation\n\n" + core,
        "## Phase 3 - Integration\n\n" + "\n".join(n_a),
        "## Phase 4 - Validation and Hardening\n\n" + task("task003", "validation", "task002"),
        "## Phase 5 - Migration and Rollout\n\nNot applicable: No data, contract, or rollout transition is triggered.\nEvidence: DECISION-001 and repository deployment inspection.",
    ]) + "\n"


class OptionalTaskPhaseV2Tests(unittest.TestCase):
    def validate(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="mago-phases-") as tmp:
            path = Path(tmp) / "tasks.md"
            path.write_text(content, encoding="utf-8")
            _, errors, _ = validate_task_contract(path, "standard")
            return errors

    def test_standard_accepts_evidence_backed_optional_phases(self) -> None:
        self.assertEqual(self.validate(document()), [])

    def test_standard_rejects_optional_phase_without_evidence(self) -> None:
        errors = self.validate(document(evidence=False))
        self.assertTrue(any("needs `Evidence:" in error for error in errors), errors)

    def test_standard_keeps_core_implementation_mandatory(self) -> None:
        errors = self.validate(document(omit_core=True))
        self.assertTrue(any("requires at least one task in Phase 2" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
