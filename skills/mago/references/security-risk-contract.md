# Security and Risk Contract

Use contract version 2 for new governed planning whenever authorization, identity, sensitive data, secrets, compliance, fraud, or another material security boundary is triggered. Version 1 remains readable only for legacy compatibility and should be upgraded during `refine` or `adapt` before governed handoff.

## Relational model

Version 2 uses stable records and reciprocal links:

```text
ASSET -> THREAT -> CONTROL -> SECVAL
BOUNDARY -> THREAT
THREAT -> ABUSE -> CONTROL
THREAT + CONTROL -> RISK -> external authority
```

Every threat must identify protected assets and trust boundaries, have at least one control, and be covered by a validation record through that control. Every abuse case must have a control. Every residual risk must cite both threats and controls. Accepted risk requires external authority and concrete acceptance evidence; Mago never accepts risk.

Restricted assets and high- or critical-impact threats require at least one protective control whose failure behavior is `fail_closed`, `deny`, `quarantine`, or `isolate`. Sensitive-data validations require an explicit logging check. Authentication and authorization assumptions belong on the trust-boundary record so reviewers can inspect the actual enforcement crossing.

## Validation

Run:

```bash
python scripts/validate_security_risk.py <package>/security-and-risk-considerations.md --require-v2
```

The validator checks structure, unique identifiers, reference integrity, reciprocal control-validation links, threat/control/validation coverage, protective failure behavior, authority boundaries, risk-acceptance evidence, and sensitive logging expectations. It does not perform threat discovery, prove control effectiveness, or replace security/compliance review.
