# Capability Preservation and Parent Provenance

Use when the caller supplies a capability map, transformation record, direct-parent identity, or when before/after attribution is material.

## Capability preservation

For each affected capability classify:

- `preserved`;
- `added`;
- `regressed`;
- `removed-authorized`;
- `removed-breaking`;
- `unproven`.

A missing/renamed file is not automatically capability loss; trace semantic owner, consumers, replacement behavior, and validators. Under strict policy, `regressed` or `removed-breaking` is blocking. `unproven` means insufficient evidence when acceptance depends on that capability.

## Differential regression status

Keep capability state separate from regression attribution. For each material finding also classify the candidate delta:

- `introduced` — absent in the relevant baseline/parent and created by this candidate;
- `worsened` — existed but became materially worse;
- `preexisting-unchanged` — inherited debt not worsened by this candidate;
- `improved` — inherited issue became materially better but remains;
- `resolved` — inherited issue is removed;
- `unknown` — evidence cannot establish attribution.

Do not make unrelated cleanup a condition for candidate acceptance merely because debt exists in the baseline. A policy may still forbid promotion when pre-existing critical debt exists, but report that as policy state rather than a candidate-introduced regression.

## Rule origin

When a finding is decision-relevant, state the authority behind the rule: Agent Skills specification, portable package policy, security policy, experiment policy, delivery-integrity policy, or another explicit source. This prevents local conventions from being misrepresented as specification mandates.

## Parent provenance

Keep direct parent and stable baseline distinct:

- `parent`: direct ancestor of this transformation;
- `baseline`: stable regression reference;
- `candidate`: frozen proposed state.

Use parent evidence to attribute the local transformation. Use baseline evidence to detect cumulative drift. Identity mismatch is blocking for strict measured claims.

## Transformation provenance

Gate actual candidate bytes, not stated intent. A `repair` can pass without positive metric delta if the confirmed defect is removed without regression. An `optimization` claim needs comparable metric evidence. An `experiment` remains an experiment until evidence supports promotion.
