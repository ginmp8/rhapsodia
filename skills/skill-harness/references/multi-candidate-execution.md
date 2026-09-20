# Multi-Candidate Execution

Use when the caller evaluates several candidates under one search/evolution run. Harness owns execution isolation/evidence, not survivor selection.

## Required invariants

- same frozen scenario partition, evaluator identity, and evaluation-policy identity for comparable candidates;
- unique candidate id, candidate identity, run id, work directory, **trace id**, trace-manifest id, and trace-manifest content identity/hash;
- no writable state shared between candidates unless the state is an explicitly frozen read-only input;
- evaluator-only assets remain inaccessible to every candidate for hidden/holdout claims;
- candidate order must not change scoring semantics;
- failures/timeouts are recorded per candidate rather than silently retried under different criteria.

## Holdout

L5 holdout should normally run only for finalists. Revealing holdout-specific feedback for mutation invalidates its unseen status for that lineage and requires a fresh holdout for later blind claims.

The current v4 manifest is intentionally one execution row per distinct candidate: `candidate_id` and `candidate_identity` are unique. Do not encode repeated measurements by duplicating a candidate row under v4; use `skill-opt.harness-multi-candidate-evidence-strict` v2 when repeated executions of the same candidate are required, rather than weakening the base invariant.

Return per-candidate execution evidence to the caller; do not choose the population survivors.


For search/evolution integration use `assets/templates/multi-candidate-manifest.json.template` contract v4 and validate it with `scripts/validate_multi_candidate_manifest.py`. Legacy v1/v2/v3 evidence remains readable outside the current evolutionary bridge; v4 is required for policy-bound evidence with unique candidate identity and canonical `sha256:<64hex>` trace-manifest identity. The interface is declared in `contracts/integration-manifest.json`.
