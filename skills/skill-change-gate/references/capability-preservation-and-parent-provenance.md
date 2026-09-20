# Capability Preservation and Parent Provenance

Use when the caller supplies a capability map, transformation record, or direct-parent identity.

## Capability preservation

Map touched candidate surfaces to capability ids when available. For each affected capability classify:

- preserved;
- added;
- regressed;
- removed-authorized;
- removed-breaking;
- unproven.

A missing/renamed file is not automatically capability loss; trace owner/consumer/validator evidence. Under strict policy, `regressed` or `removed-breaking` is blocking. `unproven` is insufficient evidence when that capability is required for acceptance.

## Parent provenance

Keep direct parent and stable baseline distinct:

- `parent`: direct ancestor of this candidate/transformation;
- `baseline`: stable regression reference;
- `candidate`: frozen proposed state.

Use parent evidence to attribute the local transformation. Use baseline evidence to prevent cumulative drift. Identity mismatch is blocking for strict experiment claims.

## Transformation provenance

When supplied, record transformation ids and change intent. Gate the actual resulting candidate, not the stated intent. A `repair` may pass without a positive metric delta if the confirmed defect is removed and no regression appears. An `optimization` claim needs comparable metric evidence. An `experiment` remains an experiment until evidence supports promotion.
