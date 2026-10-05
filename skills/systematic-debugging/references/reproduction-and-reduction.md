# Reproduction and Reduction

## At a Glance

- **Purpose:** Turn a broad or intermittent failure into a stable, minimal diagnostic case while preserving evidence identity.
- **Load when:** Reproduction is unreliable or expensive, the failing case is large, a recent regression is suspected, or record/replay/bisection may help.
- **Decision impact:** Defines known-good/bad comparators, minimization rules, bisection prerequisites, and when deterministic replay can support stronger causal evidence.

## Contents

- Reproducer contract
- Known-good and known-bad states
- Regression bisection
- Failure minimization
- Record and replay
- Reproduction limits

## Reproducer contract

Record exact steps, failure signature, code/version, config identity, input/data identity, relevant environment, concurrency/seed, and observed frequency. A reproducer is useful only if it detects the same failure, not merely any failure.

When nondeterminism is material, capture multiple attempts rather than declaring success/failure from one run.

## Known-good and known-bad states

A comparator should differ in as few material dimensions as possible. Verify that the "good" state really passes the same oracle and that the "bad" state still fails before searching between them.

## Regression bisection

When revisions can be classified with a stable oracle, prefer binary search over manually reading every change. `git bisect` is one implementation; other VCS or deployment histories may provide equivalent search. Treat untestable revisions as `skip`/unknown rather than fabricating good/bad labels.

## Failure minimization

Reduce while preserving the same failure signature:

- request/input fields;
- event/user-action sequences;
- dataset rows/records;
- config entries/flags;
- concurrent actors;
- code/dependency changes;
- services/components in the path.

With an automated oracle, systematic subset reduction/delta debugging can find a minimal failure-inducing set. Manual reduction is acceptable when the search space is small and every removal is tested.

## Record and replay

If the runtime supports deterministic or high-fidelity recording, capture a failing execution once and replay it for repeated diagnosis. This is particularly useful for intermittent failures and reverse debugging. Because support is platform/runtime-specific, record/replay is optional evidence, never a portable-core requirement.

## Reproduction limits

Production-only, external, timing-sensitive, or path-dependent failures may not be safely reproducible. In that case, preserve observational evidence, state the limitation, and use `probable` rather than `confirmed` causality unless another controlled test establishes the link.
