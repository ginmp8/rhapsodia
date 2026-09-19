# Prompt Rewrite Patterns

Use for `prompt-rewrite` and `instruction-clarity-review`. Apply `references/activation-contract.md` whenever the rewrite can affect routing, scope, evidence, or ownership.

## Rewrite principles

1. Preserve role, intent, safety, and ownership before optimizing wording.
2. Reduce a specific observed ambiguity; do not add text merely for detail.
3. Keep prerequisite checks before actions, actions before validation, and validation before claims.
4. Prefer the smallest local edit that satisfies the identified contract clause.
5. Do not weaken non-trigger boundaries, handoffs, or stop conditions to increase activation.
6. Use examples only when they calibrate a real ambiguity or boundary.
7. Ask for concise rationale/evidence, never hidden chain-of-thought.
8. Do not convert static review into measured validation.

## Activation-text rewrite evidence

For frontmatter descriptions, trigger text, boundaries, handoffs, or stop conditions, record:

1. original text/location;
2. defect/risk code;
3. contract clause;
4. minimal rewritten text;
5. scenarios affected or added;
6. expected effect stated as a hypothesis;
7. validation status.

Use `proposed improvement` until evidence justifies a stronger label.

## Common patterns

### Vague trigger -> artifact + action

Weak: `use this skill to improve prompts.`

Better: `use when asked to review or rewrite existing skill activation descriptions, reusable agent instructions, boundaries, scenarios, or output contracts.`

### Broad ownership -> explicit non-trigger

Weak: `use this skill to improve any skill package.`

Better: `review prompt/activation surfaces only; hand off full package hardening, benchmarking, harness execution, consistency repair, and implementation.`

### Fake validation -> evidence-aware wording

Weak: `validate that the prompt works.`

Better: `perform static review and define frozen scenarios; report behavioral validation only when those scenarios were actually executed with preserved evaluator identity.`

### Overlap -> ownership rule

Weak: `if the request mentions prompts, use this skill.`

Better: `route by requested artifact + action + ownership; use a generic prompt-authoring workflow for new prompt creation and this reviewer for existing activation/boundary surfaces.`
