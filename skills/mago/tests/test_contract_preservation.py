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
        for phrase in ("Core Principle", "Loop Contract", "Minimal State Expectations", "Reference Handling and Failure Policy"):
            self.assertIn(phrase, flow)

    def test_all_original_functional_files_remain_present(self) -> None:
        original_files = {
            'SKILL.md',
            'agents/openai.yaml',
            'assets/flows/discovery-order-prepare-define-loop.md',
            'assets/templates/adr.md.template',
            'assets/templates/complexity-reduction-plan.md.template',
            'assets/templates/contract-spec.md.template',
            'assets/templates/define-queue.yaml.template',
            'assets/templates/discovery-candidate.md.template',
            'assets/templates/discovery-index.yaml.template',
            'assets/templates/discovery-state.json.template',
            'assets/templates/execution-handoff-plan.md.template',
            'assets/templates/manifest.yaml.template',
            'assets/templates/migration-strategy.md.template',
            'assets/templates/notes.md.template',
            'assets/templates/observability-design.md.template',
            'assets/templates/open-questions.md.template',
            'assets/templates/operational-requirements.md.template',
            'assets/templates/prd.md.template',
            'assets/templates/security-and-risk-considerations.md.template',
            'assets/templates/spec-catalog.yaml.template',
            'assets/templates/tasks.md.template',
            'assets/templates/technical-design.md.template',
            'assets/templates/validation.md.template',
            'evals/activation-scenarios.json',
            'examples/activation-scenarios.json',
            'examples/hardening-scenarios.json',
            'references/activation-routing.md',
            'references/adr-quality.md',
            'references/architecture-decisions.md',
            'references/artifacts/discovery-order.md',
            'references/artifacts/technical-design.md',
            'references/artifacts/templates-and-status.md',
            'references/canonical-paths.md',
            'references/common-planning.md',
            'references/complexity-reduction-planning.md',
            'references/evidence-contract.md',
            'references/markdown-writing.md',
            'references/modes/adapt.md',
            'references/modes/complexity-reduction.md',
            'references/modes/define-product.md',
            'references/modes/define-tasks.md',
            'references/modes/define.md',
            'references/modes/discovery.md',
            'references/modes/order.md',
            'references/modes/prepare-define.md',
            'references/modes/refine-product.md',
            'references/modes/refine-tasks.md',
            'references/modes/refine.md',
            'references/modes/reshape-tasks.md',
            'references/modes/technical-design.md',
            'references/operating-rules.md',
            'references/planning-execution-handoff.md',
            'references/rfc-quality.md',
            'references/roadmap-evidence-input.md',
            'references/shared-artifact-ownership.md',
            'references/specialist-spellbook.md',
            'references/technical-artifact-standards.md',
            'references/validation-and-packaging.md',
            'scripts/mago_utils.py',
            'scripts/normalize_package.py',
            'scripts/package_skill.py',
            'scripts/update_template_lists.py',
            'scripts/validate_activation_scenarios.py',
            'scripts/validate_artifact.py',
            'scripts/validate_boundary.py',
            'scripts/validate_evidence_contract.py',
            'scripts/validate_package.py',
            'scripts/validate_planning_execution_handoff.py',
            'scripts/validate_repo_board.py',
            'scripts/validate_skill_package.py',
            'scripts/validate_technical_design.py',
            'scripts/write_artifact_scaffold.py',

        }
        missing = sorted(path for path in original_files if not (ROOT / path).is_file())
        self.assertEqual(missing, [], f"Original functional files removed: {missing}")

    def test_repo_board_validator_retains_original_validation_surfaces(self) -> None:
        source = (ROOT / "scripts/validate_repo_board.py").read_text(encoding="utf-8")
        for function_name in (
            "validate_segment",
            "iter_files",
            "validate_root_artifact_location",
            "validate_placeholders",
            "validate_define_queue",
            "validate_discovery_index",
            "validate_spec_packages",
        ):
            self.assertIn(f"def {function_name}(", source)



if __name__ == "__main__":
    unittest.main()
