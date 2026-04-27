# Coding Discipline Reference

Use this file only when the task is non-trivial or when the response risks becoming too broad.

## Assumption handling

Good assumption statements are specific and testable:

- "assuming the public method signature must stay unchanged..."
- "assuming this code runs in the existing dependency-injection container..."
- "assuming the failing behavior is limited to null input..."

Avoid vague disclaimers such as "there may be edge cases" unless the edge case is named.

## Simplicity tests

Before proposing a design, ask:

1. Can the user solve the problem by changing fewer files?
2. Is the new abstraction used more than once now?
3. Did the user request configurability, or am I adding it defensively?
4. Is there an existing project pattern that already solves this?
5. Would a senior reviewer call the change disproportionate?
6. Can a narrower validation check prove the change without a broad rewrite?

If the answer indicates overengineering, propose the smaller option first.

## Plan threshold

Skip a formal plan when the diff can be described in one sentence and touches one obvious artifact. Use a brief plan when the work is multi-file, has unknown validation commands, affects public behavior, or involves security, reliability, performance, data migration, or infrastructure.

A useful plan is not a brainstorming list. Each step must name the artifact it touches and the check that proves it.

## Surgical edit rules

- Preserve public APIs unless the user requested an API change.
- Do not reformat unrelated code.
- Do not rename unrelated symbols.
- Do not replace libraries or frameworks as part of a local fix.
- Do not remove pre-existing dead code unless explicitly asked.
- Mention unrelated issues separately instead of patching them opportunistically.

## Verification ladder

Prefer the strongest feasible check, in this order:

1. targeted failing test reproduced and fixed;
2. existing relevant test suite;
3. build/type/lint check;
4. local runtime smoke test;
5. static reasoning with exact files and functions named.

When none can be run, label verification as not executed and provide the command or observation that would verify it.

## Review severity scale

- Critical: likely security issue, data loss, financial/legal impact, or production outage.
- High: likely functional bug, broken compatibility, or severe operational risk.
- Medium: maintainability, performance, observability, or reliability concern with plausible impact.
- Low: style, naming, readability, or small cleanup that should not distract from the main change.

Do not inflate severity to make a review appear more useful.
