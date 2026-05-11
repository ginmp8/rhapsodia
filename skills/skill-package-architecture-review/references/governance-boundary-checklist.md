# Governance Boundary Checklist

Use this reference for `governance-boundary-review` and for package architecture questions involving ownership, authority, handoffs, stop conditions, or overlap with adjacent skills.

## Ownership questions

- Who owns the package behavior: reviewer, implementer, benchmarker, hardener, harness runner, domain expert, or router?
- Does `SKILL.md` preserve that role across modes?
- Are any resources written from a different role than the package claims?
- Are templates and reports aligned with the declared owner?
- Are examples and evals testing the right skill boundary?

## Authority questions

- Can the skill edit target files, or only review them?
- Can it package artifacts, or only recommend package changes?
- Can it run scripts, or only inspect structure?
- Can it score behavior, or only identify required evidence?
- Can it rewrite target-domain rules, or only flag that domain evidence is missing?

Authority must be explicit. When authority is absent, default to review-only behavior.

## Adjacent-skill boundaries

Use architecture review for structural and dependency judgment. Hand off when the user asks for:

- internal contradiction repair or bounded fixes: consistency repair;
- mature package hardening and package-level improvements: hardening;
- harness design, scenario gates, and evidence scaffolding: harness;
- hypothesis-driven before/after optimization: improver;
- standardized maturity score or comparison: benchmark;
- repository code implementation or refactoring: code-oriented skills;
- secret handling audit: secure review.

Do not replace these workflows. Name the handoff, preserve evidence, and avoid doing the adjacent skill's full job unless explicitly requested with the relevant skill active.

## Handoff contract

A good handoff includes:

1. Trigger: why this review is not the owner of the next action.
2. Evidence: files, findings, and commands already inspected.
3. Targeted ask: what the next skill should do.
4. Constraints: blocked paths, no domain rewrite, preserve useful resources, no fabricated metrics.
5. Acceptance gate: what would prove the next action succeeded.

## Stop conditions

Stop before recommending architectural mutation when:

- evidence does not show low cohesion, ownership conflict, activation ambiguity, maintenance difficulty, or validation burden;
- the target package has hidden consumers that cannot be inspected;
- the recommendation would remove security, validation, audit, or governance controls;
- the package claims measured quality but evidence is missing;
- the requested change crosses from package architecture into target-domain design.

## Governance risk signs

- Modes use different authority levels without saying so.
- A review-only skill includes scripts that mutate the target without safeguards.
- A benchmark-like report claims measured scenario results from planned prompts.
- Handoff rules are absent where adjacent skills clearly own the next step.
- Stop conditions are vague and allow domain rewrites by inference.
- User-facing metadata promises implementation while `SKILL.md` promises review.
