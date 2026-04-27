# Evaluator Contract

Use this reference when designing validation for a hardening run or creating a dedicated evaluator for another skill.

## Evaluation layers

A strong hardening evaluator has four layers:

1. Static structure: required files, frontmatter, directory layout, references, scripts, templates, placeholders.
2. Package semantics: scope boundary, mode selection, workflow, output contract, validation gates, stop conditions.
3. Resource integration: every useful resource is referenced, conditionally loaded, executable, copied, filled, script-consumed, or validated.
4. Behavioral evidence: activation prompts, negative prompts, ambiguous prompts, edge cases, expected outputs, and measured results.

## Required gates

Fail the hardening gate when any of these are true:

- missing or invalid `SKILL.md`;
- missing `name` or `description` frontmatter;
- description is too generic to trigger reliably;
- expected output is unclear;
- no validation or finalization rule exists;
- referenced files are missing;
- scaffolding placeholders remain;
- an existing operational template is removed or migrated solely because no script consumes it, without classification evidence;
- scripts added by the hardening run were not run or explicitly reported as untested;
- benchmark fixtures changed during an improvement run;
- packaging fails.

## Suggested score bands

- `0-49`: weak package; mostly a prompt or incomplete scaffold.
- `50-69`: usable but brittle; likely `SKILL.md`-only or resource integration is weak.
- `70-84`: good skill; clear workflow but some validation or resource maturity gaps remain.
- `85-94`: hardened skill; mature structure, integrated resources, and repeatable validation.
- `95-100`: reference-grade skill; strong behavioral evidence and deterministic tooling.

## Saturated benchmark handling

If `skill-benchmark` is already `100/100`, keep it as a required gate and add a non-saturated auxiliary metric before editing. Useful auxiliary metrics:

- resource integration score, with deletion-only fixes separated from true integration improvements;
- script test pass rate;
- activation scenario pass rate;
- package validation gate count;
- placeholder and missing-reference count;
- user-reported rework rate.

Do not claim improvement because a saturated score stayed unchanged.

## Report minimums

A hardening report should include:

- target skill path and name;
- inventory summary;
- gate status;
- score by layer;
- resource map;
- top risks;
- prioritized improvements;
- commands executed;
- evidence that was measured versus only proposed.

## Package delivery auxiliary gates

When the static audit score is already saturated, add package-delivery gates before claiming improvement:

- deterministic package builder exists and has been run;
- package validator checks archive readability, single skill root, minimal frontmatter, referenced paths, exclusions, and residual scaffold markers;
- scenario examples exist for activation, non-activation, ambiguous, and edge-case prompts;
- validator output records package status when a `skill.zip` path is supplied;
- final report separates measured evidence from proposed or planned behavioral coverage.

These gates provide a non-saturated signal without changing benchmark fixtures or inventing behavioral measurements.
