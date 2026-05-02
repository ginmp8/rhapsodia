# Harness Principles

Use to turn the generic harness model into a concrete skill-improvement harness.

## Definition and Criteria

A harness is the decision system around a target skill: inputs, scenarios, evaluators, metrics, gates, evidence records, and runner commands. It decides whether the skill is ready, improved, regressed, unsafe, or under-specified.

A good harness is repeatable; uses named scenarios and explicit pass/fail criteria; covers happy path, edge, ambiguity, non-activation, regressions, adversarial prompts; declares dependencies; makes failures observable; uses decision-relevant metrics; records baseline first; automates local/CI checks where practical; and recommends accept, reject, fix, or investigate.

## Skill Components

- `SKILL.md`: activation, modes, inputs, workflow, stops, output contract.
- `references/`: rules, rubrics, schemas, domain context, source policy.
- `scripts/`: deterministic checks, validators, inventory, converters, report generators.
- `assets/templates/`: recurring plan/report/scenario/checklist shapes; operational when copied, filled, rendered, validated, or declared in workflow.
- `examples/` or `evals/`: examples or scenario suites.
- `agents/`: UI metadata when supported.

## Resource Integration

Weak integration is not proof of disuse. Classify a resource as operational template/output skeleton, script input/output or validator fixture, explanatory reference, example/scenario evidence, or unused scaffold/duplicate/obsolete artifact. For the first four, prefer workflow reference, loading condition, copy/fill instruction, or validation gate before moving/deleting. Remove only placeholders, duplicates, obsolete/misleading files, or resources with no declared workflow use.

## Decision and Scenarios

Decision pattern:

```text
After this harness runs, we need to decide whether <target skill/version> can <advance to next stage> for <users/use case> with acceptable risk.
```

Mature scenario set: at least 5 `should_activate`, 5 `should_not_activate`, 5 `ambiguous`, 5 `edge_case`, plus known regressions from feedback/incidents/benchmarks. Mark `measured` only when executed or supplied with results; otherwise `planned`.

## Evidence Rules

Script output is measured only if run; scenario metrics only if prompts executed and results captured; researched references support claims but do not prove correctness; unknowns stay unknown; never invent package validation, installation state, benchmark scores, or citations.
