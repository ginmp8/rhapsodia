# Self-Improvement Protocol

Use this protocol only when the skill being improved is also the workflow/controller performing the improvement. This is a self-hosting safety contract, not a general specialist-orchestration layer.

## Ownership boundary

The improvement workflow owns the generation lifecycle: controller identity, baseline snapshot, isolated candidate, bounded mutation, evaluator freeze, accept/reject state, rollback, final freeze, and promotion receipt.

It does **not** own broad specialist selection. External evidence providers may be supplied by a caller/orchestrator, but this protocol consumes their evidence contracts rather than discovering or dispatching an ecosystem of reviewers.

## Generation model

Use these roles explicitly:

- `controller`: the immutable version executing the current self-improvement generation;
- `baseline`: immutable snapshot of the target state being improved; normally equivalent in content to the controller at generation start, but recorded separately because execution identity and comparison identity are different roles;
- `candidate`: isolated mutated copy produced by the controller;
- `promoted`: candidate accepted by external/frozen gates and made eligible to become the controller of a later, separate generation;
- `last_known_good`: most recent promoted controller preserved for rollback.

Never mutate the active controller in place. `controller_identity` and `candidate_identity` must differ for a material candidate. The controller tree and frozen evaluator assets are read-only during the generation.

## Required generation identity

Record before mutation:

```text
run_id
generation_id
controller_identity
baseline_identity
candidate_work_path
evaluator_identity
protected_paths
max_self_recursion_depth
last_known_good_identity
```

Default `max_self_recursion_depth = 1`: a controller may produce one candidate generation, but that candidate must not recursively start another self-improvement generation before promotion and closure of the current run.

## Required sequence

1. freeze `controller_identity` and preserve `last_known_good`;
2. create an immutable `baseline` snapshot and isolated candidate work copy;
3. freeze evaluator/scenario/expected-output identities outside the candidate mutation surface;
4. select one bounded hypothesis and predeclare acceptance/rollback rules;
5. mutate only the candidate copy;
6. freeze `candidate_identity` after the final candidate edit;
7. evaluate baseline and candidate under the same frozen evaluator contract;
8. run the configured independent change/quality gate outside the candidate mutation surface;
9. accept or reject the candidate; rejected candidates never replace `last_known_good`;
10. on accept, emit a promotion receipt tied to exact candidate bytes;
11. promote atomically when installation/replacement is in scope;
12. only a later run may use the promoted version as a new controller.

## Promotion rules

A candidate is promotion-eligible only when:

- controller/baseline/candidate identities are recorded;
- controller and evaluator remained unchanged;
- candidate was evaluated from its frozen final identity;
- required metric/evaluator rules pass;
- required change gate passes;
- protected paths are unchanged;
- no unresolved strict-policy blocker exists;
- package/install receipt, when applicable, points to the same candidate identity;
- rollback/last-known-good evidence exists.

The candidate cannot authorize its own promotion by editing the acceptance policy, evaluator, thresholds, fixtures, or gate evidence.

## Bootstrap conformance

After acceptance, a self-improving skill may be checked for **bootstrap conformance**: verify that the promoted candidate still contains the required self-improvement protocol, validators, protected-path rules, and stop conditions. This check must not automatically start generation `N+2`.

If an actual next-generation experiment is requested, close generation `N+1`, promote it, freeze its new controller identity, and start a separate run.

## Machine-readable receipt

Use a receipt shaped like:

```json
{
  "schema_version": 1,
  "run_id": "...",
  "generation_id": "...",
  "controller_identity_sha256": "...",
  "baseline_identity_sha256": "...",
  "candidate_identity_sha256": "...",
  "evaluator_identity_sha256": "...",
  "last_known_good_identity_sha256": "...",
  "max_self_recursion_depth": 1,
  "controller_unchanged": true,
  "evaluator_unchanged": true,
  "candidate_frozen": true,
  "external_validation_surface": true,
  "gate_status": "pass",
  "decision": "promote",
  "promoted_identity_sha256": "..."
}
```

Validate it with `scripts/validate_self_improvement_receipt.py` when execution is available.

## Stop conditions

Stop or reject the generation when:

- controller and candidate are the same mutable tree;
- controller/evaluator identity changes after freeze;
- the candidate can read or modify evaluator-only acceptance assets in a way that invalidates the declared evaluation;
- recursion depth exceeds the declared limit;
- the candidate attempts to promote itself before external/frozen validation completes;
- rollback/last-known-good identity is unavailable for a mutating promotion;
- the promotion receipt does not bind to the exact frozen candidate;
- the only route to promotion is weakening the evaluator, threshold, safety, compatibility, or evidence contract.
