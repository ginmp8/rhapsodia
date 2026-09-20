# Multi-Candidate Execution

Use when the caller evaluates several candidates under one search/evolution run. Harness owns execution isolation/evidence, not survivor selection.

## Required invariants

- same frozen scenario partition, evaluator identity, and evaluation-policy identity for comparable candidates;
- unique candidate id, candidate identity, run id, work directory, **trace id**, and trace manifest;
- no writable state shared between candidates unless the state is an explicitly frozen read-only input;
- evaluator-only assets remain inaccessible to every candidate for hidden/holdout claims;
- candidate order must not change scoring semantics;
- failures/timeouts are recorded per candidate rather than silently retried under different criteria.

## Holdout

L5 holdout should normally run only for finalists. Revealing holdout-specific feedback for mutation invalidates its unseen status for that lineage and requires a fresh holdout for later blind claims.

Return per-candidate execution evidence to the caller; do not choose the population survivors.


For search/evolution integration use `assets/templates/multi-candidate-manifest.json.template` contract v2 and validate it with `scripts/validate_multi_candidate_manifest.py`. Legacy v1 remains readable outside evolutionary integration; v2 is required for policy-bound comparable evidence. The interface is declared in `contracts/integration-manifest.json`.
