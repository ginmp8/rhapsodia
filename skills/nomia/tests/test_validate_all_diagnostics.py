from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_all import Gate, root_cause_id, summarize_root_causes  # noqa: E402


def gate(name: str, text: str) -> Gate:
    return Gate(name=name, command=["python", name], returncode=1, stdout=text, stderr="")


class ValidateAllDiagnosticsTests(unittest.TestCase):
    def test_protected_hash_drift_is_grouped_across_gates(self) -> None:
        message = (
            "ERROR: current protected file hash changed for agents/openai.yaml: expected "
            + "1" * 64
            + ", got "
            + "2" * 64
        )
        gates = [gate("release-contract", message), gate("contract-preservation", message), gate("unit-tests", message)]
        causes = summarize_root_causes(gates)
        self.assertEqual(len(causes), 1)
        self.assertEqual(causes[0]["gate_count"], 3)
        self.assertEqual(causes[0]["impacted_gates"], ["contract-preservation", "release-contract", "unit-tests"])
        self.assertTrue(root_cause_id(gates[0]).startswith("protected-file-hash-drift:agents/openai.yaml:"))

    def test_independent_failures_keep_independent_root_causes(self) -> None:
        gates = [gate("documentation-links", "broken link"), gate("unit-tests", "assertion failed")]
        causes = summarize_root_causes(gates)
        self.assertEqual(len(causes), 2)
        self.assertTrue(all(item["gate_count"] == 1 for item in causes))


if __name__ == "__main__":
    unittest.main()
