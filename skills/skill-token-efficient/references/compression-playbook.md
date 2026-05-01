# Compression Playbook

## Goal

Reduce instruction tokens without losing behavior or human comprehension. Cut in order: filler, duplicates, verbose phrasing, weak structure, long examples.

## Levels

- `readable`: terse professional prose; use for `SKILL.md` and activation.
- `dense`: fragments/key-value bullets; use for refs, reports, examples.
- `max-safe`: highest compression after semantic/protected-region checks pass.

Do not make durable docs comedic, intentionally broken, or cryptic.

## High-Yield Moves

- Deduplicate repeated warnings, mode text, gates, output sections.
- Use imperative: `Verify links`, not `You should make sure links are verified`.
- Use key-value: `Limit: 500 chars`, `Scope: target folder only`.
- Prefer lists; keep tables only for compact matrices.
- Move branch detail from `SKILL.md` to `references/` with clear loading triggers.
- Keep shortest behavior-calibrating examples.
- Compress frontmatter last; activation precision beats brevity.
- If validation fails, patch broken spans only; avoid full churn.

## Word Cuts

Remove pleasantries, hedges, filler, throat-clearing, repeated rationale, and weak transitions: `sure`, `happy to`, `might be worth`, `basically`, `actually`, `in order to`, `the purpose of this section is`, `additionally`.

Replace inflated verbs: `utilize -> use`, `implement a solution -> fix`, `perform validation -> validate`.

## Protected Regions

Preserve exactly unless intentionally changed and reported: code blocks, inline code, commands, URLs, links, paths, CLI flags, env vars, schemas, JSON/YAML keys, config names, proper nouns, dates, versions, numeric limits, required output sections, stop labels.

## Safe Removal

Delete only when text is duplicate, scaffold, generic filler, obsolete, or weaker than another rule and does not define scope, safety, evidence, output, validation, tool use, package behavior, or stop logic.

## Risky Compression

Avoid vague boundaries, deleted negatives, merged modes with different mutation rights, undefined acronyms, moved rules without loading links, unauditable output contracts, removed evidence/citation rules, or tool requirements hidden only in examples.

## Readability Floor

A compressed target must still answer: trigger; non-goals; inputs; order; protected regions; validation; output; stop conditions.
