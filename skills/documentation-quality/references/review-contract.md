# Documentation review contract

Contract identity: `documentation-review-v2`

## At a Glance

- **Purpose:** Stabilize evidence labels, finding shape, severity, ordering, before/after identity, repair limits, and completion claims for documentation-quality work.
- **Load when:** Running a substantive review, validated direct edit, durable report, or any before/after claim.
- **Decision impact:** Controls which evidence words are allowed, how findings are ranked/deduplicated, when comparisons are fair, when repair must stop, and what is required to claim completion.

## Contents

- Evidence labels
- Finding schema
- Severity rules
- Deterministic ordering and deduplication
- Rubric identity and content intent
- Before/after fairness and identity
- Evidence layers
- Repair loop
- Completion gates

## Evidence labels

Use exactly one primary label per finding or validation claim:

| Label | Meaning |
|---|---|
| `measured` | Produced by a command, validator, task run, test, or tool executed in the current run. |
| `observed` | Directly inspected in the current target files/artifacts or concrete reader/task interaction. |
| `supplied` | Provided by the user or another source but not independently executed or verified in the current run. |
| `inferred` | Bounded interpretation derived from inspected evidence; not directly measured. |
| `planned` | Proposed check, scenario, or improvement that was not executed. |
| `blocked` | Required evidence could not be obtained. |

Do not promote `observed`, `supplied`, `inferred`, `planned`, or `blocked` evidence to `measured` for presentation quality.

## Finding schema

Represent each material finding with these fields, explicitly or semantically:

```text
criterion_id
severity
subject
observation
evidence_label
evidence
impact
recommended_change
verification
```

When content purpose changes the criterion, also record `content_kind` at review or finding scope.

Rules:

- `criterion_id` must come from the active rubric or checklist when one exists.
- `subject` identifies the exact file, section, command, link, or claim.
- `observation` states what is wrong or what improved, without mixing in speculation.
- `evidence` names the inspected source, line/section, validator diagnostic, or task evidence when available.
- `impact` explains why the issue matters to reader success, execution, accessibility, or maintenance.
- `recommended_change` is the smallest supported repair.
- `verification` states how the repair was or will be checked.

If the review is lightweight, prose may compress the fields, but the same semantics must remain recoverable.

## Severity rules

Use the first matching rule:

| Severity | Rule |
|---|---|
| `blocker` | The documentation directs a dangerous, destructive, credential-exposing, or nonexistent required action, or asserts completion/validation that is materially unsupported. |
| `high` | The documentation is likely to cause incorrect execution, break a documented workflow, misstate a public contract, or hide a required prerequisite/artifact. |
| `medium` | The documentation remains usable but ambiguity, duplication, missing context, weak examples, poor recovery, or weak findability create avoidable rework or interpretation risk. |
| `low` | The issue is limited to polish, minor consistency, scanability, or non-blocking accessibility/readability. |

Tie-breakers:

1. Prefer demonstrated reader/execution impact over stylistic preference.
2. If impact is uncertain, use the lower defensible severity and record the uncertainty.
3. Do not increase severity because a finding is easy to fix or personally annoying.
4. Multiple low-level symptoms with one root cause should become one root-cause finding when the repair is the same.

## Deterministic ordering and deduplication

Order findings by:

1. severity: `blocker`, `high`, `medium`, `low`;
2. criterion ID;
3. normalized subject path or section name;
4. observation text as a final stable tie-breaker.

Deduplicate findings that have the same criterion, subject, failure condition, and repair. Preserve separate findings when the impact or remediation differs materially.

## Rubric identity and content intent

Use `references/documentation-quality-rubric.md` as the canonical quality rubric and record its declared identity in durable reviews. When document purpose changes the obligation, resolve `content_kind` and use `references/content-type-contracts.md`.

Apply only criteria relevant to the selected mode/content kind. An unused criterion is `not-applicable`, not failed.

## Before/after fairness and identity

For claims that documentation improved:

- preserve baseline bytes or an equivalent immutable identity;
- keep target scope, reader/task definition, applicable criteria, and evaluator/check inputs equivalent across arms;
- keep the same rubric/review-contract identities, or explicitly re-baseline rather than pretending the runs are comparable;
- run the same mechanical checks with the same options;
- freeze/hash evaluator or task-scenario assets when feasible before candidate results are inspected;
- snapshot, pin, or otherwise identify mutable material sources when they can change the conclusion;
- do not delete difficult sections from scope to improve the result;
- do not rewrite expected outcomes after seeing the candidate;
- distinguish editorial judgment from measured mechanical or reader/task delta.

If baseline/evaluator/source identity cannot be preserved, restrict claims to the current candidate state rather than inventing a before/after comparison.

## Evidence layers

Keep these layers separate:

### Mechanical

Examples: local-link existence, heading hierarchy, fence closure, syntax, file presence, missing image-alt warning.

### Semantic and source fidelity

Examples: documented behavior matches an inspected script, command interface, config, or contract.

### Runtime

Examples: documented command was actually executed and its exit/output behavior observed.

### Reader/task outcome

Examples: a defined reader/task scenario was attempted and completion, blockers, navigation effort, or feedback were actually observed/measured/supplied. This layer is optional unless the claim requires it.

### Editorial

Examples: clarity, flow, information architecture, audience fit, terminology consistency, content-purpose fit, example usefulness.

A pass in one layer does not imply a pass in another.

## Repair loop

For objective diagnostics:

1. select one failing diagnostic or root cause;
2. apply the smallest supported edit;
3. rerun the same check;
4. only then run adjacent checks;
5. stop after two consecutive repair rounds that do not reduce the same objective error set.

Do not weaken the checker, lower the criterion, remove semantic content, or relabel missing evidence to obtain a pass.

## Completion gates

A documentation edit is complete only when all applicable conditions hold:

- target, audience/task, and requested outcome are resolved;
- selected mode, content kind when material, review-contract identity, and rubric identity are stable;
- inspected source truth supports the edited technical claims;
- every executed mechanical/native check passes or unresolved failures are reported explicitly;
- required but unavailable checks are `not-run`/`blocked` rather than implied pass;
- reader/task success is claimed only when corresponding evidence exists;
- no blocker or high-severity source-fidelity defect remains hidden;
- final edited bytes are the bytes that were validated;
- no edit occurs after the final passing checks without affected revalidation;
- remaining editorial judgment is labeled as judgment rather than measured fact.
