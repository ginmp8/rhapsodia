# Evidence, Calibration, and Review Identity

## At a Glance

- **Purpose:** Define evidence layers, claim ceilings, evaluator calibration, review identity, repeated-trial policy, and bounded validator challenges.
- **Load when:** Load when making conformance, readiness, portability, behavioral, reliability, provenance, score-confidence, or evaluator-quality claims.
- **Decision impact:** Determines which evidence can support each claim, when a result may be called measured, how confidence is bounded, and when identity or calibration gaps block stronger conclusions.

## Contents

- 1. Review layers
- 2. Specification baseline
- 3. Evidence and grader strength
- 4. Stochastic behavioral evidence
- 5. Weighted score, evidence coverage, and confidence
- 6. Review evidence manifest
- 7. Bounded validator challenge
- 8. Claim ceilings


Use this reference when a review makes normative conformance, readiness, portability, behavioral, reliability, evaluator, or provenance claims. These rules are cross-cutting evidence controls; they do not add score dimensions.

## 1. Review layers

Keep three questions separate:

| Layer | Question | Typical evidence |
|---|---|---|
| Normative conformance | Does the package satisfy a named specification/profile? | pinned/retrieved spec baseline + deterministic conformance checks |
| Package integrity | Are files, references, scripts, schemas, adapters, and package mechanics internally valid? | structural inspection, syntax, link/package validators |
| Operational quality | Will activation, routing, workflow, ownership, output, compatibility, and evidence behavior work as claimed? | semantic tracing, scenarios, runtime evidence, repeated trials when required |

A pass in one layer never implies a pass in another. `skills-ref`, frontmatter parsing, syntax checks, and package shape are normative/package evidence only unless the executed check actually exercises behavior.

## 2. Specification baseline

When a finding or verdict claims compliance with an external specification:

- identify the specification locator/name and version, revision, commit, retrieval date, or other stable identity available;
- distinguish normative requirements from recommendations and experimental/implementation-varying fields;
- do not make a compliance claim against an unnamed "current spec";
- if the specification is live and cannot be pinned, record the frozen research/report artifact that interpreted it and label freshness limitations;
- do not import one host's extensions into the portable-core contract unless the target explicitly requires that host.

If no normative compliance claim is made, a missing external spec baseline is not a defect by itself.

## 3. Evidence and grader strength

Prefer the lowest reliable control layer that can decide the claim:

1. deterministic schema/test/runtime assertion for objective properties;
2. explicit contract assertion traced to canonical source and consumer;
3. reference-guided, pairwise, or classification judge for bounded semantic decisions;
4. holistic rubric judgment for irreducible review questions;
5. human or independently calibrated review when the consequence or subjectivity requires it.

For model-judge evidence record calibration status as one of:

- `not-used`;
- `uncalibrated`;
- `calibrated-against-reference`;
- `human-confirmed`.

Do not upgrade `uncalibrated` model judgment to `measured`. Prefer pairwise/reference-guided decisions to unconstrained scoring when a comparable baseline/reference exists. Keep ties/unknowns rather than forcing a verdict when evidence is insufficient.

## 4. Stochastic behavioral evidence

One execution can establish a hard failure, but one successful execution rarely establishes reliable activation or behavior.

Require repeated trials when the claim is materially about reliability, consistency, activation precision/recall, robustness, or success probability. Before running repeated trials, freeze as applicable:

- prompt/task/scenario set;
- expected route or success criteria;
- grader/evaluator logic;
- relevant model/host/tool/environment profile;
- trial budget and stop rule.

Report raw outcomes and trial count. Use `pass@k`, `pass^k`, confidence intervals, or another reliability statistic only when its assumptions and calculation are explicit. Do not infer trial independence merely because multiple runs were executed.

If repeated behavioral execution is unavailable, keep the claim ceiling at `static`, `observed`, `inferred`, `planned`, or `blocked` as appropriate. The review may still be complete for a static profile.

## 5. Weighted score, evidence coverage, and confidence

The weighted 0-100 score is an internal static quality indicator under `references/review-rubric.md`; it is not a universal compliance grade or behavioral reliability metric.

Always pair a substantive score with:

- **review profile:** portable core and any explicitly reviewed hosts/specification;
- **hard gates:** blockers/majors and claim-specific gates;
- **evidence coverage:** `complete`, `partial`, `not-run`, or `blocked` for structural/package, semantic, behavioral, runtime, and host-semantic layers;
- **confidence:** `high`, `medium`, or `low`, with a short reason tied to evidence quality and missing surfaces.

A `READY` verdict means ready within the declared review profile and evidence ceiling. It never means universally production-ready, behaviorally reliable on every host, security-reviewed, or free of undiscovered defects.

## 6. Review evidence manifest

When filesystem/code execution is available and identity matters, create a deterministic manifest before interpretation or before a baseline/candidate comparison:

```text
<PYTHON> scripts/build_review_evidence_manifest.py \
  --target <TARGET> \
  --host-profile <portable|openai|codex|claude|copilot|cursor> \
  --spec-baseline <SPEC_IDENTITY_OR_NONE> \
  --evaluator <LABEL=PATH> \
  --source '<LABEL|LOCATOR|IDENTITY>' \
  --json-out <OUTSIDE_TARGET>/review-evidence.json
```

The helper hashes target/reviewer/evaluator bytes without executing target code. Keep its output outside the reviewed target. It intentionally emits no current timestamp and no absolute filesystem paths, so identical inputs and declared identities produce identical manifest bytes.

A manifest should bind, when material:

- target identity;
- reviewer-package identity;
- specification baseline;
- requested host profiles;
- evaluator/scenario identities;
- source identities used for decision-critical claims.

Command logs and runtime transcripts remain separate evidence artifacts; do not embed large execution outputs into the identity manifest.

## 7. Bounded validator challenge

Use only when a validator is decision-critical and baseline success does not establish that it protects the claimed invariant.

Procedure:

1. preserve the real target and evaluator inputs unchanged;
2. create a temporary copy or isolated fixture outside the target;
3. alter exactly one protected invariant (for example required field, contract version, canonical path, rejected legacy alias, or broken reference);
4. run the same validator against the challenged copy;
5. require the deliberate violation to fail for the relevant reason;
6. discard the temporary copy and record the challenge as executed evidence.

A challenge that still passes is evidence that the validator does not protect that invariant. Do not mutate frozen fixtures/expected outputs, weaken thresholds, or make challenge testing mandatory for low-impact validators.

## 8. Claim ceilings

Use the strongest claim supported by the weakest required evidence layer:

- structural pass -> structurally valid for inspected scope;
- semantic review -> semantically coherent for inspected scope;
- one scenario run -> observed behavior for that run only;
- repeated comparable trials -> measured reliability for the tested scenario/profile only;
- host documentation inspection -> documented host semantics, not runtime equivalence;
- actual host execution -> runtime evidence for that host/environment;
- calibrated/human-confirmed judge -> stronger semantic evaluation, still bounded to the evaluated cases.

Never collapse these into a single "fully validated" claim.
