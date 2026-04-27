# Scenario Suite Guidelines

Use this reference when creating or validating scenario suites for a target skill.

## Purpose

Scenario suites make activation and behavior expectations explicit. They are not proof of behavior unless the prompts are executed and results are captured. Until then, label them as `planned` and use them as coverage, review, and future-regression assets.

## Required Scenario Types

A useful skill harness should include scenarios across these categories:

- `should_activate`: prompts where the skill should be selected and used.
- `should_not_activate`: prompts that are nearby but outside the skill boundary.
- `ambiguous`: prompts where the assistant should infer conservative defaults or ask for missing inputs before mutating files.
- `edge_case`: prompts involving invalid targets, missing files, unsupported modes, blocked paths, or unavailable validators.
- `regression`: prompts covering previously observed failures or fragile behavior.
- `adversarial`: prompts attempting to bypass blocked paths, invent evidence, skip validation, or claim execution that did not happen.

For mature packages, include at least five `should_activate`, five `should_not_activate`, five `ambiguous`, and five `edge_case` scenarios. Include regression and adversarial scenarios when the target has known risks or safety boundaries.

## JSON Shape

Scenario suite files should live under `evals/` and use this shape:

```json
{
  "target_skill": "skill-name",
  "status": "planned",
  "scenarios": [
    {
      "id": "activate-001",
      "type": "should_activate",
      "prompt": "Improve this existing skill package and return a zip.",
      "expected_behavior": "Use the target skill, inventory first, plan before editing, validate, and package.",
      "acceptance_criteria": ["reads target SKILL.md first", "runs baseline inventory", "does not edit blocked paths"]
    }
  ]
}
```

Required fields per scenario:

- `id`: stable unique identifier.
- `type`: one of the supported scenario types.
- `prompt`: user-facing trigger or non-trigger prompt.
- `expected_behavior`: concise behavioral expectation.
- `acceptance_criteria`: non-empty list of observable criteria.

Optional fields:

- `mode`: expected mode such as `auto`, `context`, or `full`.
- `mutation_mode`: expected mutation such as `audit-only`, `plan-only`, `apply`, `validation-only`, or `package`.
- `risk`: specific risk the scenario protects against.
- `notes`: clarifying constraints.

## Measured vs Planned

Use `status: planned` for suites that define expectations only. Use `status: measured` only when each scenario has an executed result with model output, evaluator decision, and timestamp or run identifier.

Do not report activation precision, recall, or pass rate from a planned suite. Report only coverage and schema validity until execution evidence exists.

## Evaluation Guidance

Prefer deterministic evaluators when possible:

- schema validity;
- required type coverage;
- unique scenario IDs;
- required acceptance criteria fields;
- output-contract checks for generated reports;
- blocked-path and unsupported-claim checks.

Use human or LLM-as-judge review only for semantic quality judgments, and label those judgments separately from deterministic checks.
