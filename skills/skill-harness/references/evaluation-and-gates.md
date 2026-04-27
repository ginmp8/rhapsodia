# Evaluation and Gates

Use this reference when defining measurable acceptance criteria for a target skill.

## Static Score Dimensions

A practical static audit may score these dimensions from 0 to 100:

- Scope and trigger specificity.
- Required inputs and assumptions.
- Workflow and mode clarity.
- Output contract quality.
- Supporting resource usefulness.
- Validation and gates.
- Scenario and benchmark readiness.
- Context efficiency and maintainability.
- Safety, blocked paths, and evidence discipline.
- Packaging readiness.

Static scores are guidance. Required gates override the score.

## Required Gates

A target skill should not be called ready if any required gate fails:

1. Exactly one `SKILL.md` exists.
2. Frontmatter has `name` and `description`.
3. Description is specific enough to trigger correctly.
4. Expected inputs are clear.
5. Expected outputs are clear.
6. Scope boundaries and stop conditions exist.
7. No unresolved TODO placeholders remain.
8. Referenced resources exist, including concrete template paths under `assets/templates/` when mentioned in workflow instructions.
9. Assets that exist for operational use are integrated by workflow reference, copy/fill instruction, script consumer, or validator coverage.
10. Scripts intended for use have executable or readable commands.
11. Validation criteria are present.
11. Dynamic facts are not hardcoded as permanent truth.
12. Blocked paths and secrets are protected.

## Supporting Resource Interpretation

A supporting-resource warning should guide classification, not automatic deletion. Treat an asset as integrated when it is:

- referenced from `SKILL.md` or a conditionally loaded reference;
- copied or filled by the agent during a declared workflow;
- rendered, updated, or checked by a script;
- validated by a package or structural gate.

Delete or migrate an asset only when evidence shows it is unused scaffolding, duplicated, obsolete, misleading, oversized, or purely explanatory prose better suited to `references/`.

## Behavioral Metrics

Use these only when prompts or results are supplied or executed:

- Activation precision: correct activations divided by actual activations.
- Activation recall: correct activations divided by expected activations.
- Output conformance: conforming outputs divided by executed prompts.
- Criteria coverage: satisfied criteria divided by expected criteria.
- Robustness: passed edge cases divided by edge cases executed.
- Rework rate: outputs requiring manual correction divided by executed prompts.

If not measured, label these metrics `not measured` and propose a scenario suite.

## Saturated Metric Handling

If a benchmark score is already 100/100, keep it as a required gate but add a non-saturated auxiliary metric before claiming improvement. Examples:

- Scenario conformance score.
- Strict checklist coverage.
- Packaging validator pass/fail plus new gate count.
- Reduction in unresolved risks.
- Evidence completeness score.

Do not claim improvement from a saturated score staying the same.

## Gate Severity

Classify gates:

- `blocker`: cannot package or recommend production use.
- `major`: usable only with explicit risk acceptance.
- `minor`: improvement recommended but not blocking.
- `informational`: observation only.

## Decision Language

Use precise recommendations:

- `accept`: all required gates pass and evidence supports readiness.
- `accept with risks`: required gates pass but material risks remain.
- `reject`: one or more blocker gates fail.
- `plan only`: insufficient permission or evidence to modify.
- `needs context`: target-domain claims cannot be safely improved from allowed sources.
