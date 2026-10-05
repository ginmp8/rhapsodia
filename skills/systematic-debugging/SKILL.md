---
name: systematic-debugging
description: Diagnose bugs, regressions, test/build failures, flaky or nondeterministic behavior, performance/resource failures, hangs/crashes, and multi-component integration problems using evidence-driven hypothesis testing before permanent fixes. Use when the cause is unknown, disputed, or insufficiently evidenced and technical behavior must be reproduced, localized, or explained. During an active production incident, use after or alongside safe mitigation and evidence preservation. Do not use for implementing a known accepted fix, feature development, ordinary code review, or architecture/design work without an observed failure.
---

# Systematic Debugging

## At a Glance

- **Purpose:** Converge from an observed technical failure to the strongest justified causal explanation, smallest safe correction, and verified non-recurrence evidence.
- **Default path:** `triage -> classify -> reproduce/baseline -> gather/reduce -> hypothesize/discriminate -> correct -> verify`.
- **Incident path:** `assess impact -> mitigate safely + preserve evidence -> diagnose -> permanent correction -> verify/prevent recurrence`.
- **Core rule:** Do not apply an unexplained permanent fix. A reversible mitigation may precede root-cause proof when active impact or data risk makes delay unsafe.
- **Evidence rule:** Treat expertise, past incidents, correlation, and plausible stories as hypothesis inputs, not proof.

## Activation Boundary

- **Use when:** an observed technical failure has an unknown, disputed, intermittent, multi-factor, or insufficiently evidenced cause and must be reproduced, localized, or explained before a permanent correction.
- **Do not use when:** the fix is already accepted and only implementation remains, the task is feature development or ordinary code review, or there is no observed failure to diagnose.

## Core Contract

1. State expected versus observed behavior and impact before proposing a permanent correction.
2. Preserve or identify a known baseline; restore it between experiments when prior changes could contaminate results.
3. Gather evidence before narrowing to a cause. If the failure is not reproducible, increase observation rather than guessing.
4. Form explicit hypotheses with predicted and disconfirming observations. Prefer tests that distinguish competing hypotheses.
5. Change one causal variable at a time unless the experiment intentionally tests an interaction.
6. Separate **mitigation** from **diagnosis** and **permanent correction**. Never relabel a workaround as root-cause proof.
7. Verify the original failure path after correction, then run adjacent regression checks appropriate to the touched surface.
8. Record negative results; rejected hypotheses are evidence and must not be silently retried without new information.

## Failure-Class Router

| Class | First strategy |
|---|---|
| recent regression | establish known-good/known-bad states; bisect when an oracle exists |
| input/data dependent | minimize the failing input or sequence while preserving the failure |
| flaky/nondeterministic | repeat with frozen seed/environment; inspect ordering, timing, races, shared state; use record/replay or race tools when available |
| distributed/integration | correlate one execution across boundaries; inspect contracts, propagation, retries, versions, and state transitions |
| performance | freeze workload/baseline; identify constrained resource; profile before optimizing |
| crash/exception | capture complete error/stack/state; trace invalid state backward to its origin |
| hang/deadlock | inspect thread/task/lock state and wait-for relationships; avoid timeout-as-fix |
| memory/resource | measure growth/pressure; identify allocation/retention/leak/resource ownership before changing limits |
| environment/config | fingerprint and diff known-good versus failing environments/configuration |
| unknown | use the general workflow, then reclassify when evidence narrows the failure |

## Workflow at a Glance

1. **Triage:** define symptom, expected behavior, impact, scope, and whether immediate mitigation is required.
2. **Classify:** choose the failure class above; load only the matching direct reference.
3. **Reproduce and baseline:** capture exact steps, inputs, version/config/environment, frequency, and a known-good comparator when available.
4. **Gather and reduce:** collect the least-invasive evidence that localizes the failure; minimize input/change/execution when useful.
5. **Hypothesize and discriminate:** state `cause because evidence`; predict what must be observed if true and what would reject it; run the smallest safe distinguishing test.
6. **Correct and verify:** implement the smallest root-cause correction, reproduce the original path, run focused/adjacent checks, and record remaining uncertainty.

## Control Model

Use the lowest reliable control layer for the evidence available: runtime/tool evidence and reproducible experiments first; schemas/contracts for structural facts; validators/gates for objective acceptance; bounded judgment for causal interpretation that cannot be mechanically proved. Never convert uncertainty into a stronger control claim merely to make the result deterministic.

## Causal Confidence

Use the strongest label the evidence supports:

- `confirmed` — controlled reproduction/manipulation establishes the causal relationship.
- `probable` — evidence strongly supports causality but definitive reproduction is unavailable or unsafe.
- `plausible` — consistent with evidence but not yet distinguished from alternatives.
- `correlated` — moves with the symptom; causality is not demonstrated.
- `ruled-out` — a discriminating test contradicted the hypothesis.
- `unknown` — evidence is insufficient.

## Critical Invariants and Diagnostic Safety

- Never stack speculative fixes. Revert failed experiments before testing the next hypothesis unless cumulative state is itself the subject of the experiment.
- Do not infer an architectural defect from an arbitrary number of failed attempts. Repeated non-improving attempts trigger a reset of baseline, assumptions, evidence, and hypothesis set; architecture becomes one hypothesis only when evidence points there.
- Prefer repository/source-of-truth behavior, current runtime evidence, and controlled tests over memory or authority.
- Before adding diagnostics, consider secrets/PII, production overhead, timing perturbation, destructive side effects, and authorization. Collect the minimum evidence needed.
- Do not dump arbitrary environment variables, request bodies, credentials, tokens, or customer data into logs.
- Preserve exact error messages, stack traces, versions, timestamps/ordering information, and correlation identifiers when relevant.
- A passing rerun is not proof for flaky failures; use repeated/stability evidence when nondeterminism is material.
- Do not weaken tests, validators, thresholds, or expected outcomes to make a candidate appear fixed.

## Stop Conditions

Stop or return a bounded diagnostic result when the next experiment would be destructive or unauthorized, required evidence would expose sensitive data without a safer alternative, no available observation can distinguish the live hypotheses, or the requested causal certainty exceeds the available evidence. Do not invent a cause to continue.

## Direct Resource Map

- [`references/triage-and-incident-safety.md`](references/triage-and-incident-safety.md) — active incidents, mitigation-before-RCA exception, evidence preservation, and diagnostic safety.
- [`references/failure-class-routing.md`](references/failure-class-routing.md) — detailed strategy by regression, nondeterminism, distributed, performance, crash/hang/resource, and environment classes.
- [`references/reproduction-and-reduction.md`](references/reproduction-and-reduction.md) — reproducible cases, known-good/bad baselines, bisection, minimization, and record/replay.
- [`references/hypothesis-and-causal-confidence.md`](references/hypothesis-and-causal-confidence.md) — hypothesis ledger, predictions, disconfirmation, confidence labels, and repeated-failure reset.
- [`root-cause-tracing.md`](root-cause-tracing.md) — backward tracing from manifestation to originating invalid state or trigger.
- [`references/distributed-debugging.md`](references/distributed-debugging.md) — boundary evidence, trace/correlation context, retries, versions, and cross-service state.
- [`references/performance-and-concurrency.md`](references/performance-and-concurrency.md) — performance, races, deadlocks, flakiness, resource pressure, and timing-sensitive diagnosis.
- [`condition-based-waiting.md`](condition-based-waiting.md) — replace guessed sleeps with state/condition waits when timing itself is not the behavior under test.
- [`defense-in-depth.md`](defense-in-depth.md) — prevention after cause is understood; place safeguards at ownership/trust/risk boundaries instead of duplicating checks everywhere.

## Incident Exception

When an active failure is materially harming users, availability, integrity, or data, prioritize a **safe, reversible mitigation** that limits impact. Preserve diagnostic evidence before the mitigation when feasible and low-risk. Record exactly what changed. After stabilization, return to causal diagnosis; do not treat the mitigation's success as sufficient proof of the underlying cause.

## Detailed Normal Workflow

### 1. Triage the symptom

Capture:

- expected behavior versus actual behavior;
- first known occurrence and frequency;
- affected users/components/versions/environments;
- severity and data/safety implications;
- exact errors, warnings, and stack traces;
- whether a workaround/mitigation already changed system state.

Do not start with a favored fix. Start with a falsifiable problem statement.

### 2. Reproduce and establish comparators

Prefer the smallest reliable reproducer. Freeze the material inputs: code revision, config, dependency/runtime versions, data shape, seed, locale/timezone, concurrency, and relevant external state. Identify a known-good state whenever possible.

If reproduction is intermittent, record frequency and conditions; do not convert one successful rerun into a `ruled-out` conclusion. If reproduction is unsafe in production, use lower-risk observation, non-production replay, or existing traces/logs and lower the causal-confidence claim accordingly.

### 3. Inspect recent changes and working examples

Compare failing and working states. Use diffs, deploy/config history, dependency/version changes, schema changes, environment drift, and similar working code. Read enough of the relevant reference implementation or contract to understand its assumptions; do not require reading unrelated code merely to satisfy process.

### 4. Gather evidence and localize

At each relevant boundary, capture the smallest useful evidence: input contract, output/result, timing, attempt/retry, version/config identity, state transition, and correlation/trace identity. Prefer existing observability before adding instrumentation.

When the failure is deep in a call/data chain, trace backward using [`root-cause-tracing.md`](root-cause-tracing.md). When the failing case is large, reduce it using [`references/reproduction-and-reduction.md`](references/reproduction-and-reduction.md).

### 5. Run discriminating experiments

For each live hypothesis record:

- claim;
- evidence for/against;
- prediction if true;
- disconfirming observation;
- smallest safe test;
- result and confidence state.

Prefer a test that separates two or more plausible explanations over a test that can only confirm the favored one. Treat side effects and timing perturbation introduced by the diagnostic itself as possible confounders.

### 6. Correct the cause

Implement the smallest coherent correction supported by the evidence. Avoid unrelated cleanup/refactoring. When feasible, create a failing regression test or executable reproducer before the permanent fix; when infeasible or unsafe, document the substitute verification and why a pre-fix test could not be used.

Use [`defense-in-depth.md`](defense-in-depth.md) only after the failure mechanism is understood. Prevention must reinforce the actual ownership/trust/risk boundaries, not scatter duplicate checks through every layer.

### 7. Verify and close

Require evidence that:

1. the original reproducer/failure path no longer fails;
2. the focused correction test passes;
3. relevant adjacent tests/checks did not regress;
4. flaky/performance claims use repeated or baseline-comparable evidence when needed;
5. production behavior is observed after deployment when runtime evidence is part of the claim;
6. remaining unknowns and causal confidence are explicit.

Convert confirmed generalizable failures into a regression test, validator, invariant, monitor, safer default, or documented recovery path when justified.

## Repeated Non-Improving Attempts

Do not use a magic attempt count to declare the architecture wrong. If repeated experiments or repair attempts do not improve the same objective failure set:

1. stop accumulating changes;
2. restore the known baseline;
3. review the evidence/hypothesis ledger;
4. revalidate the reproducer and environment identity;
5. identify assumptions that were treated as facts;
6. broaden or reformulate hypotheses;
7. investigate architecture only if the evidence indicates structural coupling/state/interface failure.

## When Definitive Root Cause Is Unavailable

A bounded conclusion may be correct. For external, timing-sensitive, path-dependent, or production-only failures, report the strongest supported causal label, what was ruled out, what remains unknown, and what evidence would raise or lower confidence. Implement retries/timeouts/degradation/monitoring only when they address an understood failure mode or are explicitly labeled resilience mitigation rather than causal correction.

## Output Contract

For substantive debugging work, report:

- symptom and impact;
- failure class and selected strategy;
- baseline/reproduction conditions;
- evidence gathered;
- hypotheses with confidence/dispositions;
- mitigation versus permanent correction, clearly separated;
- files/config changed;
- verification actually executed and results;
- residual uncertainty, risk, and follow-up evidence needed.

Never claim a root cause, fix, passing test, runtime recovery, or performance improvement without matching executed/supplied evidence.

## Stop Conditions

Stop and return a bounded diagnosis instead of guessing when destructive/production experiments lack authorization; required evidence would expose secrets/PII without a safe collection path; no reliable oracle or observation can distinguish the remaining hypotheses; the environment/source truth needed for diagnosis is unavailable; or the requested conclusion requires stronger certainty than the evidence can support.
