# PR / Git Workflow v3

Use PR/Git mode for branch conflict, migration-history, or lineage questions.

1. Resolve the repository root and requested base to immutable base SHA, HEAD SHA, and merge-base SHA with replacement refs disabled.
2. Record the working-tree dirty state separately; Git revision identity does not identify uncommitted bytes.
3. Enumerate changed migration/support files from the exact diff and hash analyzed working bytes.
4. Read base/head migration history from immutable Git objects; do not use working-tree content as base evidence.
5. Derive the strongest available migration-set scope: DbContext + migrations assembly when supplied/available, otherwise directory scope.
6. Compare full migration IDs and class identities. A shared timestamp alone is a manual-review signal.
7. When a changed ModelSnapshot contains `LastMigrationId`, compare it against the latest migration observed in that set. Treat absence of that property as lack of that capability, not as divergence.
8. Check snapshot-only or migration-without-snapshot changes as review signals; neither alone proves corruption.
9. Apply structured-operation, destructive/rollback, provider/version, raw-SQL, and artifact-integrity rules against the same frozen input identity.
10. If reviewed/deployment SQL is part of the PR/deployment workflow, bind exact hashes and block identity drift.
11. Report base/head/merge-base, history digests, changed-file identities, limitations, and explicit uncertainty.

### Branch reconciliation guidance

When two branches independently generated migrations from the same ancestor, preserve the intended schema/data changes but regenerate the later migration on top of the reconciled migration tree. Do not treat filename sorting or timestamp editing as proof that the branch history is valid.

### Validation hierarchy

Prefer, when available:

1. frozen static analyzer regressions;
2. exact provider-generated forward/rollback SQL review;
3. `has-pending-model-changes`/semantic evidence for the same provider/context;
4. clean database apply;
5. representative upgraded database apply + data assertions;
6. deployment-topology/concurrency validation when runtime migration behavior matters.

A pass at a lower layer does not imply a pass at a higher layer.
