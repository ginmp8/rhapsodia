# Evaluator Contract

Use when designing validation for a hardening run or a dedicated evaluator for another skill.

## Layers

1. Static structure: required files, frontmatter, layout, references, scripts, templates, placeholders.
2. Package semantics: scope boundary, modes, workflow, output contract, gates, stop conditions.
3. Resource integration: each useful resource is referenced, lazy-loaded, executable, copied, filled, script-consumed, or validated.
4. Behavioral evidence: activation, negative, ambiguous, edge prompts, expected outputs, measured results.

## Required fail gates

Fail when any applies:

- missing/invalid `SKILL.md`, `name`, or `description` frontmatter;
- description too generic for reliable activation;
- unclear output contract;
- no validation or finalization rule;
- broken references;
- scaffold placeholders remain;
- operational template removed or migrated only because no script consumes it, without classification evidence;
- scripts added by the run were not run or explicitly reported untested;
- benchmark fixtures changed during improvement;
- packaging fails.

## Score bands

- `0-49`: weak package; prompt or incomplete scaffold.
- `50-69`: usable but brittle; likely `SKILL.md`-only or weak integration.
- `70-84`: good workflow with validation/resource gaps.
- `85-94`: hardened; mature structure, integrated resources, repeatable validation.
- `95-100`: reference-grade; strong behavioral evidence and deterministic tooling.

## Saturated audits

If a benchmark is already `100/100`, keep it as a gate and add a non-saturated auxiliary metric before edits: resource-integration score, script test pass rate, activation scenario pass rate, package gate count, placeholder/missing-reference count, or user-reported rework rate. Do not claim improvement merely because a saturated score stayed unchanged.

## Report minimums

Include target path/name, inventory, gate status, score by layer, resource map, top risks, prioritized improvements, commands, and measured-versus-proposed evidence.

## Package-delivery auxiliary gates

For saturated static audits, require package gates before claiming improvement: deterministic builder ran; archive validator checks readability, single root, minimal frontmatter, references, exclusions, scaffold markers; scenario examples cover activation, non-activation, ambiguous, and edge prompts; package status is recorded when `skill.zip` is supplied; final report separates measured evidence from planned behavioral coverage.
