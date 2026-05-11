# Prompt Rewrite Patterns

Use this reference for `prompt-rewrite` and `instruction-clarity-review`.

## Rewrite Principles

1. **Preserve intent first.** Do not add new capabilities, tools, audiences, or authority that the original prompt did not imply.
2. **Reduce ambiguity before adding detail.** Replace vague words with concrete triggers, constraints, inputs, and outputs.
3. **Keep order executable.** Put prerequisite checks before actions, actions before validation, and validation before final reporting.
4. **Prefer local edits.** Rewrite the smallest section that solves the issue unless the whole prompt structure is broken.
5. **Keep boundaries strong.** A fluent prompt that silently expands scope is worse than a stricter prompt.
6. **Use examples when behavior is hard to infer.** Examples should calibrate activation and output, not restate obvious rules.
7. **Separate analysis from output.** Ask for concise rationale or review findings, not hidden chain-of-thought.
8. **Avoid fake validation.** A prompt may propose scenario tests, but it must not claim measured success without execution evidence.

## Common Rewrites

### Vague trigger to precise trigger

Weak:

> use this skill to improve prompts.

Better:

> use this skill when asked to review, improve, rewrite, or validate prompt text, skill activation descriptions, agent instructions, boundaries, stop conditions, scenarios, or output contracts.

Why it works: the better version names artifacts and actions while avoiding generic writing tasks.

### Broad scope to explicit boundary

Weak:

> use this skill to improve any skill package.

Better:

> use this skill only for prompt, activation, boundary, stop-condition, scenario, and output-contract surfaces. hand off full package hardening, benchmark, consistency repair, or implementation work.

Why it works: the better version protects ownership and prevents over-activation.

### Unclear validation to truthful validation

Weak:

> validate that the prompt works.

Better:

> perform a static review and propose activation, non-activation, ambiguous, and adversarial scenarios. report scenario results as measured only when outputs were actually executed or supplied.

Why it works: the better version separates review from measurement.

### More text to more precise text

Weak:

> add more detailed instructions so the model understands everything.

Better:

> add only the missing constraint, input, stop condition, or output requirement that reduces a specific observed ambiguity.

Why it works: the better version avoids verbosity as a proxy for quality.

## Prompt Review Checklist

Ask these questions before rewriting:

- What is the target role?
- What should trigger the artifact?
- What should not trigger it?
- What are the required inputs?
- What is the allowed mutation scope?
- What output is expected?
- What evidence is required before claiming validation?
- Which handoff is required when the request expands?
- Which examples would catch false positives and false negatives?

## Rewrite Output Pattern

When returning a rewrite, include:

1. `rewritten_text`
2. `changed_because`
3. `preserved_intent`
4. `scope_not_expanded`
5. `negative_scenarios_to_add`
6. `validation_status`
