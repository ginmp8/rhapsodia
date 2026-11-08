# Validation and Remote Delivery

## At a Glance

- **Purpose:** Define evidence needed before a locally reconciled tree is considered suitable for publication, and a safe remote handoff.
- **Load when:** A candidate is ready, local apply is authorized, PR/branch synchronization needs a push, or release/CI acceptance is requested.
- **Decision impact:** Preserves single-parent history and compare-and-swap freshness while separating structural checks from tested functionality and publication.

## Evidence and checks

1. **Freeze identities:** repo, source ref and SHA, target branch and old SHA, unique common base, candidate tree, and any approved resolution manifest. `git merge-base --all` with multiple bases blocks unless one reviewed common ancestor is explicitly selected.
2. **Inspect content:** check the complete path/mode inventory from the plan. Spot-check `both_changed` files at function/hunk level. Check the resulting diff for markers, lost registration, orphaned tests, documentation mismatches, migrations, binary assets and transitive caller changes. The helper enforces exact preservation of source-only/target-only paths but cannot infer semantic parity inside a concurrently changed file.
3. **Validate behavior:** run tests covering source features, destination-only features and their intersections, including error/security/retry paths when applicable. Record command, environment, candidate tree or SHA, exit/result, and scope. Build/lint/test checks should be specified by the project owner; the helper never executes arbitrary repository code.
4. **Apply locally:** with explicit authorization, run the helper against the frozen plan. It creates one commit with `parent = old target SHA` using `git commit-tree`; then moves the local destination ref using `git update-ref <ref> <new> <old>`. The source ref and checked-out worktree remain unchanged. A failed CAS is a stop; re-plan instead of retrying blindly.
5. **Push only if separately authorized:** first resolve the expected remote destination SHA. A normal `git push <remote> <new-commit-sha>:refs/heads/<destination>` is **non-force**; reject non-fast-forward/stale remote changes and never add `--force`. Re-read remote SHA afterward and verify the exact new commit. Do not assume a local ref update equals a published branch.
6. **Check CI on the final SHA:** inspect workflow and job outcomes (success, fail, skipped, pending, cancelled) and required checks; do not infer passing from green unrelated SHAs. Native UI, platform installers and user-data migrations need specific tests or remain `unverified`.

## Output classification

- `ready`: a conflict-free candidate tree exists and preservation invariants pass; no ref updated yet.
- `conflicts`: Git found unresolved paths; no candidate may be applied until explicit resolutions are supplied and validated.
- `no_change`: candidate equals the current destination tree; do not publish an empty commit.
- `applied`: verified single-parent commit and CAS local ref update; `remote_pushed: false` is intentional.
- `blocked`: one or more identity, trust, safety, conflict, scope or validation requirements could not be satisfied. Preserve all refs.
- `verified`: a separately supported characterization of specific tests, CI and post-push tree checks, never a blanket synonym for runtime equivalence.

## Handoff record

Include at minimum: repository and branch names; source, target, base and new commit SHAs; exact source/destination blob counts; source-only, destination-only, concurrent and conflict-path counts; path and mode exceptions; separate source/destination acceptance tests with outcomes; commit parent SHA; expected/observed remote head; CI URL and final job outcomes; outstanding cross-platform, concurrency or semantic risks. Never claim the original source commits were replayed, because this operation integrates their **content**, not their identities.
