---
name: perceptual-validation
description: "Compare reference and candidate visual artifacts with a bounded, auditable perceptual gate when semantic visual equivalence matters more than exact pixels. Use for screenshots, rendered UI, PDF/page renders, slides, charts, diagrams, and images; validate state/capture comparability first, then evaluate an explicit frozen rubric and gate policy with localized evidence. Do not use for executable behavior proof, image editing/design generation, or tasks whose real requirement is deterministic pixel identity."
---

# Perceptual Validation

## Mission and boundary

Provide a host-neutral, constrained-subjective gate for semantic visual equivalence. First establish that reference and candidate are comparable states/captures; only then judge the declared visual criteria. Deterministic contract checks constrain the review but never prove perceptual truth.

Use this skill to normalize/bind a perceptual-review contract, compare supplied visual artifacts under a frozen rubric/policy, or validate a supplied result. Own identity/state/capture/rubric/policy/evaluator binding, criterion review, localized findings, policy application, stale-result detection, and explicit non-pass outcomes. Do **not** own image/UI generation or editing, executable behavior proof, production repair, acceptance-criteria mutation, checkpoint promotion, or exact-pixel claims without deterministic measurement.

## Modes and contracts

- `request-design` — prepare/freeze the comparison request, artifact profile, rubric, gate policy, and evaluator protocol.
- `perceptual-review` — inspect comparable artifacts criterion by criterion and emit a request-bound result.
- `result-review` — validate a supplied result against the exact request and evidence identities.
- New work uses `perceptual-review-request/v2` and `perceptual-review-result/v2`; v1 is compatibility-only.

## Critical invariants

1. Freeze reference, candidate, intended state, capture/normalization context, scope, rubric, gate policy, and evaluator protocol before a promotion-bearing review.
2. Validate state/capture alignment before visual quality. Mismatch => `invalid`; unknown comparability => `inconclusive` or `blocked`; never infer `pass`.
3. `pass|fail` require `state_alignment=matched`, `review_executed=true`, and all frozen criterion/evidence/policy conditions.
4. Review only declared scope; localize material findings and attach evidence when policy requires it.
5. Keep **perceptual magnitude** separate from **impact severity**; changed area never mechanically determines semantic/business severity.
6. Supplemental pixel/geometry/DOM/layout/perceptual metrics prove only their declared property; thresholded measurements bind to the frozen gate policy and are never universal similarity oracles.
7. Candidate, rubric, policy, evaluator protocol, or material capture-context changes invalidate prior promotion evidence unless deliberately re-baselined; any relevant visible repair requires a new review.
8. Low confidence or required-reviewer disagreement follows the frozen policy, normally to `inconclusive`; never average uncertainty into a silent pass.
9. Keep contract, deterministic-measurement, perceptual, and runtime/behavior evidence distinct; one layer never implies another.
10. Keep the semantic core host-neutral: no named model/browser/proprietary tool is required, and schema validation never implies deterministic visual truth or cross-reviewer equivalence.

## Quick-start workflow

1. Resolve reference/candidate identities; prefer immutable hashes, otherwise record semantic/external identity and its limitation.
2. Resolve intended state and only material capture facts (for example viewport, theme, locale, fixture/data snapshot, zoom/font/render state).
3. Select the narrowest profile in [artifact profiles](references/artifact-profiles.md). Profiles are starting points, not hidden criteria; resolve the chosen profile into explicit request criteria.
4. Freeze rubric, gate policy, and evaluator protocol using [review contract](references/review-contract.md); load [evaluator/calibration](references/evaluator-and-calibration.md) only for repeated trials, agreement, bias controls, or higher-stakes adjudication.
5. Validate the request before review. Acquire a human/image-capable reviewer satisfying the protocol; if unavailable, return `blocked`/`not-run` rather than infer from metadata.
6. Check state/capture alignment first. On mismatch return `invalid` with recapture/re-render guidance and do not score downstream visual differences.
7. Review every required criterion in declared scope, attach evidence, and apply the frozen policy without post-hoc threshold/criterion/confidence/trial/agreement changes.
8. Validate the result against the exact request; v2 cross-binding is mandatory. Any material visible change reopens review.

## Verdicts and degraded operation

- `pass` — comparable state and frozen criteria/policy permit acceptance.
- `fail` — comparable state but one or more frozen criteria/policy rules reject the candidate.
- `invalid` — state/capture is mismatched; recapture/re-render is required.
- `blocked` — required review capability/evidence is unavailable.
- `inconclusive` — review ran or partially ran but confidence/agreement/evidence is insufficient.
- Without visual inspection, request design/contract validation remain available but perceptual review is `blocked`/`not-run`. Without Python, perceptual review may still run, but deterministic validation is `not-run`. Without capture/render, compare only supplied artifacts. If agreement is required but independent review is unavailable, return `blocked`/`inconclusive`. See [host portability](references/host-portability.md).

## Deterministic validation

Canonical schemas: [request v2](schemas/review-request-v2.schema.json) and [result v2](schemas/review-result-v2.schema.json). v1 compatibility schemas remain [request v1](schemas/review-request.schema.json) and [result v1](schemas/review-result.schema.json).

```text
<PYTHON> scripts/validate_perceptual_artifact.py <REQUEST_OR_V1_RESULT.json> --json <REPORT.json>
<PYTHON> scripts/validate_perceptual_artifact.py <V2_RESULT.json> --request <V2_REQUEST.json> --json <REPORT.json>
```

The bundled validator is Python-stdlib-only and emits stable machine-readable diagnostics. A pass proves schema/request-binding/frozen-policy conformance only, not perceptual correctness.

## Stop conditions

Stop or return bounded non-pass when identities are unresolved; material state/capture comparability is mismatched/unknown; required evidence/capability is unavailable; the requested claim depends on hidden executable behavior; green would require weakening the frozen rubric/policy/protocol/evidence; or a v2 result cannot bind to the exact reviewed request.

## Output contract

Return contract/request identity; reference/candidate identities and profile; state/capture alignment; rubric/policy/evaluator identities; verdict and whether review executed; criterion results; localized findings with evidence, magnitude, impact severity, confidence; supplemental measurements with intended property; uncertainty/recapture guidance; and capability limitations plus which evidence layers actually executed.
