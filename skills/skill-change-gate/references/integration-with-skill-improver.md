# Integration with Skill Improver

Use when `skill-change-gate` participates in a measured improvement loop. Integration is protocol-based; no runtime dependency on another installed skill is required.

## Role split

| Component | Owns |
|---|---|
| improvement loop | hypothesis selection, baseline/candidate mutation, evaluator freeze, measurement, rollback, final experiment report |
| `skill-change-gate` | candidate acceptance, evidence/context integrity, protected-path/authority/portability/compatibility/delivery classification |
| benchmark/evaluator | metric/scenario results and evaluator-specific hard gates |

## Recommended sequence

```text
1. freeze baseline/direct-parent identity
2. freeze deciding evaluator/scenarios/fixtures/policy inputs
3. record evaluator role/exposure and caller-declared evaluation contract
4. measure baseline where comparison is required
5. apply one bounded candidate transformation
6. freeze candidate identity
7. evaluate with the same frozen deciding inputs
8. create/validate Gate Context when strict measured/promotion evidence is material
9. run skill-change-gate against baseline/candidate/protected paths
10. verify package/promotion receipt and destination freshness when applicable
11. accept only when metric rule and change gate both pass for the intended claim scope
```

Do not refresh expected hashes or evaluator identities after a mismatch. Re-baseline explicitly if the experiment definition legitimately changed.

## Self-improvement promotion

For self-improvement keep controller/evaluator/policy independent from candidate mutation. Preserve run/generation/controller/baseline/candidate/last-known-good identities, candidate freeze state, external validation surface, and promotion receipt.

Strict rules:

- candidate cannot authorize its own promotion by editing gate policy, evaluator, fixtures, thresholds, or receipts;
- controller/evaluator/policy identity remains frozen after acceptance begins;
- decision is produced outside candidate mutation surface;
- promotion/package receipt identifies the same frozen candidate;
- destination/current state is rechecked before promotion when material;
- last-known-good remains recoverable until commit succeeds.

## Evaluator exposure and repeated search

Frozen bytes are necessary but not sufficient for holdout claims. If candidate generation/selection repeatedly consumed an evaluator's hidden results, classify that evaluator as development/selection evidence rather than fresh holdout evidence. A final generalization/promotion claim that requires holdout must use a fresh independent holdout or explicitly reduce the claim.

## Static helper integration

```text
<PYTHON> scripts/static_change_gate.py \
  --target <CANDIDATE> \
  --before <BASELINE> \
  --policy strict \
  --profile portable \
  --expected-before-sha256 <BASELINE_TREE_HASH> \
  --expected-target-sha256 <CANDIDATE_TREE_HASH> \
  --protected-path evals/** \
  --artifact-receipt <PACKAGE_RECEIPT_IF_APPLICABLE> \
  --gate-context <GATE_CONTEXT_IF_APPLICABLE> \
  --json <REPORT_OUTSIDE_BOTH_SKILL_ROOTS>
```

## Acceptance rule

Accept only when all applicable conditions hold:

```text
baseline/direct-parent/candidate identities match frozen expectations
and protected evidence is unchanged
and required evaluator/benchmark gates pass
and supplied evidence is candidate-bound
and evaluator exposure supports the claim
and caller-declared trial/replication contract is satisfied
and policy/verifier identity is sufficient for the selected policy
and destination state is fresh when promotion depends on it
and authority expansion is authorized when strict policy requires it
and known consumers are compatible for an ecosystem-safe claim
and package/promotion receipt identifies the same candidate
and skill-change-gate passes
```

The gate never selects hypotheses, tunes benchmark weights, edits evaluator fixtures, repairs the candidate, ranks peers, or claims measured improvement.
