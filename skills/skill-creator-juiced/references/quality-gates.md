# Quality Gates

Use these gates before claiming a skill is ready.

## Structural Gates

- exactly one root `SKILL.md` for the package;
- frontmatter has `name` and `description`;
- name is lowercase hyphen-case and matches package intent;
- description states what the skill does and when to use it;
- `../agents/openai.yaml` exists for ChatGPT packages;
- referenced local files exist;
- no scaffold markers or unfinished placeholders remain outside template files;
- no caches, old zips, generated reports, or secrets are included.

## Activation Gates

- valid activation examples exist or are planned;
- non-activation examples exist for adjacent domains;
- ambiguous examples define when to ask, proceed, or hand off;
- description is specific enough to avoid false positives and broad enough to avoid common false negatives;
- boundaries and stop conditions are visible.

## Architecture Gates

- one operational role or an explicit router decision explains the package;
- modes share vocabulary, inputs, outputs, evidence, and validation;
- branch-specific detail lives in references, not the control plane;
- every important resource has a declared use;
- scripts are used for deterministic work, not ornamental complexity;
- assets are output materials, not hidden instructions.

## Content Gates

- instructions are imperative and actionable;
- workflow order is clear;
- defaults are preferred over menus;
- examples calibrate style or format;
- output contract is auditable;
- limitations and assumptions are visible;
- no validation, benchmark, or production-readiness claim is unsupported.



## Hypothesis Discovery Gates

- For redesign or quality-upgrade work with multiple possible directions, run `skill-hypothesis-discovery`, apply its checklist, or record why it is not applicable.
- Discovery output is non-mutating: it may recommend `test-hypotheses`, `gather-evidence`, or `no-mutation-recommended`, but it does not accept patches or claim measured improvement.
- Hypotheses used by `skill-improver` must be evidence-backed, bounded, testable, reversible, and protected by evaluator and change-gate checks.
- When discovery says `gather-evidence` or `no-mutation-recommended`, do not force mutation just to satisfy an optimization workflow.

## Change Acceptance Gates

- For existing-skill updates or redesigns, material changes have a `skill-change-gate` result or an explicitly applied checklist.
- Blocking regressions in activation, boundaries, local references, safety, validation, packaging, output contracts, or evidence discipline are repaired before acceptance.
- Material concerns are either fixed, explicitly waived by the user, or recorded as accepted trade-offs with decision impact.
- For net-new skills without before/after evidence, `skill-change-gate` may be advisory or not-applicable, but final delivery still requires local structural and package gates.

## Code and Script Gates

- added or changed scripts have safe command interfaces;
- a deterministic package builder exists for `skill.zip` delivery;
- scripts avoid unsafe shell invocation, path traversal, broad deletes, and untrusted archive extraction;
- scripts have at least a smoke test or syntax check;
- dependencies are minimal and justified;
- failures are reported without pretending success.

## Final Package Gate

A package can be delivered only when:

- local quality gate passes or remaining warnings are explicitly accepted;
- required `skill-hypothesis-discovery` review is run, applied by checklist, or marked not-applicable with rationale when redesign or quality-upgrade work needed hypothesis selection;
- required `skill-change-gate` review passes, is applied by checklist, or is marked advisory/not-applicable with rationale;
- platform/package validator passes;
- `skill.zip` exists at the reported path;
- archive size is below the upload limit;
- final response distinguishes executed validation from planned validation.
