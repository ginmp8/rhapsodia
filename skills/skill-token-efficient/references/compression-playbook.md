# Compression Playbook

## Goal

Reduce tokens without losing behavior or readable execution. Cut filler, duplicates, inflated phrasing, weak structure, then long examples.

## Levels

- `readable`: terse prose for `SKILL.md` and activation.
- `dense`: fragments/key-values for refs, reports, examples.
- `max-safe`: highest compression only after semantic/protected checks pass.

Do not make durable docs comedic, broken, or cryptic.

## High-Yield Moves

- Deduplicate warnings, mode text, gates, outputs.
- Use imperatives and key-values: `Verify links`, `Limit: 500 chars`.
- Prefer lists; keep compact matrices.
- Move branch detail from `SKILL.md` to refs with loading triggers.
- Keep only behavior-calibrating examples.
- Compress frontmatter last; activation precision beats brevity.
- If validation fails, patch broken spans only.
- Check changed files/sections; never hide local verbosity behind net reduction.

## Word Cuts

Remove pleasantries, hedges, filler, throat-clearing, repeated rationale, and weak transitions such as `sure`, `happy to`, `might be worth`, `basically`, `actually`, `in order to`, `additionally`.

Replace inflated verbs: `utilize -> use`, `implement a solution -> fix`, `perform validation -> validate`.

## Protected Regions

Preserve unless intentionally changed and reported: code blocks, inline code, commands, URLs, links, paths, CLI flags, env vars, schemas, JSON/YAML keys, config names, proper nouns, dates, versions, numeric limits, required output sections, stop labels, and paired/slash terms that encode separate duties.

Examples: `evidence/citation`, `audit/validate`, `validate/package`, `source/path`, `file/line`. Keep both sides unless the replacement visibly preserves both duties.

## Safe Removal

Delete only duplicate, scaffold, generic, obsolete, or weaker text that does not define scope, safety, evidence, citation/reference traceability, output, validation, tool use, package behavior, or stop logic. If a changed section grows, compress it, justify the semantic gain, or reject it.

## Risky Compression

Avoid vague boundaries, deleted negatives, merged modes with different mutation rights, undefined acronyms, moved rules without loading links, unauditable outputs, removed evidence/citation rules, collapsed source/path/line duties, or tool requirements hidden only in examples.

## Readability Floor

A compressed target still answers: trigger; non-goals; inputs; order; protected regions; evidence and citation/reference duties; validation; output; stop conditions.
