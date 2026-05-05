# Discovery Method

Use this method to generate hypotheses from evidence, not from random mutation.

## Evidence signals

Inspect available evidence and classify signals by area:

- `activation`: vague trigger, false positive risk, false negative risk, missing non-activation boundaries.
- `ambiguity`: unclear ask/proceed/handoff rules, adjacent-skill conflicts, missing examples.
- `output`: missing output contract, inconsistent sections, artifact naming ambiguity, evidence labels missing.
- `architecture`: bloated control plane, weak mode boundaries, poor progressive loading, resources not consumed.
- `consistency`: contradictions across `SKILL.md`, references, scripts, examples, evals, templates, or reports.
- `documentation`: unclear references, stale examples, unverified claims, missing script usage notes.
- `validation`: missing validators, failed gates, unvalidated scripts, no package checks, weak scenario schemas.
- `security`: broad authority, unsafe shell/archive handling, sensitive logging, unclear blocked paths.
- `packaging`: old zips, generated reports, caches, symlinks, package scope ambiguity.
- `token`: repeated rules, verbose examples, branch details in `SKILL.md`, duplicated reference sections.
- `behavioral`: missing executed prompts, saturated scores, absent holdouts, weak regression coverage.

## Broad discovery pass

Generate 5-10 candidate hypotheses. Each hypothesis must have:

1. observed evidence or missing-evidence signal;
2. mechanism explaining why the change could help;
3. expected effect;
4. validation method;
5. risk and rollback/gate notes;
6. decision on whether to test now, defer, reject, or gather evidence first.

## Deep discovery pass

Use when full optimization or saturated metrics require stronger planning.

1. Generate a broad list.
2. Critique for duplicates, vague mechanisms, missing validators, and high-risk mutations.
3. Combine overlapping ideas.
4. Add missing classes such as activation, validation, security, token cost, and package gates.
5. Return top 5-8 after dedupe, not a raw pile of 20 ideas.

## No-mutation outcome

Return `no-mutation-recommended` when:

- all current evidence is strong and no safe, measurable hypothesis is visible;
- the next best work is adding scenario or benchmark evidence;
- expected benefit is lower than regression risk;
- requested changes are cosmetic without a clear gate;
- evaluator scores are saturated and no auxiliary metric exists.

## Anti-patterns

Reject these hypothesis patterns:

- random renames, section moves, or rewrites without evidence;
- changing tests, expected outputs, scoring weights, or benchmark baselines to make a result pass;
- deleting examples/resources only because they look unused without checking consumers;
- optimizing token count before activation, safety, validation, and output contracts are stable;
- suggesting broad multi-file rewrites when one bounded candidate would answer the question;
- claiming measured improvement from planned or inferred evidence.
