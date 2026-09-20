# Multi-Candidate Execution

Use when the caller evaluates several candidates under one search/evolution run. Harness owns execution isolation/evidence, not survivor selection.

## Required invariants

- same frozen scenario partition/evaluator identity for comparable candidates;
- unique candidate id, candidate identity, run id, work directory, and trace manifest;
- no writable state shared between candidates unless the state is an explicitly frozen read-only input;
- evaluator-only assets remain inaccessible to every candidate for hidden/holdout claims;
- candidate order must not change scoring semantics;
- failures/timeouts are recorded per candidate rather than silently retried under different criteria.

## Holdout

L5 holdout should normally run only for finalists. Revealing holdout-specific feedback for mutation invalidates its unseen status for that lineage and requires a fresh holdout for later blind claims.

Return per-candidate execution evidence to the caller; do not choose the population survivors.
