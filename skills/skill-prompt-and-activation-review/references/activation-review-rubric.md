# Activation Review Rubric

Use with `references/activation-contract.md`. The contract defines semantics; this rubric defines how to inspect and report evidence.

## At a Glance

- **Purpose:** Define the inspection, severity, evidence, and finding-record rubric used to review discovery descriptions, routing boundaries, scenarios, and activation-text changes.
- **Load when:** A static or evidence-backed review must judge routing specificity, FP/FN risk, overlap, scenario quality, evidence comparability, severity, or rewrite traceability.
- **Decision impact:** Determines whether an issue is a risk or confirmed defect, which severity applies, what evidence a rewrite needs, and what must appear in each finding record.

## Contents

- 1. Discovery description
- 2. Invocation-mode review
- 3. False-positive risk versus confirmed false positive
- 4. False-negative risk versus confirmed false negative
- 5. Negative semantics and overlap
- 6. Ambiguity, boundary, and activation gaming
- 7. Scenario quality
- 8. Evidence comparability
- 9. Evidence requirements for activation-text changes
- 10. Stable severity
- 11. Finding record

## 1. Discovery description

A strong description is a compact routing surface, not a second instruction manual. Check whether it:

- names the owned artifact(s) and action(s), not only generic verbs;
- states the most important adjacent non-goals when they discriminate ownership;
- uses realistic synonyms without keyword stuffing;
- is concise enough to coexist with neighboring skill descriptions;
- avoids promotional/superlative wording whose purpose is to win routing rather than describe ownership;
- keeps detailed workflow, validation, and host behavior in the body/references;
- remains host-neutral unless a host extension is explicitly being reviewed.

Do not reward length. More trigger phrases can increase both context cost and overlap risk.

## 2. Invocation-mode review

Distinguish:

- explicit direct use;
- implicit automatic routing;
- contextual automatic routing under noise/long context/multi-intent.

A description may support all three operationally, but explicit success is not evidence that automatic discovery works. Flag evaluation designs that mix explicit cases into automatic precision/recall as `EVIDENCE_CLAIM`.

## 3. False-positive risk versus confirmed false positive

Use `ACTIVATION_FALSE_POSITIVE_RISK` for static overbreadth, generic verbs, unresolved overlap, missing exclusions, keyword routing, or activation-gaming language.

Use `ACTIVATION_FALSE_POSITIVE` only when FP-001 is satisfied by executed frozen routing evidence.

High-value negative cases are near misses: they share vocabulary/intent with this skill but belong to another owner. Easy unrelated negatives are useful only as abstention controls.

## 4. False-negative risk versus confirmed false negative

Use `ACTIVATION_FALSE_NEGATIVE_RISK` when valid artifacts/actions/synonyms are omitted or wording is overfit to one exact phrase.

Use `ACTIVATION_FALSE_NEGATIVE` only when FN-001 is satisfied by executed frozen routing evidence.

Check coverage for frontmatter descriptions, reusable agent instructions, boundary/handoff/stop text, activation scenarios, and output/evidence contracts.

## 5. Negative semantics and overlap

Classify negative scenarios as:

- `alternative-owner`: another workflow should own the request; record the intended neighboring owner;
- `abstain`: no relevant skill should own the request.

Do not merge these into one negative metric. Apply OVL-001 to alternative-owner cases: artifact -> requested action -> ownership -> split/handoff if decomposable.

## 6. Ambiguity, boundary, and activation gaming

Flag `ACTIVATION_AMBIGUITY` when artifact/action/ownership cannot be inferred reliably.

Flag `BOUNDARY_OWNERSHIP` when the reviewer starts owning package-wide mutation, benchmark authority, implementation, deployment, or unrelated code review.

Flag `ADVERSARIAL_RESILIENCE` when instructions can be induced to:

- remove non-trigger/stop conditions merely to activate more often;
- claim priority over all neighboring skills;
- add promotional or manipulative routing language;
- weaken evaluator/evidence requirements to improve apparent metrics.

## 7. Scenario quality

When routing changes, require coverage across positive, negative, ambiguous, boundary, adversarial, and candidate-visible regression cases. A true blind holdout must be external/evaluator-only.

Use orthogonal dimensions when material:

- language;
- clean/noisy/long context;
- terse/conversational/typo style;
- single versus multi-intent requests;
- explicit/implicit/contextual invocation.

Prefer distinct failure modes over many paraphrases of one easy scenario.

## 8. Evidence comparability

For behavioral comparisons, inspect:

- frozen suite/evaluator identity;
- evaluator visibility/leakage;
- competing catalog hash and size;
- host/model/discovery metadata included in routing fingerprint;
- fixed trial policy;
- baseline/candidate case-set identity;
- execution timestamp/provenance.

A changed material routing fingerprint is a comparison blocker, not a small warning.

## 9. Evidence requirements for activation-text changes

Every recommendation that changes discovery/activation text must record:

- exact original evidence/location;
- TAX-001 defect/risk code;
- contract/rubric criterion;
- smallest supported change;
- affected/new scenario IDs;
- invocation modes affected when relevant;
- validation status/evidence layer.

If these are missing, classify the recommendation as insufficiently evidenced.

## 10. Stable severity

- **blocking:** fabricated evidence, frozen-evaluator corruption, safety/ownership weakening, activation gaming that changes authority, or invalid behavioral comparison presented as measured.
- **high:** likely material FP/FN risk, unresolved ownership overlap, contradictory routing rules, missing comparison identity, or missing stop/evidence gate.
- **medium:** bounded ambiguity or scenario/evidence weakness likely to create inconsistent routing/review.
- **low:** local wording/redundancy with little expected routing impact.
- **note:** observation with no required change.

Severity describes consequence/risk, not reviewer confidence.

## 11. Finding record

For each finding include:

- `id`;
- `defect_code` from TAX-001;
- `severity`;
- `evidence` and exact location when available;
- `contract_clause`;
- `issue`;
- `proposed_change`;
- `rationale`;
- `scenario_ids`;
- `invocation_modes` when relevant;
- `validation_status`: proposed, observed-static, supplied, executed, or blocked;
- `claim_level`: proposed-improvement, structurally-supported, or measured-behavioral-result.
