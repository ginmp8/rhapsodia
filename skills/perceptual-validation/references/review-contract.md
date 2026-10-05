# Perceptual Review Contract

## At a Glance

- **Purpose:** Define the canonical v2 request/result contract that freezes identities, comparable state/capture facts, rubric, gate policy, evaluator protocol, evidence requirements, and request/result binding while preserving v1 compatibility.
- **Load when:** Designing a v2 request, interpreting or producing a v2 result, deciding gate-policy semantics, checking stale-result binding, or validating how findings/measurements affect a verdict.
- **Decision impact:** Determines what must be frozen before review, when artifacts are comparable, what evidence a pass/fail may rely on, how uncertainty and measurements are treated, and when a result is invalid or stale.

## Contents

- Contract generations
- Request v2
- Rubric
- Gate policy
- Evaluator protocol
- Result v2
- State and verdict relations
- Compatibility v1

## Contract generations

Use v2 for new reviews. v1 remains accepted for compatibility and is intentionally not reinterpreted as v2.

| Contract | Status | Binding |
|---|---|---|
| `perceptual-review-request/v1` / `perceptual-review-result/v1` | compatibility | result identities are locally validated |
| `perceptual-review-request/v2` / `perceptual-review-result/v2` | canonical | result must validate against the exact request digest and repeated identities |

An incompatible future semantic change requires a new contract version rather than silently changing v2.

## Request v2

A v2 request freezes the inputs that can materially change the judgment:

- `reference` and `candidate` identities plus identity kind;
- `artifact_kind` and resolved `artifact_profile`;
- intended reference/candidate state;
- capture/normalization identity and explicit comparison facts;
- declared comparison scope;
- versioned rubric and criterion list;
- versioned gate policy;
- versioned evaluator protocol.

### Artifact identity

Prefer `identity_kind=sha256` when exact bytes are available. Use `semantic` or `external` only when byte identity is unavailable and record the resulting limitation in the review. A semantic identity is not cryptographic proof.

### Capture context

`capture_context.comparison_keys` declares only the facts that materially affect comparability. Each key must have a value in both `reference_facts` and `candidate_facts`. Different declared values make the pair incompatible for `state_alignment=matched`; missing material facts make alignment unknown.

Examples of useful facts are viewport, theme, locale, fixture/data snapshot, zoom/device scale, font set, or render state. Do not require fields that cannot affect the reviewed surface.

`normalization_policy_identity` records intentional normalization such as animation/caret suppression, deterministic fixture setup, masks for explicitly ignored volatile regions, or stable renderer settings. Normalization must not hide semantic content that the rubric requires.

## Rubric

The rubric is explicit, versioned, and frozen before review. Each criterion has:

- stable `id`;
- category;
- `required` flag;
- a falsifiable description;
- expected evidence types.

Artifact profiles provide starting criteria, not hidden policy. Resolve the actual criteria into the request so a result is auditable without knowing which host performed the review.

Do not reduce visual equivalence to one scalar similarity number. Review criteria separately when the semantics differ: content presence, structure, layout, alignment, spacing, typography, hierarchy, component shape, chart encoding, or diagram relations.

## Gate policy

The gate policy turns observations into a decision. Freeze it before seeing the candidate.

Canonical policy fields:

- `blocking_severities`;
- `max_medium_findings`;
- `minimum_confidence`;
- `low_confidence_action=inconclusive`;
- evidence requirements for findings and required criteria;
- `required_trials`;
- optional agreement requirement;
- `disagreement_action=inconclusive`.

A project may choose stricter or looser thresholds before review. The skill must not tune policy after observing the candidate merely to obtain a pass.

## Evaluator protocol

The evaluator protocol records who/how the judgment is produced without coupling the portable core to a vendor:

- `kind`: `human | model | hybrid`;
- review mode;
- required capability;
- optional implementation/prompt identity;
- whether presentation order must be swapped.

Use [evaluator-and-calibration.md](evaluator-and-calibration.md) when repeated trials, agreement, or higher-stakes adjudication are material.

## Result v2

A result binds to the exact request through:

- canonical `request_digest` (SHA-256 of sorted compact JSON UTF-8 bytes);
- matching review, reference, candidate, rubric, policy, and evaluator-protocol identities.

The validator rejects mismatches rather than treating a stale result as current evidence.

### Criterion results

Every required criterion must be represented for `pass|fail`. The frozen policy controls minimum confidence and evidence requirements.

### Findings

A finding records:

- human-readable region;
- optional structured locator;
- criterion/category;
- observable difference and difference type;
- `perceptual_magnitude`;
- `impact_severity`;
- confidence and optional uncertainty reason;
- evidence references.

Magnitude and severity are intentionally independent. Never derive business/semantic severity mechanically from changed pixel area.

### Supplemental measurements

Measurements are optional. Each measurement names:

- method/version;
- intended property;
- scope and optional criterion;
- value;
- optional threshold;
- outcome and evidence reference.

A thresholded measurement must bind to the gate-policy identity. Pixel diff, geometry, DOM/layout, SSIM-like, learned perceptual, or other metrics remain supplemental unless the frozen rubric/policy explicitly makes that property decisive. No measurement is a universal perceptual oracle.

## State and verdict relations

- `pass|fail` require `state_alignment=matched` and `review_executed=true`.
- `invalid` requires `state_alignment=mismatched` plus actionable recapture/re-render guidance.
- `blocked|inconclusive` require explicit limitations or uncertainty reasons.
- a declared capture/state mismatch cannot be reported as `matched`.
- required criterion coverage, confidence, evidence, trial count, agreement, order-swap, severity, and medium-finding caps are enforced from the frozen request.
- `policy_decision.outcome` must match `verdict`.

## Compatibility v1

v1 remains valid under its original semantics:

- `pass|fail` require matched state and executed review;
- `invalid` requires mismatched state;
- `fail` requires a finding;
- `pass` cannot contain blocking/high findings.

Use v1 only to validate existing integrations. Do not claim v2 request binding, capture normalization, criterion coverage, or gate-policy enforcement for a v1 result.
