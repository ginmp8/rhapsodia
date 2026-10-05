# Waiver Policy

## At a Glance

- **Purpose:** Distinguish an authorized, bounded risk acceptance from an attempt to hide or bypass failed evidence.
- **Load when:** A material finding may be accepted under policy instead of repaired before acceptance.
- **Decision impact:** A waiver is valid only when candidate/policy/finding/authority-bound; identity drift, protected-evaluator mutation, receipt mismatch, unsafe path/secret exposure, fabricated evidence, contaminated holdout claims, and candidate self-authorization remain non-waivable failures.

## Required waiver fields

Use Gate Context v1. A waiver must identify:

- stable waiver id;
- exact candidate tree;
- exact policy digest;
- explicit finding codes;
- authorizer identity or authority reference;
- rationale and accepted risk;
- single-use intent;
- optional expiry metadata.

The deterministic validator verifies subject/policy correspondence and non-waivable classes. Expiry-time evaluation is environment/time dependent and remains a semantic/current-state check; do not fake deterministic time inside the portable validator.

## Non-waivable classes

Do not waive:

- frozen baseline/candidate identity mismatch;
- protected evaluator/fixture mutation in a measured experiment;
- artifact/promotion receipt pointing to different candidate bytes;
- path traversal or output alias that can mutate protected/input evidence;
- included secrets/credentials or unsafe sensitive exposure;
- fabricated, hidden, or failed required evidence;
- candidate self-authorization by changing its deciding policy/evaluator/gate;
- invalid holdout claims where the deciding holdout was exposed to candidate construction/selection.

If one of these classes is legitimate to change, invalidate/restart the experiment or change the declared workflow; do not waive the contradiction.

## Waivable material concerns

A caller may explicitly accept bounded material concerns such as optional host-adapter degradation, temporary documentation debt, or a known compatibility limitation when the claim is correspondingly scoped and no non-waivable invariant is violated.

Under `strict`, an unresolved material concern needs a valid waiver or the decision fails. Under `normal`, a valid waiver is recorded but should not erase the original finding from the audit trail.
