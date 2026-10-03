# Migration is owned by producers

Workspace does not read legacy Board records as authoritative envelopes and never moves their files. Each Mags package supplies `scripts/migrate_artifacts.py` with read-only `plan`, explicit `apply`, `recovery-plan`, and approved `recover` operations.

Migration copies only recognized files owned by that producer. The original Board is unchanged. The plan lists excluded unknown/non-owned files. Source hashes and conflicts are rechecked before any write; replay is idempotent. Migrated state is `unknown` until its owner revalidates the actual domain evidence. No historical duration, finished task, release, or ownership is inferred.

After all owners have applied the intended plans and validated the migrated content, Workspace indexes their sidecars exactly like native artifacts. Keeping the original Board for audit/rollback is a deliberate compatibility policy, not a required runtime dependency. It can be removed from a disposable test copy without breaking indexing.

An interrupted copy records only new target files in the producer's journal. Recovery requires the expected journal hash, a dead/released writer lock, and unchanged hashes of every rollback target. A committed receipt finalizes rather than rolls back completed copies. Original files are never rollback targets.
