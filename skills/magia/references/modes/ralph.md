# RALPH Mode

Use RALPH when Magia executes one selected task or an explicit dependency-safe batch from a validated Mago planning contract. `artifact-native` is the default profile: no Board, cycle, shared registry, or peer runtime import is required. Board mechanics below are compatibility-only and activate only when `legacy-board` is explicitly selected.

## Canonical Rules

- Require a validated planning handoff with stable work-item/spec/task identity, repository scope, objective/acceptance reference, planned proof/expected result, dependencies, and current source bindings.
- Treat Mago/Nomia artifacts as read-only; Magia owns repository implementation plus owner-local execution state/evidence.
- Bind execution proof to current candidate bytes and planning hashes; historical dependency receipts prove prior task completion, not today's candidate.
- Execute one selected task by default or an explicitly dependency-safe batch; never invent, rewrite, split, or resequence planning tasks.
- Close only from current passing evidence plus required external verifier/checkpoint gates; local self-validation never grants governance/release completion.
- Use `legacy-board` only when the request explicitly targets an existing Board or its migration/maintenance.

## Roots

Native RALPH resolves the repository root, the read-only Mago planning directory referenced by the handoff, and Magia's owner-local execution root (default `docs/implementation/<work_item_id>/` unless an authorized alternate is supplied). Candidate roots must not overlap canonical artifact roots. See `references/artifact-native.md` for exact identity/publication rules.

For explicit `legacy-board`, resolve `BOARD_ROOT`, selected spec package, registry entry, and related identities through `references/canonical-paths.md` and `references/board-contract.md`; those paths never become native defaults.

## Planning-Origin Handoff

Load `references/planning-handoff.md` when the task came from planning, roadmap, discovery, governance, migration, or another Mago-owned package. Treat the validated handoff as executable input. Do not treat implementation requirement, planning provenance, roadmap provenance, governance provenance, or a non-executed planning state as a blocker. Block only for concrete missing/contradictory execution evidence, unsafe paths, unavailable dependencies/services, absent truthful proof, or a required planning/governance change.

## Workflow

1. Validate the `mago_to_magia` handoff and resolve repository, planning, task, dependency, candidate, and Magia artifact identities.
2. Confirm the selected task resolves to current objective/acceptance intent and a planned validation action with expected result.
3. Inspect current repository state and relevant tests/contracts before mutation.
4. Execute only the selected task or declared dependency-safe batch; make the smallest sufficient change.
5. Run explicitly reviewed bounded checks with finite timeouts and capture real exit codes/output hashes; command authority comes from the approved execution task, not a catalog entry.
6. Record Magia-owned implementation/validation evidence and publish sidecars/actions only after semantic validation.
7. Validate current candidate/planning bindings before close; stale candidate or planning bytes require renewed evidence.
8. Return `magia_to_mago` for planning reconciliation needs and `magia_to_nomia` only as execution evidence with delivery impact; never close planning/governance from Magia.

For native command details use `references/artifact-native.md`. For explicit `legacy-board`, use the retained Board scripts/contracts; do not mix native closure with Board state mutation.

## Task Selection

Select only tasks present in the validated planning contract. Require stable task identity, satisfied dependencies, current intent/acceptance linkage, and a credible planned proof. Prefer the next dependency-ready task or an already-authorized parallel/independent task; do not create or rewrite ordering metadata.

In `legacy-board` only, `scripts/validate_execution_readiness.py <board_root> --spec-id <spec_id> --task-id <taskNNN>` remains the readiness check. Board task/manifest/registry reconciliation stays governed by the retained Board contracts and state scripts.

Do not treat implementation requirement, planning provenance, roadmap provenance, governance provenance, or `phase: define` as blocker.

## Blockers

Return BLOCKED only for concrete execution blockers: missing targets or source-bound task identity, unresolved dependencies, unavailable credentials/services, contradictory source-of-truth, unsafe secret access/path, missing truthful validation path, stale/mismatched candidate or planning bindings, or required changes to product intent/task definitions/order/architecture/public contract/data-security/user behavior. Preserve completed partial evidence and hand off rather than broadening authority.

## Batch Execution

When a batch is explicitly authorized, execute only dependency-safe tasks within that batch. Validate each task at the narrowest supported boundary before continuing; stop early on a blocking failure. Preserve per-task evidence and dependency receipts. A batch must not weaken ordering, validation, or checkpoint requirements.

## Unattended Loop Protocol

Do not ask for next actions when a selected executable task exists and the caller explicitly delegated unattended execution. Do not recursively invoke Magia/Mago/Nomia or create substitute completion markers. Continue only while scope, authority, state, and proof remain bounded and verifiable; stop on authority drift, stale evidence, concrete blockers, or failed required gates. Let the parent orchestrator own commit/push/retry/timeout/task-selection responsibilities when assigned there.

## Legacy-board compatibility

When `legacy-board` is explicitly selected, preserve the retained Board behavior: validate `BOARD_ROOT`; read the selected registry/spec package; keep PRD/design/notes/validation plan read-only; write execution truth to `implementation-notes.md` and `validation-evidence.md`; toggle only existing truthful task checkboxes; use `write_execution_log.py`, `close_execution_state.py` (or documented fallback sync/validate scripts), heal only evidence-proven narrow drift, and run `validate_repo_board.py` before closure when local Board files exist. Board manifests/registry move to execution/done states only when their existing contracts and current evidence permit it. Never apply these storage mechanics to native RALPH.
