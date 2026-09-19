# Hypothesis Discovery Examples

These examples show classification and decision behavior. They are not executed benchmark evidence.

## 1. Saturated metric

Evidence:

- static benchmark is 100/100;
- no executed holdout/ambiguous-activation result exists;
- planned scenarios exist but were not run.

Classification:

- benchmark score -> `saturated` primary metric and regression gate;
- missing holdout behavior -> `evidence-gap`;
- rewriting `SKILL.md` merely to chase 100/100 -> `unsupported-speculation`.

Correct decision: gather an active auxiliary metric (for example holdout failures or ambiguous activation) before selecting another mutation hypothesis.

## 2. Weak activation boundary with measured false positives

Evidence source `E001` records executed false activations on generic code-review prompts. The frontmatter is observed to lack adjacent non-use boundaries.

A valid hypothesis can be:

```text
H001 — testable-hypothesis
Evidence: E001 + direct frontmatter observation
Mechanism: explicit adjacent non-goals should reduce routing ambiguity
Expected effect: false-positive activations decrease on a frozen non-activation suite
Evaluator: existing activation evaluator
Acceptance: fewer false positives with no regression on should-activate cases
Recommendation: test-now
```

The same wording without `E001` or an evaluator is not `test-now`.

## 3. Evidence gap, not a hypothesis

Evidence:

- package has `evals/activation-scenarios.json`;
- there is no record that the scenarios were executed.

Correct item:

```text
kind: evidence-gap
statement: behavioral activation evidence is missing
recommendation: gather-evidence
```

Do not infer that activation is poor merely because execution evidence is absent.

## 4. Duplicate hypotheses

Candidates:

- "Require evaluator before selecting test-now."
- "Prevent selected experiments without a validator."

If subject, mechanism, and effect are the same, normalize them to the same `dedupe_key`, merge evidence refs, and keep one backlog item. Do not preserve both to inflate backlog size.

## 5. Conflicting hypotheses

If `H001` proposes consolidating two references and `H002` proposes splitting the same reference into modes, record symmetric `conflicts_with` edges. They may both remain in the backlog when evidence supports both alternatives, but they cannot be selected in the same experiment shortlist.

## 6. Missing evaluator

A strongly evidenced idea with no evaluator is still not ready:

```text
kind: testable-hypothesis
recommendation: gather-evidence
Evaluator status: missing
```

Define/freeze the evaluator first; then re-run discovery or update the same backlog from new evidence.

## 7. No measurable effect

"Make the skill instructions clearer" is a recommendation, not a testable hypothesis, until an observable effect and acceptance rule are specified (for example fewer ambiguous-routing failures on a frozen suite).

## 8. Ranking tie

If two ready hypotheses have equal priority score, do not choose arbitrarily. Apply the fixed chain: gate effect -> testability -> confidence -> lower risk -> lower cost -> lexical id.

## 9. No mutation recommended

When activation/non-activation/edge/output scenarios are executed and passing, validators/package checks pass, no material token duplication exists, and no active non-saturated metric shows a problem, return:

```text
recommendation: no-mutation-recommended
reason: no evidence-backed, measurable, low-risk mutation is visible from the current snapshot.
```
