from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_activation_scenarios import validate


class ActivationBoundarySemanticsTests(unittest.TestCase):
    def copy_suite(self, mutator=None) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="mago-activation-boundary-"))
        (tmp / "examples").mkdir()
        source = ROOT / "examples" / "activation-scenarios.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        if mutator is not None:
            mutator(data)
        (tmp / "examples" / "activation-scenarios.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        self.addCleanup(shutil.rmtree, tmp)
        return tmp

    def test_current_boundary_contracts_pass(self) -> None:
        self.assertEqual(validate(ROOT)["status"], "pass")

    def test_mutable_catalog_and_queue_boundary_is_rejected(self) -> None:
        def mutate(data):
            item = next(x for x in data["scenarios"] if x["id"] == "activate-order-backlog")
            item["expected_boundary"] = "update spec catalog and define queue only under the resolved board root"
            item.pop("boundary_contract", None)
        report = validate(self.copy_suite(mutate))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("prohibited legacy mutation" in e or "structured boundary_contract" in e for e in report["errors"]), report)

    def test_multi_spec_prepare_define_is_rejected(self) -> None:
        def mutate(data):
            item = next(x for x in data["scenarios"] if x["id"] == "activate-prepare-define-shells")
            item["prompt"] = "Seed package shells for <spec_id> and <spec_id>."
            item["boundary_contract"]["cardinality"] = "multiple-specs"
        report = validate(self.copy_suite(mutate))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("exactly-one-spec" in e or "exactly one <spec_id>" in e for e in report["errors"]), report)


if __name__ == "__main__":
    unittest.main()
