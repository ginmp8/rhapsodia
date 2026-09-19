# Run State and Recovery

Use a machine-readable run state for resumable, multi-step, governed, multi-repository, or interruption-prone execution. The state is execution evidence, not a substitute for repository truth.

## Contract

A run state records:

- schema version and run identity;
- source mode and execution profile;
- repository root, selected scope, task, and allowed writes;
- inspected files and their fingerprints;
- planned and completed writes;
- commands with pass, fail, or not-run results;
- current checkpoint and pending step;
- status: active, cancelled, retry_pending, rollback_pending, rolled_back, handed_off, blocked, or closed;
- retry count, cancellation reason, rollback evidence, and handoff state;
- creation and update timestamps.

Use `scripts/run_state.py` to create and transition the contract. Use `assets/templates/run-state.json.template` as the field reference.

## Fingerprints and Drift

Fingerprint every inspected or frozen source file that supports the next action. A fingerprint includes existence, size, and SHA-256 content digest. Before resume:

1. resolve the stored repository root;
2. recompute every tracked fingerprint;
3. compare existence and digest;
4. stop with `repository_drift` when any tracked file changed, appeared, or disappeared;
5. re-inspect and create a new checkpoint or run before continuing.

Never resume blindly after branch changes, dependency changes, generated-code changes, migrations, or external contract updates. Directory names alone are not sufficient evidence; track the concrete files relied upon.

## Checkpoints

Create a checkpoint after a meaningful, independently reviewable transition:

- scope and profile resolved;
- reproduction or baseline captured;
- bounded patch applied;
- targeted validation completed;
- repository-level boundary completed;
- convergence evaluated;
- rollback completed;
- handoff prepared;
- closure completed.

A checkpoint must identify the next pending step. Do not use a checkpoint to imply a successful command that was not executed.

## Cancellation

Cancellation stops new mutation. Preserve accepted completed writes and evidence, set status to `cancelled`, record the reason, and report whether rollback is required. Cancellation is not completion.

## Retry

Retry only the failed or blocked step when inputs and fingerprints still match. Increment retry count and retain the earlier failed result. Do not overwrite failure history. If the failure class or source assumptions changed, re-inspect instead of retrying.

## Rollback

Rollback must identify:

- files, migrations, repositories, or operations reverted;
- command or manual evidence;
- pass, fail, or not-run status;
- remaining side effects;
- whether a forward fix is safer than reversal.

Set `rollback_pending` before reversal and `rolled_back` only after evidence exists. A rollback failure is a separate stop category and cannot be hidden by returning the run to active.

## Handoff

Set `handed_off` when execution cannot continue within MAGIA authority. Record destination owner category, evidence path or summary, exact planning/governance gap, and the safe state of completed writes. Do not rewrite product intent to avoid a handoff.

## Close

Close only after validation and convergence have current evidence. Closed state includes final checkpoint, no pending mutation step, command outcomes, changed-file mapping, and residual risks. A closed run can be inspected but not resumed; create a new run for follow-up work.
