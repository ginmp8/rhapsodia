# Compression Playbook

## Priority

1. Preserve semantics, safety, evidence, compatibility, and execution clarity.
2. Remove duplicated warnings/rationale/filler.
3. Shorten inflated wording and examples.
4. Consolidate repeated rules without collapsing distinct duties.
5. Move branch-specific detail to progressively loaded references.
6. Compress activation/frontmatter last.

Token reduction is rejected when it depends on weaker activation, scope, safety, validation, evidence/citation, compatibility, output contract, progressive loading, or readability.

## Levels

- `readable`: default for `SKILL.md`, activation, safety, gates, outputs.
- `dense`: low-risk references, reports, examples.
- `max-safe`: only after all preservation/readability gates pass; never a blanket instruction.

## High-yield moves

- Use imperatives/key-values; keep compact matrices only when they clarify distinctions.
- Merge duplicate negatives but retain negatives preventing false activation, unsafe edits, scope drift, fabricated validation, or lost citations.
- Keep only behavior-calibrating examples.
- Shorten `in order to -> to`, `utilize -> use`, `perform validation -> validate`.
- If validation fails, repair the smallest broken span and rerun the same gate before broader cleanup.
- Do not hide local growth behind net reduction; justify or revert changed files/sections that grow.

## Critical regions

Do not compress critical regions merely because they look verbose. Demonstrate equivalence for commands, URLs, paths, env vars, schemas, flags, proper nouns, versions, numbers, safety rules, validation rules, evidence/citation rules, output requirements, and stop conditions.

## Risk labels

- `low`: wording shortened; no semantic duty moved/removed.
- `medium`: duplicates merged or detail moved; refs/consumers verified.
- `high`: activation, scope, safety, validation, compatibility, output, stop, or evidence/citation wording changed.
- `blocking`: equivalence cannot be demonstrated or a hard gate weakens.

High-risk changes require targeted regression evidence; blocking changes are rejected.
