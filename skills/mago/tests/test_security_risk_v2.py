from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_security_risk import validate

GOLDEN = ROOT / "examples" / "golden" / "security-v2" / "security-and-risk-considerations.md"


class SecurityRiskV2Tests(unittest.TestCase):
    def validate_text(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="mago-security-v2-") as tmp:
            path = Path(tmp) / "security-and-risk-considerations.md"
            path.write_text(text, encoding="utf-8")
            return validate(path, require_v2=True)

    def test_valid_v2_security_graph_passes(self) -> None:
        self.assertEqual(validate(GOLDEN, require_v2=True), [])

    def test_orphan_threat_is_rejected(self) -> None:
        text = GOLDEN.read_text(encoding="utf-8").replace("- Threats: THREAT-001\n- Abuse cases", "- Threats: THREAT-999\n- Abuse cases")
        errors = self.validate_text(text)
        self.assertTrue(any("unknown `THREAT-999`" in error for error in errors), errors)
        self.assertTrue(any("THREAT-001` has no planned control" in error for error in errors), errors)

    def test_high_impact_alert_only_control_is_rejected(self) -> None:
        text = GOLDEN.read_text(encoding="utf-8").replace("- Failure behavior: deny", "- Failure behavior: alert")
        errors = self.validate_text(text)
        self.assertTrue(any("no fail-closed protective control" in error for error in errors), errors)

    def test_control_validation_link_must_be_reciprocal(self) -> None:
        text = GOLDEN.read_text(encoding="utf-8").replace("- Controls: CONTROL-001\n- Threats: THREAT-001", "- Controls: CONTROL-999\n- Threats: THREAT-001")
        errors = self.validate_text(text)
        self.assertTrue(any("unknown `CONTROL-999`" in error for error in errors), errors)
        self.assertTrue(any("validation link is not reciprocal" in error for error in errors), errors)

    def test_accepted_risk_requires_acceptance_evidence(self) -> None:
        text = GOLDEN.read_text(encoding="utf-8").replace("- Status: review_required", "- Status: accepted_by_authority").replace(
            "- Acceptance evidence: none while review is pending", "- Acceptance evidence: none"
        )
        errors = self.validate_text(text)
        self.assertTrue(any("accepted risk requires concrete Acceptance evidence" in error for error in errors), errors)

    def test_sensitive_validation_requires_logging_check(self) -> None:
        text = GOLDEN.read_text(encoding="utf-8").replace(
            "- Sensitive logging check: verify customer values and requested restricted values are absent from logs",
            "- Sensitive logging check: none",
        )
        errors = self.validate_text(text)
        self.assertTrue(any("requires a Sensitive logging check" in error for error in errors), errors)

    def test_legacy_contract_remains_accepted_without_strict_flag(self) -> None:
        legacy = """# Security and Risk Considerations

## Scope
content
## Data Classification and Assets
content
## Threat Actors and Trust Boundaries
content
## Misuse and Abuse Cases
content
## Planned Controls
- Control owner: owner
- Control validation: tests
## Risks and Residual Risk
- Residual risk: low
- Risk authority: security
## Validation Expectations for Magia
content
## Required Review
- Security reviewer: security
- Compliance reviewer: compliance
"""
        with tempfile.TemporaryDirectory(prefix="mago-security-v1-") as tmp:
            path = Path(tmp) / "security-and-risk-considerations.md"
            path.write_text(legacy, encoding="utf-8")
            self.assertEqual(validate(path), [])
            self.assertTrue(any("version 2 is required" in error for error in validate(path, require_v2=True)))


if __name__ == "__main__":
    unittest.main()
