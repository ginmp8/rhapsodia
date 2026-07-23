# Ecosystem Handoff Contract v3

Applies to every Nomia/Mago/Magia transfer. [ecosystem-handoff-contract.json](ecosystem-handoff-contract.json) is canonical. Packages keep byte-equivalent local copies, never read peers at runtime, and transfer evidence rather than authority. Direction payloads are closed.

## Compatibility

Release `1.9.1`; envelope `3.0.0`; mapping `2.0.0`; exact versions only. Legacy aliases and envelopes are rejected; adaptation must occur before a handoff is built. There is no runtime compatibility switch for pre-v3 envelopes.

## Envelope

Require identity, direction, versions, provenance, freshness, payload, unknowns, conflicts, deterministic `handoff_id`, stable `workflow_id`, and `privacy_handling`; follow-ups reuse the workflow and set `causation_id`.

Privacy covers classification, data categories, redactions, audience, destinations, purpose, retention, reference visibility, and external sharing. Validate declarations against all text-bearing envelope fields. Reject secrets, private locations, contradictory identifiers, and sensitive public output with masked reasons. Durable artifacts inherit [artifact privacy](artifact-privacy-contract.json); external projection fails closed.

## Directions

- `nomia_to_mago`: governance/readiness, no technical plan.
- `mago_to_magia`: validated execution intent, no governance/runtime claim.
- `magia_to_mago`: execution evidence/deviation, no planning rewrite.
- `mago_to_nomia`: planning projection, no governance decision.
- `magia_to_nomia`: execution projection, no closure/risk acceptance.

## Validation

Malformed, stale, future, conflicting, wrong-role, mixed-version, lineage/privacy-invalid, tampered, undeclared, or authority-violating envelopes fail closed. Drafts are inspection-only with `--allow-draft`. Use `scripts/ecosystem_handoff.py`; the ledger stores transport state only.
