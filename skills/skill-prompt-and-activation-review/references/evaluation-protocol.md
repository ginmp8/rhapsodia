# Activation Evaluation Protocol

Protocol version: `2.0.0`.

Use this protocol when activation/boundary text changes or when the user asks for evidence beyond static review. Keep the protocol host-neutral: a host adapter or external harness may execute routing, but the evidence contract is portable.

## At a Glance

- **Purpose:** Define the frozen before/after protocol for activation or boundary changes when behavioral routing evidence or measured comparison claims are requested.
- **Load when:** Activation/boundary text changed and the review will execute or compare host-routing evidence, repeated trials, baseline/candidate arms, or freshness-sensitive routing metrics.
- **Decision impact:** Fixes evaluator and catalog identity, visibility/isolation, trial policy, comparable-arm requirements, metric eligibility, claim vocabulary, gate order, and comparison stop conditions.

## Contents

- Evidence layers
- Canonical suite
- Invocation-mode separation
- Routing environment identity
- Repeated trials
- Baseline/candidate pairing
- Self-generated candidates
- Result evidence contract
- Metrics
- Freshness and historical evidence
- Claim vocabulary
- Gate order
- Stop conditions

## Evidence layers

Keep these distinct:

- `static-contract`: deterministic validation of suite shape, traceability, identities, and package rules;
- `static-adjudication`: linguistic review without observing host auto-invocation;
- `host-routing`: actual skill discovery/invocation observed in a host or harness;
- `runtime`: downstream behavior after routing.

Only `host-routing` supports automatic activation precision/recall or routing-regression claims.

## Canonical suite

`evals/activation-scenarios.json` is the candidate-visible regression/calibration suite. Major version `3` adds invocation modes, negative kinds, realistic dimensions, and explicit external blind-holdout policy.

Because the canonical suite ships with the skill, no bundled case is a true blind holdout. A blind holdout must be evaluator-only and supplied outside candidate-visible inputs.

Before baseline execution:

1. validate the suite with `scripts/validate_activation_suite.py`;
2. freeze the exact suite plus evaluator/rubric/profile assets with `scripts/freeze_activation_evaluator.py`;
3. classify candidate-visible versus evaluator-only assets using `references/evaluator-visibility.md`;
4. inventory the materially available skill catalog and derive its stable hash;
5. freeze the routing profile and fixed trial policy;
6. record suite/evaluator/catalog/environment identities before either arm runs.

If a frozen evaluator is wrong, invalidate the experiment, fix it separately, freeze a new evaluator, and rerun both arms.

## Invocation-mode separation

Every routing scenario declares exactly one mode:

- `explicit`: direct named/selected skill use;
- `implicit`: automatic discovery from user intent;
- `contextual`: automatic discovery under realistic context/noise/multi-intent conditions.

Explicit invocation is useful for direct-use compatibility but is excluded from automatic activation precision/recall. Do not let explicit cases inflate discovery metrics.

## Routing environment identity

Use `references/routing-evidence-profile.md`. Baseline and candidate are behaviorally comparable only when materially relevant routing inputs are equivalent, including:

- host and material host version;
- model/provider/snapshot when model routing is involved;
- discovery mode;
- exact competing catalog identity and size;
- host-specific metadata extensions that can affect discovery;
- evaluator visibility/isolation;
- fixed trial policy.

A changed competing catalog is environment drift. The old run remains historical evidence but cannot be attributed to the prompt/activation change alone.

## Repeated trials

A single routing observation is not repeatability evidence. For claims about reliability or stochastic improvement, predeclare a fixed number of trials and preserve the same count across paired arms.

The bundled comparator reports trigger rates and Wilson 95% intervals. Treat them as descriptive uncertainty over the recorded trials, not proof of independent identical trials.

Use a stronger stochastic-evaluation workflow for broad or high-confidence superiority claims. This reviewer must not manufacture statistical certainty from a small run count.

## Baseline/candidate pairing

For any before/after behavioral claim:

- use exactly the same scenario IDs/prompts/expectations;
- use the same frozen evaluator identity;
- use the same routing fingerprint;
- use the same fixed trial policy and isolation policy;
- preserve baseline/candidate identities separately;
- do not drop difficult/failing cases after baseline observation;
- verify evaluator assets remained unchanged after candidate execution;
- compare with `scripts/compare_activation_evidence.py`.

A static rewrite may still be recommended when execution is unavailable, but the report must label the behavioral delta `not-run` or `blocked`.

## Self-generated candidates

When a skill/controller authors a candidate for the same skill family, keep generation provenance separate from routing evaluation. Record when available:

```text
candidate_origin = self-generated
generation_id
controller_identity
baseline_identity
candidate_identity
```

For blind evaluation, neither the authoring controller nor the evaluated candidate may see evaluator-only expected routes, holdout labels, grader prompts, or post-run adjudication. Leakage invalidates blind-evaluation claims.

Controller identity is provenance, not an activation result. This reviewer does not own candidate promotion or unrelated specialist orchestration.

## Result evidence contract

Use evidence version `2` from `references/routing-evidence-profile.md`. Do not silently compare legacy one-case/one-observation evidence as if it were equivalent.

Validate each arm before comparison:

```text
<PYTHON> scripts/validate_activation_evidence.py --input <ARM.json> --suite <FROZEN_SUITE.json> --json <OUT.json>
```

## Metrics

Keep metrics separated by semantic question:

- **automatic activation precision**: implicit/contextual binary discovery cases only;
- **automatic activation recall**: implicit/contextual binary discovery cases only;
- **explicit route accuracy**: direct invocation cases, reported separately;
- **abstention accuracy**: negative cases where no skill should activate;
- **near-miss false activation rate**: negative cases where a named alternative owner should win;
- **overall expected-route accuracy**: full route equality across all evaluated trials;
- **per-case trigger rate and expected-route-match rate**: diagnostic evidence;
- **routing regressions**: any case whose candidate expected-route-match rate falls below baseline.

Ambiguous, split-handoff, and policy-rejection cases are excluded from binary precision/recall unless the frozen evaluator explicitly gives a binary expectation. They remain eligible for route-regression analysis.

## Freshness and historical evidence

Record `executed_at` plus routing fingerprint on executed/supplied evidence.

When host/model/catalog/discovery identity changes materially:

- preserve the prior result as historical evidence;
- mark it non-comparable for current attribution;
- rerun or explicitly re-baseline before claiming a current behavioral delta.

Do not use date alone as a freshness cutoff. Identity drift, not age by itself, determines comparability.

## Claim vocabulary

- `proposed`: suggested but not validated;
- `observed-static`: supported by text/package inspection or deterministic static validator;
- `supplied`: externally supplied execution evidence;
- `executed`: actually run in the current workflow;
- `derived`: deterministic calculation from executed/supplied evidence;
- `blocked`: required evidence unavailable or invalid.

Never report automatic precision/recall, behavioral improvement, reliability improvement, or regression reduction from static evidence alone.

`measured-single-run` is an observation, not stochastic reliability evidence. `measured-repeated` means repeated trials were recorded under the same declared profile; it is still bounded to that profile and trial set.

## Gate order

1. target identity and scope fixed;
2. suite validates;
3. evaluator and any blind holdout assets frozen;
4. catalog/routing profile and trial policy frozen;
5. baseline evidence captured;
6. candidate authored without evaluator leakage;
7. candidate evidence captured with the same identities;
8. evaluator manifest verifies unchanged;
9. both evidence arms validate under v2;
10. comparator passes suite/evaluator/routing/trial gates;
11. target package validators/tests pass;
12. final candidate freezes; any later edit restarts affected validation.

## Stop conditions

Stop the behavioral comparison when:

- suite/evaluator identity differs between arms;
- materially relevant routing fingerprint differs;
- catalog identity is unavailable and catalog competition is material to the claim;
- trial policies differ;
- hidden evaluator assets leaked or leakage status is unresolved;
- scenario IDs differ;
- a frozen expectation changed after outcome observation;
- required host-routing evidence is unavailable for a requested behavioral metric;
- the only path to pass weakens a boundary, evaluator, or expected result;
- host-specific invocation behavior is too undocumented to interpret the observed route.
