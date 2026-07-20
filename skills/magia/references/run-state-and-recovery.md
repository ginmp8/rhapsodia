# Run State, Recovery, and Multi-Repository Execution

Load for multi-step, interruptible, automated, governed, or multi-repository work. Run-state controls execution and is the machine summary; it does not replace required human implementation/validation records.

## Contract

Schema `1` requires:

- identity/control: `run_id`, `profile`, internal `mode`, `status`, `checkpoint`, `pending_step`, bounded `scope`;
- evidence/writes: fingerprinted repository-relative `inspected_files`, `planned_writes`, `completed_writes`, and commands with `pass|fail|not_run`;
- outcome/recovery: `validation_status`, `convergence_status`, `retry`, `cancellation`, `rollback_evidence`, `handoff`;
- repositories: dependency order, checkpoint/status, compatibility window, rollback state, and `atomicity: not_guaranteed` for more than one repository.

Locations: ADHOC `.magia/run-state/<run_id>.json`; RALPH `{BOARD_ROOT}/specs/<spec_id>/.magia/run-state.json`; multi-repo uses one explicit coordinator state with per-repo entries. Never imply a distributed transaction.

Validate before resume/close:

```bash
python scripts/validate_run_state.py --state <file> --repo-root <root> --verify-drift --json
```

## Transitions

Checkpoints are `inspect|execute|validate|converge|close`; statuses are `pending|in_progress|paused|cancelled|blocked|failed|completed|rolled_back|handoff`.

- Resume `paused|blocked|failed|in_progress` only after rechecking scope, file hashes, dependencies, and pending step.
- Any source/dependency drift stops with `repository_drift`; inspect again, restart safely, or hand off.
- `completed` requires `close`, null pending step, validation `pass`, convergence `satisfied`, no failed repo, and no cancellation request.
- Cancellation preserves writes/evidence; retry is bounded and records the prior category; repeated failure without new evidence stops.
- Rollback records action, affected scope, result, and residual state; rollback failure is a separate blocker.

## Multi-Repository Protocol

1. Record dependency order and compatibility windows before writes.
2. Checkpoint and validate each repository before dependents.
3. Prefer expand-contract: add compatible behavior, migrate, then remove old behavior.
4. On partial failure, stop dependents, preserve compatible successes, assess rollback per repo, and report residual topology.
5. Keep `atomicity: not_guaranteed` unless a real external transaction/orchestrator proves otherwise.
6. Stop when compatibility/rollback cannot preserve a supported state or ordering would change planning intent.

## Failure Taxonomy

- `input_blocker`: locate/request concrete input; no unbounded mutation.
- `repository_drift`: stop resume, refresh context/fingerprints, restart safely.
- `reproducibility_failure`: gather evidence; do not patch a guessed cause.
- `implementation_failure`: repair the bounded patch or roll back.
- `test_failure`: diagnose, repair, or revert; never complete.
- `environment_failure`: retry only with transient evidence; otherwise block/record `not_run`.
- `dependency_failure`: isolate/fallback only within intent; otherwise hand off.
- `contract_conflict`: stop incompatible rollout; hand material change to Mago.
- `planning_gap`: technical-gap handoff to Mago; do not rewrite intent.
- `governance_gap`: hand owner/date/status/risk acceptance to nomia.
- `security_stop`: stop exposure, redact, preserve evidence, recommend containment/rotation.
- `rollback_failure`: freeze rollout and report residual state/operator action.

Every failure records category, evidence, repair/retry/rollback decision, next safe checkpoint, and handoff target.
