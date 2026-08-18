from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_assurance_contract import validate_assurance_contract


class AssuranceContractTests(unittest.TestCase):
    @property
    def skill_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def test_current_assurance_contract_passes(self) -> None:
        result = validate_assurance_contract(self.skill_root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["critical_gate_coverage"], [f"G{i}" for i in range(1, 9)])

    def test_measured_claim_requires_validator(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "assurance.json"
            data = json.loads((self.skill_root / "references" / "assurance-contract.json").read_text(encoding="utf-8"))
            data["claims"][1]["validators"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            result = validate_assurance_contract(self.skill_root, path)
            self.assertTrue(any("requires at least one validator" in error for error in result["errors"]))

    def test_missing_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "assurance.json"
            data = json.loads((self.skill_root / "references" / "assurance-contract.json").read_text(encoding="utf-8"))
            data["claims"][0]["artifacts"] = ["references/does-not-exist.md"]
            path.write_text(json.dumps(data), encoding="utf-8")
            result = validate_assurance_contract(self.skill_root, path)
            self.assertTrue(any("references missing file" in error for error in result["errors"]))

    def test_activation_precision_cannot_be_claimed_as_measured(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "assurance.json"
            data = json.loads((self.skill_root / "references" / "assurance-contract.json").read_text(encoding="utf-8"))
            data["claims"][-1]["evidence_status"] = "measured"
            data["claims"][-1]["validators"] = ["scripts/validate_activation_scenarios.py"]
            data["claims"][-1]["ledger_gates"] = ["activation-scenarios"]
            path.write_text(json.dumps(data), encoding="utf-8")
            result = validate_assurance_contract(self.skill_root, path)
            self.assertTrue(any("activation precision must remain planned" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
