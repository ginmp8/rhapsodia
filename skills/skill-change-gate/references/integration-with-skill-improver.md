# Integration with Skill Improver

Use this reference when `skill-change-gate` participates in a measured improvement loop. The integration is protocol-based: no runtime dependency on another installed skill is required.

## Role split

| Component | Owns |
|---|---|
| improvement loop | hypothesis selection, baseline/candidate mutation, evaluator freeze, measurement, rollback, final experiment report |
| `skill-change-gate` | structural/semantic acceptance, evidence identity interpretation, protected-path regression classification, portability and delivery integrity |
| benchmark/evaluator | measured score, scenario results, hard evaluator gates, report artifacts |

## Recommended sequence

```text
1. capture/freeze baseline skill identity
2. freeze evaluator, scenarios, expected outputs, and blocked paths
3. measure baseline
4. apply one bounded candidate hypothesis
5. freeze candidate identity before acceptance testing
6. rerun the same frozen evaluator/scenario inputs
7. run skill-change-gate with before/candidate identities and protected paths
8. verify package/delivery receipt points to the frozen candidate when packaging is in scope
9. accept only if metric rule and change gate both pass
10. otherwise reject, revert, repair-before-accept, or explicitly restart the experiment
```


## Self-improvement promotion gate

For `self-improvement`, the gate is still stateless, but it should receive generation provenance from the improvement loop when available:

```text
run_id
generation_id
controller_identity_sha256
baseline_identity_sha256
candidate_identity_sha256
last_known_good_identity_sha256
controller_unchanged
evaluator_unchanged
candidate_frozen
external_validation_surface
promotion_receipt_path_or_identity
```

Additional strict-policy rules:

- `controller_identity_sha256` must differ from the material candidate identity;
- the active controller and frozen evaluator must remain unchanged after freeze;
- the gate decision must be produced outside the candidate mutation surface;
- the candidate cannot authorize its own promotion by altering the gate policy, evaluator, fixtures, thresholds, or receipt;
- a `promote` decision is invalid if the promotion/package receipt identifies bytes different from the gated candidate;
- `last_known_good` must remain recoverable until promotion commits successfully;
- a new generation must not begin merely because the current candidate passed this gate. Promotion/closure belongs to the caller's self-improvement lifecycle.

This integration is deliberately pairwise: the change gate may understand the improvement-loop handoff, but it must not discover or orchestrate unrelated review/improvement specialists.

## Static helper integration

A strict local-filesystem loop can use:

```text
<PYTHON> scripts/static_change_gate.py \
  --target <CANDIDATE> \
  --before <BASELINE> \
  --policy strict \
  --profile portable \
  --expected-before-sha256 <BASELINE_TREE_HASH> \
  --expected-target-sha256 <CANDIDATE_TREE_HASH> \
  --protected-path evals/** \
  --protected-path <OTHER_FROZEN_PATH> \
  --artifact-receipt <PACKAGE_RECEIPT_IF_APPLICABLE> \
  --json <REPORT_OUTSIDE_BOTH_SKILL_ROOTS>
```

Do not refresh expected hashes after a mismatch. A mismatch invalidates the claimed comparison until the caller intentionally re-baselines.

## Acceptance rule

Accept only when all applicable conditions hold:

```text
same frozen evaluator/scenario inputs
and baseline identity matches the frozen baseline
and candidate identity matches the frozen candidate
and protected paths are unchanged
and required benchmark/evaluator gates pass
and configured metric rule is satisfied when improvement is claimed
and package receipt identifies the same frozen candidate when packaging is in scope
and skill-change-gate passes under the selected policy
```

Hold/fail when:

- metric improves but the gate reports a blocking regression;
- gate passes but the metric rule does not satisfy the experiment contract;
- evaluator/source identity drifts;
- protected paths change;
- package receipt points to another candidate;
- required evidence is missing;
- material concerns remain under strict policy.

## Policy defaults

| Caller mode | Change gate policy |
|---|---|
| benchmark-only | not-run unless quality interpretation is requested |
| manual patch | normal |
| automated loop | strict |
| self-improvement | strict |
| package install/update | normal or strict based on destination risk |

## Machine-readable handoff fields

A caller should preserve at least:

```text
quality_gate.status
quality_gate.policy
quality_gate.before_tree_sha256
quality_gate.target_tree_sha256
quality_gate.protected_path_changes
quality_gate.blocking_regressions
quality_gate.material_concerns
quality_gate.portability_profile
quality_gate.artifact_receipt_correspondence
quality_gate.generation_id
quality_gate.controller_identity_sha256
quality_gate.candidate_identity_sha256
quality_gate.external_validation_surface
quality_gate.promotion_receipt_correspondence
```

## Non-goals

Do not let the change gate select hypotheses, tune benchmark weights, edit evaluator fixtures, repair the candidate, or claim measured improvement. It decides whether the already-measured candidate remains acceptable.
