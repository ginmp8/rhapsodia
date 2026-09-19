# Activation Review Rubric

Use with `references/activation-contract.md`. The contract defines semantics; this rubric defines how to inspect and report evidence.

## 1. Activation description

Check whether the description alone identifies:

- target artifacts and requested actions covered by ACT-001;
- adjacent work excluded by NTR-001;
- enough wording variety to avoid obvious FN risk without becoming generic;
- no dependency on proprietary host invocation syntax;
- no claims of measured validation that require EVD-001/CLM-001 evidence.

A strong description is specific enough to route before loading the body, but it does not try to encode the entire workflow.

## 2. False-positive risk vs confirmed false positive

Use `ACTIVATION_FALSE_POSITIVE_RISK` when static text is overly broad, examples conflict, exclusions are missing, or overlap is unresolved.

Use `ACTIVATION_FALSE_POSITIVE` only when FP-001 is satisfied by executed frozen routing evidence.

Static indicators of FP risk include:

- generic verbs such as `improve`, `review`, or `validate` without naming the artifact;
- owning generic writing, code review, benchmark, hardening, harness, or implementation work;
- using keywords as the routing rule instead of artifact + action + ownership;
- missing split-handoff behavior for mixed-scope requests.

## 3. False-negative risk vs confirmed false negative

Use `ACTIVATION_FALSE_NEGATIVE_RISK` when valid artifacts/actions/synonyms are omitted or wording is overfit to one exact phrase.

Use `ACTIVATION_FALSE_NEGATIVE` only when FN-001 is satisfied by executed frozen routing evidence.

Common static omissions include:

- frontmatter `description`, activation/trigger/when-to-use wording;
- non-trigger boundaries, handoffs, overlap, stop conditions;
- reusable agent instructions, chat modes, output contracts;
- positive/negative/ambiguous/boundary/adversarial scenarios.

## 4. Ambiguity and boundary review

Use AMB-001 and BND-001.

Flag `ACTIVATION_AMBIGUITY` when the artifact or ownership cannot be inferred reliably from supplied context. Do not convert ambiguity into a forced yes/no activation judgment solely for scoring convenience.

Flag `BOUNDARY_OWNERSHIP` when a reviewer starts owning package-wide mutation, benchmark authority, code implementation, or other responsibilities outside its contract.

## 5. Overlap review

Apply OVL-001 in order:

1. identify artifact;
2. identify requested action;
3. compare ownership contracts;
4. prefer the narrower legitimate owner;
5. split mixed requests when possible;
6. record unresolved overlap explicitly instead of silently choosing by keyword count.

Overlap is not automatically a defect: two workflows may inspect the same artifact for different actions. The defect is ambiguous or duplicated ownership for the same action.

## 6. Evidence requirements for frontmatter/description changes

A proposed activation-text change is reviewable only when the report records:

- exact original evidence/location;
- defect/risk code from TAX-001;
- contract clause or rubric criterion;
- minimal proposed change;
- affected frozen or proposed scenario IDs;
- validation status and evidence layer.

If the report lacks these, classify the recommendation as insufficiently evidenced rather than accepting it because the rewrite sounds better.

## 7. Stable severity

- **blocking:** would fabricate evidence, remove required safety/ownership boundary, corrupt frozen evaluator integrity, or cause uncontrolled ownership expansion.
- **high:** likely material FP/FN risk, unresolved ownership overlap, contradictory routing rules, or missing stop/evidence gate.
- **medium:** local ambiguity likely to produce inconsistent review/routing but bounded to one surface.
- **low:** non-blocking wording/redundancy with little expected routing effect.
- **note:** observation with no required change.

Severity describes consequence/risk, not reviewer confidence.

## 8. Finding record

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
- `validation_status`: proposed, observed-static, supplied, executed, or blocked;
- `claim_level`: proposed-improvement, structurally-supported, or measured-behavioral-result.
