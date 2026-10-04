from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _swp_common import sha256_file  # noqa: E402
from apply_transaction import apply  # noqa: E402
from validate_sequential import validate_cycle  # noqa: E402
from verify_evals import verify  # noqa: E402
from _fixtures import make_cycle  # noqa: E402


def codes(report: dict) -> set[str]:
    return {d["code"] for d in report["diagnostics"]}


def add_traceability(root: Path, *, include_validation: bool = True, task_requirement: str = "req001") -> None:
    prd = root / "specs/spec001/prd.md"
    prd.write_text(
        "# context\n\n# functional requirements\n\n"
        "- Requirement ID: req001\n"
        "  - Statement: preserve deterministic behavior\n\n"
        "# acceptance criteria\n\n- testable\n",
        encoding="utf-8",
    )
    tasks = root / "specs/spec001/tasks.md"
    text = tasks.read_text(encoding="utf-8")
    text = text.replace("  - Validation: test\n", f"  - Satisfies: {task_requirement}\n  - Validation: test\n")
    tasks.write_text(text, encoding="utf-8")
    validation = root / "specs/spec001/validation.md"
    if include_validation:
        validation.write_text(
            "# validation strategy\n\n"
            "- Validation ID: val001\n"
            "  - Covers: req001\n"
            "  - Evidence: focused regression test\n",
            encoding="utf-8",
        )


class ResearchRegressionTests(unittest.TestCase):
    def test_transaction_identity_is_stable_when_equivalent_cycle_moves(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            txids = []
            for parent_name in ("clone-a", "clone-b"):
                parent = base / parent_name
                parent.mkdir()
                root = make_cycle(parent)
                target = root / "specs/spec001/notes.md"
                candidate = parent / "candidate-notes.md"
                candidate.write_text("# assumptions\n\nportable identity\n", encoding="utf-8")
                plan = {
                    "plan_version": 1,
                    "mode": "refine",
                    "cycle_root": str(root),
                    "writes": [{
                        "path": "specs/spec001/notes.md",
                        "source": str(candidate),
                        "expected_before_sha256": sha256_file(target),
                    }],
                    "post_validate": {"mode": "refine", "spec_id": "spec001"},
                }
                plan_path = parent / "plan.json"
                receipt_path = parent / "receipt.json"
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                result = apply(plan_path, receipt_path)
                self.assertEqual("applied", result["status"])
                txids.append(result["transaction_id"])
            self.assertEqual(txids[0], txids[1])

    def test_success_receipt_declares_semantic_identity_contract(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            candidate = base / "candidate-notes.md"
            candidate.write_text("# assumptions\n\nreceipt identity\n", encoding="utf-8")
            plan = {
                "plan_version": 1,
                "mode": "refine",
                "cycle_root": str(root),
                "writes": [{
                    "path": "specs/spec001/notes.md",
                    "source": str(candidate),
                    "expected_before_sha256": sha256_file(target),
                }],
                "post_validate": {"mode": "refine", "spec_id": "spec001"},
            }
            plan_path = base / "plan.json"
            receipt_path = base / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt_path)
            self.assertEqual(2, result["transaction_identity_version"])
            self.assertEqual("01.00.00", result["cycle_version"])
            self.assertIn("cycle_root", result)

    def test_verify_evals_checks_all_versioned_frozen_manifests(self):
        with tempfile.TemporaryDirectory() as td:
            copy_root = Path(td) / "sequential-work-packaging"
            import shutil
            shutil.copytree(ROOT, copy_root)
            report = verify(copy_root)
            self.assertEqual("pass", report["status"])
            (copy_root / "evals/scenarios-v2.json").write_text("{}\n", encoding="utf-8")
            report = verify(copy_root)
            self.assertEqual("fail", report["status"])
            self.assertTrue(any(e.get("code") == "FROZEN_EVAL_CHANGED" for e in report["errors"]))

    def test_manifest_schema_version_must_be_supported_and_match_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            manifest = root / "specs/spec001/manifest.yaml"
            manifest.write_text(
                manifest.read_text(encoding="utf-8").replace("schema_version: 1", "schema_version: 2", 1),
                encoding="utf-8",
            )
            report = validate_cycle(root, "define", "spec001")
            self.assertEqual("fail", report["status"])
            self.assertIn("MANIFEST_SCHEMA_UNSUPPORTED", codes(report))

    def test_untraced_structural_package_is_defined_not_execution_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            report = validate_cycle(root, "define", "spec001")
            self.assertEqual("pass", report["status"])
            self.assertEqual("defined", report["readiness"]["spec001"]["state"])
            self.assertIn("REQUIREMENT_TRACEABILITY_NOT_DECLARED", codes(report))

    def test_bidirectionally_covered_requirements_make_package_execution_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            add_traceability(root)
            report = validate_cycle(root, "define", "spec001")
            self.assertEqual("pass", report["status"])
            self.assertEqual("execution_ready", report["readiness"]["spec001"]["state"])
            self.assertEqual([], report["readiness"]["spec001"]["gaps"])

    def test_unknown_requirement_reference_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            add_traceability(root, task_requirement="req999")
            report = validate_cycle(root, "define", "spec001")
            self.assertEqual("fail", report["status"])
            self.assertIn("TASK_REQUIREMENT_UNKNOWN", codes(report))

    def test_requirement_without_validation_is_structurally_valid_but_not_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            add_traceability(root, include_validation=False)
            report = validate_cycle(root, "define", "spec001")
            self.assertEqual("pass", report["status"])
            self.assertEqual("defined", report["readiness"]["spec001"]["state"])
            self.assertIn("REQUIREMENT_WITHOUT_VALIDATION", codes(report))


if __name__ == "__main__":
    unittest.main()
