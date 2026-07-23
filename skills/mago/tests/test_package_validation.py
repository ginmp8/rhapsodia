from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_package import CONDITIONAL_ARTIFACTS, validate_package
from validate_repo_board import validate as validate_repo_board


PHASES = (
    (1, "Foundation", "analysis"),
    (2, "Core Implementation", "implementation"),
    (3, "Integration", "integration"),
    (4, "Validation and Hardening", "validation"),
    (5, "Migration and Rollout", "rollout"),
)


def task_block(task_id: str, title: str, task_type: str, dependencies: str, traceability: bool) -> str:
    fields = [
        f"- [ ] {task_id}: {title}",
        "  - Objective: Produce one bounded planning result.",
        "  - Affected boundary: src/export-service",
        f"  - Task type: {task_type}",
        "  - Reasoning: medium",
        "  - Why this reasoning is sufficient: The affected boundary and validation path are explicit.",
        "  - Specialist Support: not_required",
        "  - Required LOAD: none",
        "  - Optional LOAD: none",
        "  - Selection Hint: No specialist is needed for this bounded task.",
        f"  - Dependencies: {dependencies}",
    ]
    if traceability:
        fields.extend(
            [
                "  - Requirements: REQ-001",
                "  - Acceptance: AC-001",
                "  - Decisions: none",
                "  - Validations: VAL-001",
            ]
        )
    fields.extend(
        [
            "  - Validation: Validate the declared result with the package fixture.",
            "  - Expected result: The bounded planning result is complete and verifiable.",
        ]
    )
    return "\n".join(fields)


def tasks_document(profile: str = "standard") -> str:
    lines = ["# Tasks - Export", "", "## Execution Rules", "", "- Follow the declared order.", ""]
    if profile == "quick":
        lines.extend(
            [
                "## Phase 1 - Foundation",
                "",
                task_block("task001", "Confirm boundary", "analysis", "none", False),
                "",
                "## Phase 2 - Core Implementation",
                "",
                task_block("task002", "Plan bounded change", "implementation", "task001", False),
                "",
                "## Phase 3 - Integration",
                "",
                "Not applicable: The change has no additional integration boundary.",
                "",
                "## Phase 4 - Validation and Hardening",
                "",
                "Not applicable: Validation is contained in task002 for this bounded quick package.",
                "",
                "## Phase 5 - Migration and Rollout",
                "",
                "Not applicable: No migration or rollout behavior changes.",
            ]
        )
        return "\n".join(lines) + "\n"

    previous = "none"
    for number, name, task_type in PHASES:
        task_id = f"task{number:03d}"
        lines.extend(
            [
                f"## Phase {number} - {name}",
                "",
                task_block(task_id, f"Plan {name.lower()}", task_type, previous, True),
                "",
            ]
        )
        previous = task_id
    return "\n".join(lines)


def artifact_decisions(required: set[str] | None = None) -> dict[str, dict[str, str]]:
    required = required or set()
    return {
        artifact: {
            "status": "required" if artifact in required else "not_applicable",
            "rationale": (
                "Repository evidence triggers this focused artifact."
                if artifact in required
                else "Repository evidence shows this concern is not applicable."
            ),
        }
        for artifact in CONDITIONAL_ARTIFACTS
    }


class PackageValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        if yaml is None:
            self.skipTest("PyYAML required")
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_package(
        self,
        profile: str = "standard",
        *,
        required_conditional: set[str] | None = None,
        decisions: dict[str, dict[str, str]] | None = None,
    ) -> Path:
        package = self.root / "package"
        package.mkdir(parents=True, exist_ok=True)
        manifest = {
            "kind": "mago-spec-manifest",
            "spec_id": "spec-2026-07-20-filtered-export",
            "cycle_id": "cycle-2026-07-20-q3-delivery",
            "feature_key": "filtered-export",
            "title": "Filtered export",
            "type": "feature",
            "classification": "internal",
            "profile": profile,
            "status": "planned",
            "phase": "define",
            "feature_version": "0.1.0",
            "created_at": "2026-07-20T12:00:00Z",
            "source_of_truth": {
                "registry": "../../registry/spec-2026-07-20-filtered-export.yaml",
                "prd": "prd.md",
                "tasks": "tasks.md",
                "validation": "validation.md",
                "notes": "notes.md",
            },
            "traceability": {
                "primary_discovery_file": "candidates/filtered-export.md",
                "supporting_discovery_files": [],
                "discovery_frontier": "src/export-service",
            },
            "mutation_state": {
                "status": "clean",
                "transaction_id": None,
                "inspected_digest": None,
                "planned_writes": [],
                "completed_writes": [],
                "checkpoint": None,
                "cancellation_requested": False,
                "rollback_required": False,
            },
        }
        if profile in {"standard", "governed"}:
            manifest["artifact_decisions"] = decisions if decisions is not None else artifact_decisions(required_conditional)
        elif decisions is not None:
            manifest["artifact_decisions"] = decisions
        (package / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        (package / "prd.md").write_text("# PRD\n\n## Requirements\n\n### REQ-001\n\nThe system MUST preserve selected columns.\n", encoding="utf-8")
        (package / "tasks.md").write_text(tasks_document(profile), encoding="utf-8")
        (package / "validation.md").write_text("# Validation\n\n### VAL-001\n\nValidate AC-001 for REQ-001.\n", encoding="utf-8")
        if profile in {"standard", "governed"}:
            (package / "notes.md").write_text("# Notes\n\n## Assumptions\n\n- Repository evidence is current.\n", encoding="utf-8")
        return package

    def assert_valid(self, package: Path) -> None:
        errors, warnings = validate_package(package)
        self.assertEqual(errors, [], "\n".join(errors + warnings))

    def test_valid_quick_package_accepts_explicit_non_applicable_phases(self) -> None:
        self.assert_valid(self.write_package("quick"))

    def test_valid_standard_package(self) -> None:
        self.assert_valid(self.write_package("standard"))

    def test_empty_package_is_rejected(self) -> None:
        package = self.root / "empty"
        package.mkdir()
        errors, _ = validate_package(package)
        self.assertTrue(any("missing required manifest.yaml" in error for error in errors), errors)

    def test_incomplete_profile_package_is_rejected(self) -> None:
        package = self.write_package("standard")
        (package / "prd.md").unlink()
        errors, _ = validate_package(package)
        self.assertTrue(any("missing required `prd.md`" in error for error in errors), errors)

    def test_missing_profile_is_rejected(self) -> None:
        package = self.write_package("standard")
        manifest = yaml.safe_load((package / "manifest.yaml").read_text(encoding="utf-8"))
        manifest.pop("profile")
        (package / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        errors, _ = validate_package(package)
        self.assertTrue(any("missing required key `profile`" in error for error in errors), errors)

    def test_task_dependency_cycle_is_rejected(self) -> None:
        package = self.write_package("standard")
        text = (package / "tasks.md").read_text(encoding="utf-8")
        text = text.replace("  - Dependencies: none", "  - Dependencies: task002", 1)
        text = text.replace("  - Dependencies: task001", "  - Dependencies: task001", 1)
        (package / "tasks.md").write_text(text, encoding="utf-8")
        errors, _ = validate_package(package)
        self.assertTrue(any("dependency cycle" in error for error in errors), errors)

    def test_task_self_dependency_is_rejected(self) -> None:
        package = self.write_package("standard")
        text = (package / "tasks.md").read_text(encoding="utf-8")
        text = text.replace("  - Dependencies: task001", "  - Dependencies: task002", 1)
        (package / "tasks.md").write_text(text, encoding="utf-8")
        errors, _ = validate_package(package)
        self.assertTrue(any("cannot depend on itself" in error for error in errors), errors)

    def test_missing_task_field_is_rejected(self) -> None:
        package = self.write_package("standard")
        text = (package / "tasks.md").read_text(encoding="utf-8")
        text = text.replace("  - Expected result: The bounded planning result is complete and verifiable.\n", "", 1)
        (package / "tasks.md").write_text(text, encoding="utf-8")
        errors, _ = validate_package(package)
        self.assertTrue(any("missing required field `Expected Result`" in error for error in errors), errors)

    def test_phase_task_type_mismatch_is_rejected(self) -> None:
        package = self.write_package("standard")
        text = (package / "tasks.md").read_text(encoding="utf-8")
        text = text.replace("  - Task type: implementation", "  - Task type: validation", 1)
        (package / "tasks.md").write_text(text, encoding="utf-8")
        errors, _ = validate_package(package)
        self.assertTrue(any("invalid for Phase 2" in error for error in errors), errors)

    def test_governed_requires_complete_artifact_decisions(self) -> None:
        decisions = artifact_decisions()
        decisions.pop("migration-strategy.md")
        package = self.write_package("governed", decisions=decisions)
        errors, _ = validate_package(package)
        self.assertTrue(any("must decide every conditional artifact" in error for error in errors), errors)

    def test_required_security_artifact_rejects_presence_only_content(self) -> None:
        package = self.write_package("governed", required_conditional={"security-and-risk-considerations.md"})
        (package / "security-and-risk-considerations.md").write_text(
            "# Security and Risk Considerations\n\n- Contract version: 2\n\n## Scope\n\n- Spec: present\n",
            encoding="utf-8",
        )
        errors, _ = validate_package(package)
        self.assertTrue(any("missing" in error and "heading" in error for error in errors), errors)

    def test_valid_security_artifact_passes_governed_gate(self) -> None:
        package = self.write_package("governed", required_conditional={"security-and-risk-considerations.md"})
        (package / "security-and-risk-considerations.md").write_text(
            '# Security and Risk Considerations\n\n- Contract version: 2\n\n## Scope\n\n- Spec: `spec-2026-07-20-filtered-export`\n- Security domains: authorization, sensitive_data\n- In-scope components and consumers: export API and export worker\n\n## Assets and Data Classification\n\n### ASSET-001 - Exported customer data\n\n- Classification: restricted\n- Sensitive data or secrets: customer identifiers and financial attributes\n- Retention and logging constraints: values must not be logged; generated files follow restricted-data retention\n\n## Trust Boundaries\n\n### BOUNDARY-001 - API to export worker\n\n- Source: authenticated export API\n- Destination: export worker\n- Authentication: workload identity\n- Authorization: API policy and worker-side column allowlist\n\n## Threats\n\n### THREAT-001 - Restricted column disclosure\n\n- Assets: ASSET-001\n- Trust boundaries: BOUNDARY-001\n- Threat actor: unauthorized internal caller\n- Likelihood: medium\n- Impact: high\n- Security domains: authorization, sensitive_data\n\n## Misuse and Abuse Cases\n\n### ABUSE-001 - Request restricted columns\n\n- Threats: THREAT-001\n- Observable misuse: caller submits restricted or unknown column identifiers\n- Expected prevention or detection: reject the request and record only safe metadata\n\n## Planned Controls\n\n### CONTROL-001 - Server-side column allowlist\n\n- Threats: THREAT-001\n- Abuse cases: ABUSE-001\n- Owner: export service owner\n- Validation: SECVAL-001\n- Failure behavior: deny\n\n## Risks and Residual Risk\n\n### RISK-001 - Allowlist configuration drift\n\n- Threats: THREAT-001\n- Controls: CONTROL-001\n- Residual likelihood: low\n- Residual impact: high\n- Risk authority: application security\n- Status: review_required\n- Acceptance evidence: none while review is pending\n\n## Validation Expectations for Magia\n\n### SECVAL-001 - Restricted-column negative tests\n\n- Controls: CONTROL-001\n- Threats: THREAT-001\n- Test type: negative\n- Expected evidence: contract tests proving restricted and unknown columns are rejected\n- Sensitive logging check: verify customer values and requested restricted values are absent from logs\n\n## Required Review\n\n- Security reviewer: application security\n- Compliance reviewer: data governance\n- Review evidence required before handoff closure: linked review record or unresolved blocker\n',
            encoding="utf-8",
        )
        self.assert_valid(package)

    def test_non_clean_mutation_state_blocks_handoff(self) -> None:
        package = self.write_package("standard")
        manifest = yaml.safe_load((package / "manifest.yaml").read_text(encoding="utf-8"))
        manifest["mutation_state"] = {
            "status": "in_progress",
            "transaction_id": "tx-001",
            "inspected_digest": "sha256:abc",
            "planned_writes": ["prd.md"],
            "completed_writes": [],
            "checkpoint": "staged",
            "cancellation_requested": False,
            "rollback_required": False,
        }
        (package / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        errors, _ = validate_package(package)
        self.assertTrue(any("not handoff-ready" in error for error in errors), errors)

    def test_repo_board_rejects_registered_empty_package(self) -> None:
        repo = self.root / "repo"
        cycle_cmd = [
            sys.executable,
            "-B",
            str(SCRIPTS / "create_planning_identity.py"),
            "cycle",
            "--repo-root",
            str(repo),
            "--board-id",
            "delivery",
            "--cycle-key",
            "q3-delivery",
            "--created-at",
            "2026-07-20T12:00:00Z",
        ]
        cycle = subprocess.run(cycle_cmd, capture_output=True, text=True, check=False)
        self.assertEqual(cycle.returncode, 0, cycle.stdout + cycle.stderr)
        board = repo / "docs" / "boards" / "delivery" / "2026" / "cycles" / "cycle-2026-07-20-q3-delivery"
        spec_cmd = [
            sys.executable,
            "-B",
            str(SCRIPTS / "create_planning_identity.py"),
            "spec",
            "--board-root",
            str(board),
            "--feature-key",
            "filtered-export",
            "--title",
            "Filtered export",
            "--profile",
            "quick",
            "--created-at",
            "2026-07-20T12:10:00Z",
        ]
        spec = subprocess.run(spec_cmd, capture_output=True, text=True, check=False)
        self.assertEqual(spec.returncode, 0, spec.stdout + spec.stderr)
        (board / "specs" / "spec-2026-07-20-filtered-export").mkdir()
        errors, _ = validate_repo_board(repo, board_root_override=str(board))
        self.assertTrue(any("missing required manifest.yaml" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
