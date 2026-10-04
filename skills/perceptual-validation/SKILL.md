---
name: perceptual-validation
description: "Compare reference and candidate visual artifacts with a bounded, auditable perceptual gate when semantic visual equivalence matters more than exact pixels. Use for screenshots, rendered UI, PDF/page renders, slides, charts, diagrams, and images; validate state/capture comparability first, then evaluate an explicit frozen rubric and gate policy with localized evidence. Do not use for executable behavior proof, image editing/design generation, or tasks whose real requirement is deterministic pixel identity."
---

# Perceptual Validation

## Mission

Provide a host-neutral perceptual gate for visual artifacts. Make objective mechanics deterministic, keep irreducible visual judgment explicit, and never turn subjective similarity into fake pixel determinism.

The first question is **whether the artifacts are comparable states**. Only then judge the declared visual criteria.

## Ownership boundary

Own:

- request normalization and contract validation;
- reference/candidate, state, capture, rubric, policy, and evaluator identity binding;
- rubric-guided perceptual comparison;
- localized findings with evidence, magnitude, impact severity, and confidence;
- result-policy validation and stale-result detection through request binding;
- explicit `invalid`, `blocked`, and `inconclusive` outcomes.

Do not own image/UI generation or editing, executable behavior proof, production repair, acceptance-criteria mutation, checkpoint promotion, or claims of exact pixel equivalence without deterministic measurement.

## Modes

- `request-design` — prepare a comparison request, profile, rubric, gate policy, and evaluator protocol.
- `perceptual-review` — inspect comparable artifacts and emit a bound result.
- `result-review` — validate a supplied result against its exact request and evidence identities.

For new work, use `perceptual-review-request/v2` and `perceptual-review-result/v2`. Preserve v1 only for compatibility with existing callers.

## Reproducibility ceiling

This is a **constrained-subjective** skill. Mechanically enforce identities, schemas, state/capture declarations, criteria coverage, evidence requirements, policy thresholds, and request/result binding. Keep actual perceptual judgment bounded by the frozen rubric and evaluator protocol.

Do not claim deterministic visual truth, cross-model equivalence, or human-level agreement from schema validation.

## Core invariants

1. Freeze reference, candidate, intended state, capture/normalization context, scope, rubric, gate policy, and evaluator protocol before a promotion-bearing review.
2. Validate state/capture alignment before visual quality. Incompatible states yield `invalid`, not `fail`.
3. `pass` and `fail` require `state_alignment=matched`, an executed review, and the frozen policy's required criterion/evidence conditions.
4. Unknown state/capture comparability yields `inconclusive` or `blocked`; never infer `pass`.
5. Every material finding must be localized and evidence-backed when the gate policy requires it.
6. Keep **perceptual magnitude** separate from **impact severity**. A tiny wrong digit can be blocking; a large allowed texture change can be low impact.
7. Supplemental measurements are evidence about a declared property, not a universal similarity oracle. Thresholded measurements must bind to the gate policy.
8. A candidate, rubric, gate-policy, evaluator-protocol, or material capture-context change invalidates prior promotion evidence unless deliberately re-baselined.
9. Low-confidence or evaluator disagreement follows the frozen policy, normally to `inconclusive`; never average uncertainty into a silent pass.
10. Keep the semantic core host-neutral. No named vision model, browser, or proprietary tool is required.

## Workflow

1. **Resolve artifacts and identities.** Prefer immutable hashes; otherwise record a stable semantic/external identity and state its limitation.
2. **Resolve intended state and capture context.** Record the comparison facts that materially affect equivalence (for example viewport, theme, locale, data fixture, expansion/loading state). Do not add irrelevant environment fields.
3. **Select an artifact profile.** Load [references/artifact-profiles.md](references/artifact-profiles.md). Profiles are starting points only; resolve them into an explicit rubric in the request.
4. **Freeze the rubric, gate policy, and evaluator protocol.** Load [references/review-contract.md](references/review-contract.md). For model/human calibration or repeated review, load [references/evaluator-and-calibration.md](references/evaluator-and-calibration.md).
5. **Validate the request.** Use the deterministic validator before review.
6. **Acquire review capability.** Use any available image-capable reviewer or human that satisfies the declared protocol. If absent, return `blocked`/`not-run` rather than guessing from filenames or metadata.
7. **Check state/capture alignment first.** If mismatched, return `invalid` with explicit recapture/re-render guidance. Do not score downstream visual differences.
8. **Review criterion by criterion.** Compare only the declared scope. Attach evidence references to criterion results and findings.
9. **Apply the frozen gate policy.** Do not loosen criteria, thresholds, confidence rules, trial count, or agreement requirements after seeing the candidate.
10. **Validate the result against the exact request.** For v2, cross-binding is mandatory.
11. **Invalidate after relevant visible change.** A repaired candidate needs a new review result.

## Verdict semantics

- `pass` — comparable state; required criteria and frozen policy permit acceptance.
- `fail` — comparable state; one or more criteria/policy rules reject the candidate.
- `invalid` — artifacts are not comparable states/captures; recapture or re-render is required.
- `blocked` — a required capability/evidence source is unavailable.
- `inconclusive` — review ran or partially ran, but confidence/agreement/evidence is insufficient for pass/fail.

## Machine contracts

v1 compatibility:

- [schemas/review-request.schema.json](schemas/review-request.schema.json)
- [schemas/review-result.schema.json](schemas/review-result.schema.json)

v2 canonical contracts:

- [schemas/review-request-v2.schema.json](schemas/review-request-v2.schema.json)
- [schemas/review-result-v2.schema.json](schemas/review-result-v2.schema.json)
- [references/review-contract.md](references/review-contract.md)

Validate a request or a v1 result:

```text
<PYTHON> scripts/validate_perceptual_artifact.py <ARTIFACT.json> --json <REPORT.json>
```

Validate a v2 result with mandatory request binding:

```text
<PYTHON> scripts/validate_perceptual_artifact.py <RESULT.json> --request <REQUEST.json> --json <REPORT.json>
```

The validator uses only the Python standard library and emits stable machine-readable diagnostic codes. Its pass proves contract/policy conformance, not perceptual truth.

## Evidence model

Keep evidence layers distinct:

- **contract evidence** — schemas, request/result binding, policy checks;
- **deterministic measurements** — optional pixel/geometry/DOM/layout metrics tied to their intended property;
- **perceptual evidence** — human or image-capable judgment under the frozen rubric;
- **runtime/behavior evidence** — external executable or browser/tool oracle; this skill does not provide it.

Never let one layer imply another.

## Portability and degradation

Load [references/host-portability.md](references/host-portability.md) when runtime differences matter. The portable core requires only readable artifacts/metadata for request design and Python 3 for deterministic validation when execution is available. Visual review may be human or host-native image inspection.

If the host lacks image inspection, `request-design` and contract validation remain available; `perceptual-review` is `blocked`/`not-run`.

## Stop conditions

Stop or return a bounded non-pass result when:

- reference/candidate identity is unresolved;
- intended state or material capture facts do not align;
- required visual-review capability is unavailable;
- required evidence cannot be inspected;
- requested judgment depends on hidden interaction/behavior that belongs to an executable oracle;
- the only path to green is weakening the frozen rubric, policy, evaluator protocol, or evidence requirement;
- a v2 result cannot be bound to the exact request used for review.

## Output contract

Return:

1. contract and request identity;
2. reference/candidate identities and artifact profile;
3. state/capture alignment;
4. rubric, gate-policy, and evaluator-protocol identities;
5. verdict and whether review executed;
6. criterion results;
7. localized findings with evidence, magnitude, impact severity, and confidence;
8. supplemental measurements with intended property when used;
9. uncertainty/limitations and recapture guidance when applicable;
10. capability limitations and which evidence layers actually executed.
