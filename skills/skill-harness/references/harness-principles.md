# Harness Principles

Use this reference when translating the generic harness model into a concrete skill-improvement harness.

## Definition

A harness is a controlled structure for executing, evaluating, comparing, and improving a system. For a target skill, the harness surrounds the skill with inputs, scenarios, evaluators, metrics, gates, and evidence records.

The harness is not just a test runner. It is the decision system that lets the user say whether a target skill is ready, improved, regressed, unsafe, or under-specified.

## Good Harness Criteria

A good harness has:

1. Repeatability: same target, same inputs, same config, comparable result.
2. Clear scenarios: each case tests a named behavior.
3. Objective success criteria: pass/fail conditions are explicit.
4. Relevant coverage: happy path, edge cases, ambiguity, non-activation, regressions, adversarial prompts.
5. Controlled isolation: real and simulated dependencies are declared.
6. Observability: failures explain what happened and where.
7. Useful metrics: metrics inform a decision, not vanity reporting.
8. Baseline comparison: current state is measured before changes.
9. Automation: commands are easy to run locally or in CI when possible.
10. Actionability: reports recommend accept, reject, fix, or investigate.

## Harness Components for Skills

For target skills, map the harness into these package areas:

- `SKILL.md`: activation boundaries, mode selection, required inputs, workflow, stop conditions, output contract.
- `references/`: detailed rules, rubrics, scenario schemas, domain context, source policy.
- `scripts/`: deterministic checks, validators, inventory, converters, report generators.
- `assets/templates/`: stable artifact shapes such as reports, plans, scenario files, and checklists. These are operational assets when the workflow copies, fills, renders, or validates them; script consumption is useful but not required.
- `examples/` or `evals/`: optional examples or scenario suites when the target skill needs measured behavior.
- `agents/`: UI metadata, if supported.

## Resource Integration Principle

A weakly integrated supporting resource is not automatically unused. First classify it:

1. operational template or output skeleton;
2. script input, script output, or validator fixture;
3. explanatory reference;
4. example or scenario evidence;
5. unused scaffold, duplicate, or obsolete artifact.

For categories 1-4, prefer adding a workflow reference, loading condition, copy/fill instruction, or validation gate before moving or deleting the file. Remove a resource only when it is a placeholder, duplicate, obsolete, misleading, or has no declared workflow use.

## Decision Statement Pattern

Write the decision statement before the plan:

```text
After this harness runs, we need to decide whether <target skill/version> can <advance to next stage> for <users/use case> with acceptable risk.
```

Examples:

```text
After this harness runs, we need to decide whether the updated skill can be packaged as skill.zip.
```

```text
After this harness runs, we need to decide whether the target skill is mature enough to use for recurring governance reports.
```

## Minimum Scenario Set

For a mature target skill, propose or implement at least:

- 5 prompts that should activate the skill.
- 5 prompts that should not activate the skill.
- 5 ambiguous prompts that require mode selection or clarification.
- 5 difficult prompts involving edge cases, missing inputs, invalid files, volatile facts, or blocked operations.
- Known regressions from user feedback, incidents, or benchmark failures.

Mark scenarios as `measured` only when they were actually executed or the user provided results. Otherwise mark them as `planned`.

## Evidence Rules

- Treat script output as measured only if the command was actually run.
- Treat scenario metrics as measured only if prompts were executed and results were captured.
- Treat researched references as support, not proof that the target package is correct.
- Preserve unknowns as unknown.
- Never invent package validation, installation state, benchmark scores, or source citations.
