# Compression Protocol

## Goal

Spend less private reasoning effort by removing non-load-bearing work, not by deleting correctness checks. Compression is a search/representation strategy, not a style gimmick.

## Minimal ledger

Use this only when it reduces work:

```text
goal: user outcome
facts: load-bearing facts only
unknowns: blockers or assumptions
path: next 1-3 reasoning/tool steps
checks: evidence, citations, commands, safety gates
answer: final stance or patch direction
```

Delete fields as they stop affecting the decision. Do not preserve narrative history of resolved branches.

## Level rules

### readable

Use terse complete clauses. Default for ambiguity, high stakes, external evidence, citations, code changes, security, destructive actions, or failed attempts.

### dense

Use compact labels/fragments after the task, constraints, and checks are stable. Good for repeated comparisons and evidence bookkeeping.

### max-safe

Use a tiny ledger only for low-risk substeps with stable success criteria and no material uncertainty. Escalate immediately if safety, citations, external facts, identity, code correctness, or user-impact risk appears.

## What to cut

Remove greetings, self-talk, repeated restatement, obvious transitions, discarded options, low-value rationale, duplicate evidence, and speculative branches that cannot change the answer.

## What to preserve

Preserve goal, constraints, user language, requested format, evidence/citation duties, freshness, safety boundaries, validation status, exact commands, file paths, line ranges, APIs, schemas, flags, versions, dates, numeric limits, and acceptance criteria when material.

## Tool-call efficiency

Prefer the smallest source/tool set that can establish the answer. Batch independent lookups only when doing so preserves source identity and error visibility. Do not avoid a necessary read, test, search, or validator merely to reduce tool count.

## Anti-patterns

- novelty speech, broken grammar, or foreign-language obfuscation;
- unexplained acronyms or shorthand;
- removing caveats that affect correctness;
- treating a planned check as executed evidence;
- broad repository/file sweeps without a named information need;
- repeatedly reconsidering a resolved branch without new evidence;
- claiming hidden token savings from static text size alone.
