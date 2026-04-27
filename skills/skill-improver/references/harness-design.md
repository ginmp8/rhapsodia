# Skill Improver Harness Design

Use this reference when a run asks for a complete improvement harness for `skill-improver` or when the static score is saturated and a second, non-saturated contract is required before claiming improvement.

## Decision supported

After this harness runs, decide whether the target package can be used or packaged for controlled skill-improvement work with acceptable risk. The decision must distinguish: accept, accept with risks, reject, validation-only, and plan-only.

## Skill behavior under test

The harness evaluates whether the skill reliably guides a user or agent through:

1. inspecting a target skill before mutation;
2. preparing and freezing a benchmark or auxiliary evaluator;
3. measuring a baseline;
4. selecting one falsifiable hypothesis at a time;
5. applying only allowed edits;
6. accepting, rejecting, or reverting candidates from measured evidence;
7. packaging or installing only after validation;
8. reporting commands, evidence, blocked paths, and residual risks truthfully.

## Source basis

### Supplied context

The supplied autoresearch repository establishes the primary pattern used here: a small mutable surface, fixed evaluation budget, baseline first, one measurable metric, accept or discard each experiment, and log outcomes. For skill improvement, the mutable surface is the target skill folder, the metric is the frozen evaluator score or scenario conformance, and the accept/discard decision is the patch decision.

### Target package

The target package already defines benchmark freezing, blocked paths, saturated metric handling, self-improvement safeguards, a bundled runner, and a starter static scorer. This harness makes those rules testable through scenarios and a deterministic package validator.

### Additional research

Use additional external research only when a concrete gap remains after reading the target package and supplied context, such as a changed command interface for an external evaluator. Record the source and keep researched recommendations separate from the supplied-context rules.

## Scope boundary

In scope:

- `SKILL.md` activation, workflow, modes, stop conditions, and output contracts;
- `references/` evaluation, benchmark, hypothesis, and harness policies;
- `scripts/` deterministic runners and validators;
- `evals/` planned or measured scenario suites;
- canonical report guidance in `references/report-template.md` plus executable templates in `assets/templates/` consumed by `scripts/skill_improver_loop.py`;
- packaging exclusions, validation evidence, and resource-integration checks that distinguish script-consumed templates, workflow-filled templates, references, examples, fixtures, and unused scaffolding.

Out of scope unless explicitly requested:

- modifying locked evaluator fixtures or expected outputs during an improvement iteration;
- editing secrets, caches, package artifacts, generated evidence reports, or `.git`;
- claiming scenario pass rates without executed prompt outputs;
- running unbounded autonomous loops outside a disposable sandbox.

## Scenario suite

Use `evals/skill-improver-scenarios.json` as the frozen planned suite. A measured suite may be derived from it, but the measured results must be locked before candidate edits. Required categories are:

- `should_activate`: prompts that clearly require hypothesis-driven skill improvement;
- `should_not_activate`: generic coding, writing, or product questions outside skill-improvement scope;
- `ambiguous`: prompts that require benchmark/mode/scope clarification or conservative defaults;
- `edge_case`: missing target path, dirty git state, saturated metric, blocked path edits, or unsafe sandbox modes;
- `regression`: known failure modes such as changing the evaluator mid-run or claiming improvement from a saturated score.

## Evaluators

Structural evaluator:

- skill-harness inventory and audit for package structure, references, placeholders, scenarios, validation, and maintainability.

Activation evaluator:

- scenario review against the planned or measured suite; calculate precision and recall only when actual activation decisions are captured.

Output-conformance evaluator:

- check final reports for baseline, final score, evaluator hash, accepted/rejected hypotheses, files changed, gates, package result, and residual risks.

Safety and scope evaluator:

- verify blocked paths were not modified, mutation scope was respected, sandbox mode was stated, and unsupported persistence claims are absent.

Packaging evaluator:

- run `scripts/validate_skill_improver_package.py` and verify the package archive excludes evidence, caches, secrets, and transient state;
- verify `assets/templates/improvement-run-report.md.template` and `assets/templates/patch-decision-record.md.template` are consumed by `scripts/skill_improver_loop.py`; for other target skills, verify templates are consumed by a script, explicitly referenced by a workflow, copied or filled by the agent, or validated by a gate before treating them as integrated.

## Metrics

- Activation precision: measured correct activations divided by actual activations; mark not measured until outputs exist.
- Activation recall: measured correct activations divided by expected activations; mark not measured until outputs exist.
- Output conformance: required report sections satisfied divided by required sections.
- Criteria coverage: required harness criteria satisfied divided by required criteria.
- Robustness: passed edge and regression scenarios divided by executed edge and regression scenarios.
- Rework risk: qualitative low, medium, or high based on failed gates, unmeasured behavior, and manual-review burden.

## Gates

Blocking gates:

1. exactly one skill file exists;
2. frontmatter name and description exist;
3. no unresolved placeholder markers remain;
4. all referenced target resources exist;
5. required scenario categories are present;
6. deterministic validator passes;
7. reusable asset templates are integrated through a runner, declared workflow, copy/fill instruction, or validation gate when present;
8. no blocked paths or generated evidence were modified as target content;
9. package archive is produced when packaging is requested.

Warning gates:

1. activation metrics are planned but not measured;
2. auxiliary metric is used because the primary metric is saturated;
3. behavior depends on an external evaluator not available in the runtime;
4. self-improvement was performed without a separate persistent installation destination.

Informational gates:

1. additional research was not needed;
2. package applies to the current runtime copy only unless installed elsewhere;
3. scenario suite should be expanded after user feedback or incident evidence.

## Evidence record

A complete harness run records:

- baseline inventory, audit, static score, and evaluator hashes;
- source summary separated into supplied context, target contents, and researched sources;
- harness map and improvement hypotheses;
- changed files grouped by control plane, references, scripts, templates/assets, scenarios, validation, and packaging;
- commands executed and pass/fail outputs;
- before/after comparison;
- package path and exclusions;
- residual risks and next hypotheses.
