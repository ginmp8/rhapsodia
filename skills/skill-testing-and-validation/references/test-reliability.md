# Test reliability and stability

Use this reference when repeated execution, flakiness, hermeticity, ordering, concurrency, time, randomness, network state, or mutable external inputs can affect a gate.

## Separate gate outcome from reliability

A gate receipt answers whether one execution was `pass`, `fail`, `blocked`, or `not-run`. Reliability is an orthogonal property of repeated comparable executions.

Use only these stability states:

- `stable`: comparable attempts agree on the material outcome;
- `unstable`: comparable attempts disagree, including pass/fail alternation;
- `inconclusive`: a material blocker, target mutation, or incomparable evidence prevents a stability conclusion;
- `not-assessed`: stability was not requested or attempts were not executed.

Never convert an unstable gate into `pass` by retrying until one attempt succeeds. Retries are diagnostic evidence, not an acceptance policy.

## When stability assessment is material

Assess stability when at least one applies:

- the same gate has produced inconsistent results;
- failure evidence suggests order, concurrency, timing, random seed, cache, network, or external-state sensitivity;
- the user explicitly requires flake/reliability evidence;
- a release-critical acceptance decision depends on a gate already suspected to be flaky;
- a repair claims to remove an observed flake.

Do not impose repeated execution on every gate. A deterministic parser/unit validator with no observed variance does not need an ornamental retry budget.

## Bounded assessment

Use an explicit attempt budget; do not hide a retry default:

```text
<PYTHON> scripts/assess_stability.py --target <TARGET> --gate <GATE> --runs <N> --execute --receipt <RECEIPT.json>
```

The helper executes the same selected command and records every attempt. It does not stop on the first pass.

Interpret required reliability as an acceptance overlay:

- `stable` + all attempts `pass` -> reliability condition may pass;
- `unstable` -> required reliability fails;
- `inconclusive` -> required reliability is blocked;
- `not-assessed` -> required reliability is not-run.

This overlay does not add a new gate state or failure category.

## Hermeticity checklist

Before calling two attempts comparable, account for material implicit inputs when relevant:

- clock/date/timezone;
- locale/encoding;
- random seed and hash seed;
- test order and shared mutable state;
- concurrency/scheduling;
- caches and generated runtime files;
- network/API/service state;
- external filesystem paths;
- dependency/runtime/tool versions;
- credentials/permissions when required to execute;
- CI-specific execution context.

`scripts/environment_fingerprint.py` records only a safe subset of material context. Never serialize arbitrary environment variables into evidence.

## Candidate identity

`scripts/run_gate.py` records the material target identity before and after a gate. Runtime caches such as `__pycache__` and `.pyc` are excluded from material identity, but source/configuration changes are not.

A read-only gate that changes material target bytes invalidates that receipt as final acceptance evidence unless the mutation was explicitly expected, separately authorized, and re-baselined.
