# Mode and Research Policy

Use this reference when deciding what evidence sources may be used to improve the target skill.

## Auto Mode

Use `auto` when the user gives a target skill and expects the skill-harness to determine how to improve it.

Allowed sources:

- Target skill contents.
- User-provided files that are part of the target request.
- Public web research for external frameworks, best practices, current tool behavior, or primary documentation.
- Internal/company sources only when the user's request is clearly work-related and the available environment provides permission-aware access.
- Existing benchmark, hardening, or evaluation reports supplied by the user.

Behavior:

1. Inspect the target first.
2. Derive research questions from concrete weaknesses.
3. Prefer primary sources for technical claims.
4. Use current sources for volatile facts.
5. Cite or record sources in the final evidence section.

## Context Mode

Use `context` when the user says to use only supplied context or when the task is a controlled rewrite based on references they provided.

Allowed sources:

- Target skill contents.
- Context explicitly provided in the conversation.
- Files or links explicitly provided as reference context, if the environment can open them.

Forbidden in context mode unless the user changes mode:

- Public web research.
- Internal knowledge search not included by the user.
- Adding domain rules not present in target or context.

Behavior:

1. Extract constraints, examples, claims, and acceptance criteria from the context.
2. Improve the target only where the context supports the change.
3. State missing context as a limitation instead of guessing.

## Full Mode

Use `full` when the user provides context and also wants broader research.

Allowed sources:

- Everything allowed in `context`.
- Additional research derived from both the target and supplied context.
- Primary docs, current best practices, comparable mature skills, and public references.

Behavior:

1. Extract the user's context first.
2. Inspect the target.
3. Generate research questions that extend, verify, or challenge the context.
4. Resolve conflicts explicitly: primary/current sources override older or secondary sources unless the user provided a binding constraint.
5. Keep user-provided constraints visible in the plan.

## Conflict Handling

When sources disagree:

1. Prefer user-declared constraints for desired behavior.
2. Prefer target repository truth for implementation facts.
3. Prefer primary/current sources for external technical facts.
4. Prefer measured harness results over expectations.
5. Record unresolved conflicts and do not bake them into the target as fact.

## Research Output Contract

Record:

- Research questions asked.
- Sources used.
- Key claims adopted.
- Claims rejected or not used.
- Constraints derived from context.
- Remaining unknowns.
