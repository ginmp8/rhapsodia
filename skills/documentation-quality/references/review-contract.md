# Documentation review contract

Contract identity: `documentation-review-v1`

Use this reference for substantive documentation reviews, direct edits that require validation, or durable reports. It stabilizes how evidence, findings, severity, ordering, and completion claims are represented without pretending editorial judgment is deterministic.

## Evidence labels

Use exactly one primary label per finding or validation claim:

| Label | Meaning |
|---|---|
| `measured` | Produced by a command, validator, test, or tool executed in the current run. |
| `observed` | Directly inspected in the current target files or artifacts. |
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

Rules:

- `criterion_id` must come from the active rubric or checklist when one exists.
- `subject` identifies the exact file, section, command, link, or claim.
- `observation` states what is wrong or what improved, without mixing in speculation.
- `evidence` names the inspected source, line/section, or validator diagnostic when available.
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
| `medium` | The documentation remains usable but ambiguity, duplication, missing context, or weak examples create avoidable rework or interpretation risk. |
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

## Rubric identity and mode mapping

Use `references/documentation-quality-rubric.md` as the canonical quality rubric. Record its declared rubric identity in durable reviews.

Apply only criteria relevant to the selected mode. A mode may activate multiple criteria; unused criteria are `not-applicable`, not failed.

## Before/after fairness

For claims that documentation improved:

- keep the same target scope for baseline and candidate;
- keep the same rubric identity and applicable criteria;
- run the same mechanical checks with the same options;
- do not delete difficult sections from scope to improve the result;
- do not rewrite expected outcomes after seeing the candidate;
- distinguish an editorial judgment from a measured mechanical delta.

If the baseline bytes are not preserved, restrict claims to the current candidate state rather than inventing a before/after comparison.

## Evidence layers

Keep these layers separate:

### Mechanical

Examples: local-link existence, heading hierarchy, fence closure, syntax, file presence.

### Semantic and source fidelity

Examples: documented behavior matches an inspected script, command interface, config, or contract.

### Runtime

Examples: documented command was actually executed and its exit/output behavior observed.

### Editorial

Examples: clarity, flow, information architecture, audience fit, example usefulness.

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

- target and audience are resolved;
- selected mode and rubric identity are stable;
- inspected source truth supports the edited technical claims;
- every executed mechanical check passes or unresolved failures are reported explicitly;
- required but unavailable checks are marked `not-run` or `blocked`;
- no blocker or high-severity source-fidelity defect remains hidden;
- final edited bytes are the bytes that were validated;
- remaining editorial judgment is labeled as judgment rather than measured fact.
