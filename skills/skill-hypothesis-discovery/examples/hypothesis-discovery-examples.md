# Hypothesis Discovery Examples

## At a Glance

- **Purpose:** Calibrate classification and decision behavior with concrete examples; these examples are explanatory fixtures, not executed benchmark or runtime evidence.
- **Load when:** A borderline classification, saturation, deduplication, conflict, evaluator, research, falsification, deep-discovery, or evidence-gap decision needs an example after the normative root/reference rules are known.
- **Decision impact:** Helps interpret the normative contracts consistently but cannot override them, establish behavioral success, or substitute for validator/test evidence.

## Contents

- 1. Saturated metric
- 2. Weak activation boundary with measured false positives
- 3. Evidence gap, not a hypothesis
- 4. Duplicate hypotheses
- 5. Conflicting hypotheses
- 6. Missing evaluator
- 7. No measurable effect
- 8. Ranking tie
- 9. No mutation recommended
- 10. Bounded research closes a source-resolvable gap
- 11. Validation leakage
- 12. Falsification before research-backed handoff
- 13. Deep-discovery is not deep research
- 14. Evidence-gap priority

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

## 10. Bounded research closes a source-resolvable gap

Evidence exists for a target failure, but the proposed mechanism depends on an external standard or research result that is not in the package. With `research_policy: if-needed`, run bounded research for that specific question, deliberately search for contradicting evidence, freeze the resulting corpus, validate the research-discovery artifact, then derive the v2 hypothesis. Do not make network access a permanent prerequisite.

## 11. Validation leakage

A candidate already won a benchmark. That winning result cannot be retroactively cited as the discovery evidence for why the same change should have been hypothesized. Classify it as `validation` evidence. To use the new observation for another hypothesis, explicitly re-baseline with a new discovery snapshot and new hypothesis identity.

## 12. Falsification before research-backed handoff

A literature-backed hypothesis has strong supporting findings. Before it can proceed to v2 handoff, record a bounded attempt to find counterevidence or a competing mechanism, at least one falsification criterion, and an independent/held-out deciding evaluator. `confirmation found` by itself is insufficient.

## 13. Deep-discovery is not deep research

`deep-discovery` may generate more internal candidates, critique them adversarially, search counterexamples, consolidate, and deterministically rank the final bounded set. It does not require web research or multiple agents. If the evidence is already sufficient, deep-discovery can remain fully local and serial.

## 14. Evidence-gap priority

For two open gaps:

```text
G001: information_value=5, collection_cost=2 -> priority 4
G002: information_value=4, collection_cost=1 -> priority 3
```

Collect `G001` first. This is a bounded diagnostic heuristic, not a statistical posterior and not a mutation score.

