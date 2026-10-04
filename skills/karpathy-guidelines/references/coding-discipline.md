# Coding Discipline Reference

Use this file only when the task is non-trivial or risks becoming broader than the user's request.

## Assumption handling

State only assumptions that could change correctness, scope, or validation. Make them specific and falsifiable, such as preserving a public signature, using the existing dependency-injection container, or limiting the reported failure to a named input class.

Avoid vague disclaimers such as "there may be edge cases" unless the edge case is identified.

## Simplicity tests

Before proposing a design, ask:

1. Can the problem be solved by changing fewer artifacts?
2. Is a new abstraction used more than once now?
3. Did the user request configurability, or is it being added defensively?
4. Does the repository already contain a pattern that solves this?
5. Is the change reversible and proportional to the demonstrated problem?
6. Can a narrower oracle prove the requested behavior without a broad rewrite?

If the answers indicate overengineering, choose the smaller option first.

## Semantic change contract

For a non-trivial modification, bound semantics before editing:

- **requested delta** — what observable behavior may change;
- **preserved invariants** — public contracts, valid-input behavior, authorization, persistence, ordering, compatibility, or other behavior that must remain unchanged;
- **affected surface** — the smallest files/modules expected to implement the delta;
- **oracle** — what evidence can falsify the requested delta or an invariant break.

Do not turn this into ceremony for an obvious one-line local edit. The purpose is to prevent a patch from solving the visible test while silently changing unrelated behavior.

## Plan threshold

Skip a formal plan when the change can be described in one sentence, touches one obvious artifact, and has a clear validation command. Use a brief plan when work is multi-file, validation is unknown, public behavior changes, or security, reliability, performance, data, migration, infrastructure, or destructive actions are involved.

Each plan step should name the affected artifact or behavior and the check that proves it.

## Escalation ladder

Use the least process that can safely answer the task:

1. direct local change + focused validation;
2. explore -> change -> verify when nearby context is needed;
3. short explicit plan for multi-file, risky, or uncertain work;
4. extra tests, independent review, or multi-step/orchestrated execution only when the failure model, blast radius, or explicit requirement justifies it.

Do not add process merely because the host can support it. If the simple path is sufficient, keep it simple.

## Surgical edit rules

- Preserve public APIs unless the request requires an API change.
- Do not reformat or rename unrelated code.
- Do not replace frameworks or libraries as part of a local fix.
- Do not remove pre-existing dead or odd-looking code unless removal is in scope and its role is understood.
- Mention unrelated issues separately instead of patching them opportunistically.

## Repository archaeology gate

When code appears redundant, defensive, oddly shaped, or unnecessarily complex and removal would change behavior:

1. inspect callers/references;
2. inspect relevant tests and configuration;
3. inspect nearby comments/docs and current project patterns;
4. if the reason is still unexplained and history is available, inspect the relevant commit/blame/history before deleting or collapsing the behavior.

History is conditional evidence, not a default context dump. Stop once the constraint is explained well enough to make the bounded decision.

## Validation selection

Do not use a universal test ladder as a substitute for the failure model. Select the narrowest relevant oracle first, then broaden only when risk or contracts require it. Use `validation-and-stop-conditions.md` for the failure-model matrix and action-risk rules.

A generic build or passing suite may be useful regression evidence but does not prove behavior it never exercised.

## Review severity scale

- Critical: likely security issue, data loss, financial/legal impact, or production outage.
- High: likely functional bug, broken compatibility, or severe operational risk.
- Medium: maintainability, performance, observability, or reliability concern with plausible impact.
- Low: style, naming, readability, or small cleanup that should not distract from the main change.

Do not inflate severity to make a review appear more useful. Style preference is not a defect unless an explicit contract makes it objective.

## Control-layer note

Simplicity tests, escalation defaults, and tool/validation ordering are heuristics unless a project contract makes a step mandatory. Truthful evidence reporting and hard safety/contract gates are non-negotiable. When competent engineers can legitimately disagree after objective constraints are satisfied, use `decision-variance-model.md` rather than forcing one deterministic answer.
