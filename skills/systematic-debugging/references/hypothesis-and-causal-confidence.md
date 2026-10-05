# Hypothesis and Causal Confidence

## At a Glance

- **Purpose:** Keep diagnosis falsifiable, preserve negative evidence, and prevent correlation or authority from being promoted to causality.
- **Load when:** More than one cause is plausible, experiments are being designed, repeated attempts have failed, or root-cause certainty is disputed.
- **Decision impact:** Defines the hypothesis ledger, confidence labels, discriminating-test rule, confounder handling, and reset behavior after non-improving attempts.

## Contents

- Hypothesis record
- Discriminating experiments
- Confidence states
- Confounders
- Repeated non-improving attempts
- Multi-factor causes

## Hypothesis record

For each live hypothesis record:

```yaml
id: H1
claim: "X causes the observed failure"
evidence_for: []
evidence_against: []
prediction: "If X is causal, Z should be observed"
disconfirmation: "If W is observed, reject or weaken X"
test: "smallest safe experiment"
result: null
confidence: plausible
```

Record ruled-out hypotheses instead of deleting them. Only revive one when new evidence changes its premises.

## Discriminating experiments

Prefer experiments whose possible outcomes separate competing explanations. A test that only reproduces the favored story but cannot reject it is weak evidence. Restore baseline state between experiments when prior interventions could affect the next result.

## Confidence states

- `confirmed`: controlled reproduction/manipulation demonstrates the causal link.
- `probable`: strong causal evidence, but definitive reproduction is unavailable or unsafe.
- `plausible`: compatible with current evidence; alternatives remain.
- `correlated`: associated with the symptom without demonstrated causation.
- `ruled-out`: a valid distinguishing test contradicted the hypothesis.
- `unknown`: evidence is insufficient.

## Confounders

Consider diagnostic-induced changes: added logging can alter scheduling; retries can mask timeouts; cache clears can remove the state needed to reproduce; environment edits can change dependency resolution. Record these as part of experiment state.

## Repeated non-improving attempts

Do not infer "architecture is wrong" from a fixed attempt count. When repeated interventions do not improve the same objective failure set, stop the branch, restore baseline, revalidate reproduction/environment, review assumptions, and rebuild the hypothesis set. Architecture becomes a live hypothesis only when evidence points to structural coupling, hidden shared state, broken ownership, or incompatible interfaces.

## Multi-factor causes

Allow multiple jointly necessary causal factors. Do not force a single-root narrative when the failure requires an interaction such as load + race + configuration. Preserve which factors are necessary, sufficient, or merely contributing when evidence allows that distinction.
