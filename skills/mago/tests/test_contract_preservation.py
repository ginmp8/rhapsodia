from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContractPreservationTests(unittest.TestCase):
    def run_gate(self, script: str) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / script), str(ROOT)],
            cwd=str(ROOT), text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_planning_execution_handoff_contract(self) -> None:
        self.run_gate("validate_planning_execution_handoff.py")

    def test_generated_view_contract(self) -> None:
        self.run_gate("validate_generated_view_contract.py")

    def test_task_contract_remains_reachable(self) -> None:
        template = (ROOT / "assets/templates/tasks.md.template").read_text(encoding="utf-8-sig")
        contract = (ROOT / "references/artifacts/templates-and-status.md").read_text(encoding="utf-8")
        self.assertIn("references/artifacts/templates-and-status.md", template)
        for phrase in ("Canonical Task Contract", "Affected boundary", "Why this reasoning is sufficient", "Execution Handoff Consistency"):
            self.assertIn(phrase, contract)

    def test_orchestration_flow_retains_state_and_failure_contracts(self) -> None:
        flow = (ROOT / "assets/flows/discovery-order-prepare-define-loop.md").read_text(encoding="utf-8")
        for phrase in ("Core Principle", "Loop Contract", "Minimal State Expectations", "Traceability and Failure Policy"):
            self.assertIn(phrase, flow)


if __name__ == "__main__":
    unittest.main()
