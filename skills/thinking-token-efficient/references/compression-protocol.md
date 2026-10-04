# Compression Protocol

## Goal

Spend less private reasoning effort by removing non-load-bearing work, not by deleting correctness checks. Compression is a representation/search discipline, not a substitute for reasoning-effort selection. Use `references/adaptive-effort-policy.md` to decide how much reasoning is justified.

## Orthogonality rule

Reasoning effort and representation are orthogonal:

- `direct|light|standard|deep` controls how much reasoning work is justified;
- `readable|dense|max-safe` controls how compactly private state is represented.

Do not infer low effort from `dense` or `max-safe`, and do not expand effort merely because the representation is `readable`. Risk, uncertainty, evidence, and validation decide effort; auditability and stability decide representation.

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

Use terse complete clauses. Default for ambiguity, high stakes, external evidence, citations, code changes, security, destructive actions, failed attempts, or externally auditable decisions.

### dense

Use compact labels/fragments after the task, constraints, and checks are stable. Good for repeated comparisons and evidence bookkeeping.

### max-safe

Use a tiny ledger only for low-risk substeps with stable success criteria and no material uncertainty. Escalate immediately if safety, citations, external facts, identity, code correctness, or user-impact risk appears.

## What to cut

Remove greetings, self-talk, repeated restatement, obvious transitions, discarded options, duplicate evidence, and speculative branches that cannot change the answer.

Close a resolved branch. Reopen it only when new evidence, a failed gate, or a changed constraint can alter the decision.

## What to preserve

Preserve goal, constraints, user language, requested format, evidence/citation duties, freshness, safety boundaries, validation status, exact commands, file paths, line ranges, APIs, schemas, flags, versions, dates, numeric limits, compatibility, and acceptance criteria when material.

## Tool-call and branch efficiency

Prefer the smallest source/tool set that can establish the answer. Before another read, search, tool, subagent, or branch, ask whether its plausible result could change the decision or satisfy an unmet obligation. If not, stop that branch.

Batch independent lookups only when doing so preserves source identity and error visibility. Do not avoid a necessary read, test, search, or validator merely to reduce tool count.

## Anti-patterns

- novelty speech, broken grammar, or foreign-language obfuscation;
- unexplained acronyms or shorthand;
- removing caveats that affect correctness;
- treating a planned check as executed evidence;
- broad repository/file sweeps without a named information need;
- repeatedly reconsidering a resolved branch without new evidence;
- forcing lower reasoning effort because the private representation is compressed;
- claiming hidden token savings from static text size alone.
