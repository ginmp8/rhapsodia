# Compression Protocol

## Goal

Spend fewer private reasoning tokens without lowering final-answer correctness. Compression is a search strategy, not a style gimmick.

## Minimal ledger

Use this shape only when it helps:

```text
goal: user outcome
facts: only load-bearing facts
unknowns: blockers or assumptions
path: next 1-3 reasoning/tool steps
checks: evidence, citations, commands, safety gates
answer: final stance or patch direction
```

Delete fields as they become unnecessary. Keep only facts that change the answer.

## Level rules

### readable

Use complete terse clauses. Best for first pass, high ambiguity, high stakes, external sources, citations, or code decisions.

### dense

Use short labels and fragments after the task is bounded. Good for repeated checks, comparing options, and summarizing inspected files.

### max-safe

Use tiny ledgers for low-risk substeps. Allowed only when success criteria and facts are stable. Escalate immediately on uncertainty, citations, safety, or user-impact risk.

## What to cut

Remove greetings, self-talk, repeated task restatements, obvious transitions, discarded options, low-value rationale, and verbose confidence wording. Prefer key-value lists over paragraphs in private notes.

## What to preserve

Keep task goal, constraints, user language, required format, evidence/citation duties, source freshness, safety boundaries, validation status, exact commands, file paths, line ranges, APIs, versions, dates, numeric limits, and acceptance criteria.

## Anti-patterns

- Novelty speech that makes reasoning harder to inspect.
- Random language switching or foreign-language obfuscation.
- Acronyms that are not obvious from local context.
- Removing caveats that affect correctness.
- Treating a planned check as executed evidence.
- Compressing activation, safety, citation, or validation rules below readability.

## Caveman-style boundary

The useful lesson from caveman-style compression is omission of filler and redundant syntax. Do not copy comedy voice, broken grammar, or novelty modes. Prefer terse professional notes and clear final answers.
