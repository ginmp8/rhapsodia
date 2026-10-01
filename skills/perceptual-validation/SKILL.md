---
name: perceptual-validation
description: "Compare a reference visual artifact with a candidate using bounded perceptual review when semantic visual equivalence matters more than byte or pixel identity. Use for screenshots, rendered UI states, diagrams, charts, slides, PDF/page renders, or generated visual artifacts; validate state alignment first, then report localized differences and a pass/fail/invalid/blocked result. Do not use for executable behavior testing, general design creation, image editing, or when exact deterministic pixel comparison is the real requirement."
---

# Perceptual Validation

## Mission

Provide a portable **perceptual gate** for artifacts where exact pixels are an unreliable proxy for correctness but visual structure, hierarchy, alignment, spacing, content presence, or rendering state still matters.

The first question is not “how different are the pixels?” It is “are these artifacts representing the same state and therefore valid to compare?”

## Ownership boundary

Own:

- comparison-request normalization;
- reference/candidate/state identity checks;
- rubric-guided perceptual comparison;
- localized findings with severity/confidence;
- `perceptual-review-request/v1` and `perceptual-review-result/v1` validation;
- explicit `invalid` results for state-misaligned comparisons.

Do not own:

- image/UI generation or editing;
- executable behavior proof;
- production code repair;
- requirements or acceptance-criteria changes;
- claiming exact pixel equivalence unless a deterministic pixel tool actually measured it;
- checkpoint promotion; callers decide how a perceptual result participates in a gate.

## Authority and side effects

- Default authority is read-only inspection of explicitly supplied or caller-authorized visual artifacts and metadata.
- Do not edit, overwrite, delete, publish, send, deploy, or otherwise mutate the reference, candidate, source repository, or acceptance criteria.
- A caller-owned capture/render step is a separate capability: require explicit authorization for any write/execute side effect and keep generated evidence outside protected source artifacts.
- Record reference, candidate, evaluator/rubric, and review-result identities so the judgment is auditable.
- Fail closed: when authorization, artifact identity, state alignment, or required review capability is unresolved, return `blocked`, `invalid`, `inconclusive`, or `not-run` as appropriate; never infer `pass`.

## Modes

- `request-design`: prepare a valid comparison request and rubric.
- `perceptual-review`: inspect reference and candidate with an image-capable/human reviewer.
- `result-review`: validate a supplied result and evidence identity.

## Core invariants

1. Freeze reference, candidate, intended state, scope, and evaluator/rubric before the judgment used for promotion.
2. Validate **state alignment before visual quality**. Different application/data states yield `invalid`, not `fail`.
3. `pass` and `fail` require matched state. Unknown state yields `inconclusive` or `blocked`.
4. Findings must identify the affected region/element and observable difference; avoid vague “looks off” judgments.
5. Separate objective content/structure absence from perceptual spacing/hierarchy judgment.
6. A candidate change invalidates the prior result when it may affect the reviewed surface.
7. A changed evaluator/rubric invalidates same-evaluator comparison claims unless re-baselined.
8. Required image/render capabilities that are unavailable yield `blocked`/`not-run`, never an inferred pass.
9. Perceptual review is an irreducibly judgment-bearing evidence layer; schema validation makes it auditable, not deterministic.
10. Keep the semantic core host-neutral. Do not require a named vision model.

## Workflow

1. **Resolve artifacts and intended state.** Record immutable identities and what user/system state each artifact should show.
2. **Select scope/rubric.** Limit review to the elements that matter: structure, content presence, typography, spacing/alignment, hierarchy, chart/diagram relationships, or other explicit criteria.
3. **Validate request.** Use the bundled deterministic validator.
4. **Acquire review capability.** Use an available image-capable model, human reviewer, or host-native visual inspection. If absent and required, return `blocked`.
5. **Check state alignment first.** If reference and candidate are not comparable states, return `invalid` with recapture/re-render guidance. Do not score design differences.
6. **Compare only the declared scope.** Produce localized findings, severity, confidence, and evidence notes.
7. **Return result.** `pass | fail | invalid | blocked | inconclusive`.
8. **Invalidate on relevant candidate repair.** A workflow must rerun this gate after a visible change.

## Machine contracts

Use:

- [schemas/review-request.schema.json](schemas/review-request.schema.json)
- [schemas/review-result.schema.json](schemas/review-result.schema.json)
- [references/review-contract.md](references/review-contract.md)

Validate either artifact:

```text
<PYTHON> scripts/validate_perceptual_artifact.py <REQUEST_OR_RESULT.json> --json <REPORT.json>
```

## Portability and degradation

Load [references/host-portability.md](references/host-portability.md) when host differences matter.

The portable core requires no vendor-private model. A runtime may provide:

- image-capable model review;
- human visual review;
- browser/app capture plus one of the above;
- deterministic pixel/DOM/layout measurements as supplemental evidence.

If the host cannot inspect images/rendered artifacts, `request-design` remains available but `perceptual-review` is `not-run`/`blocked`.

## Stop conditions

Stop or return a bounded partial result when:

- reference/candidate identity is missing;
- intended states do not match;
- capture/render state is unknown and materially affects comparison;
- required reviewer capability is unavailable;
- requested judgment depends on hidden interaction/behavior that should use an executable oracle instead;
- the only way to pass is changing the rubric after seeing the candidate.

## Output contract

Return:

1. request/result contract identity;
2. reference and candidate identities;
3. state-alignment result;
4. verdict;
5. localized findings with category/severity/confidence/evidence;
6. recapture/re-render requirement when `invalid`;
7. capability/evaluator limitations and whether the review actually executed.
