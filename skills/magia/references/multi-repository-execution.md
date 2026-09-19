# Safe Multi-Repository Execution

Multi-repository work is a governed profile. Repository checkpoints coordinate evidence; they do not provide distributed atomicity.

## Required Plan Before Mutation

Record:

- repositories and exact writable scopes;
- dependency and deployment order;
- producer/consumer or schema compatibility direction;
- expand-contract or equivalent compatibility window;
- repository-level success checks;
- rollback or forward-fix per repository;
- cross-repository smoke/contract evidence;
- stop conditions for partial failure.

## Sequence

1. Inspect every affected repository and freeze relevant contracts.
2. Choose a dependency-safe order. Prefer backward-compatible producers/servers before consumers when evidence supports it.
3. Establish compatibility windows before breaking removals.
4. Apply one repository batch and validate it before advancing.
5. Record the repository checkpoint and current cross-repository state.
6. Stop on an incompatible or unverified boundary; do not continue to make the partial state look complete.
7. Run cross-repository checks and convergence before closure.

## Partial Failure

When one repository fails:

- preserve evidence from completed repositories;
- identify whether the current state is compatible, degraded, or unsafe;
- do not claim atomic completion;
- roll back only where the rollback is safe and verified;
- prefer a bounded forward fix when rollback would break already-deployed compatibility;
- hand off planning or governance changes when sequencing or accepted risk must change.

## Stop Conditions

Stop when:

- no compatible intermediate state exists;
- a required repository is unavailable or outside writable scope;
- rollback cannot restore compatibility and no bounded forward fix exists;
- contract ownership or release sequencing must change;
- cross-repository validation cannot distinguish safe partial completion from failure;
- credentials, production access, or destructive operations exceed the authorized scope.

## Closure Evidence

Governed closure includes repository order, commit or file scope when known, checks per repository, compatibility status, cross-repository checks, rollback state, partial-failure handling, and residual deployment assumptions. Never describe the sequence as distributed atomicity unless an actual transaction mechanism provides it and current evidence proves its use.
