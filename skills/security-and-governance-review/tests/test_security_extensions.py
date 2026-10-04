from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_security_extensions import validate

class ExtensionValidationTests(unittest.TestCase):
    def test_valid_extensions_pass(self):
        report={
          "control_evidence":{"controls":[{"id":"c1","effectiveness":"runtime-observed","evidence_refs":[{"layer":"runtime","source_identity":"run:1"}]}]},
          "agent_inventory":{"components":[{"id":"m1","kind":"model","identity":{"version":"v1"}}]},
          "authority_boundaries":{"records":[{"actor":"agent","action":"deploy","resource_scope":"prod","authorization_source":"policy","approval":"human","audit_receipt":"required","failure_behavior":"fail-closed","rollback_containment":"rollback"}]},
          "framework_mappings":[{"framework":"OWASP Agentic Top 10","source_locator":"https://example.invalid","source_version_or_date":"2026","mapping_type":"coverage","claim_level":"mapped-only"}],
          "compliance_context":{"conclusion":"needs-verification"}}
        self.assertEqual([],validate(report))
    def test_behavioral_level_requires_behavioral_evidence(self):
        e=validate({"control_evidence":{"controls":[{"id":"c1","effectiveness":"behaviorally-demonstrated","evidence_refs":[{"layer":"structural","source_identity":"file:1"}]}]}})
        self.assertTrue(any("behavioral evidence" in x for x in e))
    def test_runtime_level_requires_runtime_evidence(self):
        e=validate({"control_evidence":{"controls":[{"id":"c1","effectiveness":"runtime-observed","evidence_refs":[{"layer":"behavioral","source_identity":"test:1"}]}]}})
        self.assertTrue(any("runtime evidence" in x for x in e))
    def test_strong_compliance_requires_context(self):
        e=validate({"compliance_context":{"conclusion":"compliant","jurisdiction":"EU"}})
        self.assertTrue(any("actor_role" in x for x in e))
    def test_mapping_cannot_override_sgr(self):
        e=validate({"framework_mappings":[{"framework":"x","source_locator":"u","source_version_or_date":"v","mapping_type":"coverage","claim_level":"mapped-only","severity_override":"critical"}]})
        self.assertTrue(any("must not override" in x for x in e))
    def test_inventory_requires_identity(self):
        e=validate({"agent_inventory":{"components":[{"id":"t1","kind":"tool","identity":{}}]}})
        self.assertTrue(any("requires identity" in x for x in e))
if __name__=="__main__": unittest.main()
